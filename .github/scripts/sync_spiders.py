"""
Sync spider slugs from changed spider files to Airtable.

For each spider file passed in, extract all (name, agency) pairs and
create/update Airtable records.

The extraction of spiders currently only works for the following
two patterns:
    1. Singular scraper — a class whose body has `name = "..."` and
         `agency = "..."` as direct class attributes. Only top-level class
         assignments count; anything inside a method is ignored.
    2. Spider factory — a module-level `spider_configs = [{...}, ...]`
         list of dicts, each with its own "name" and "agency" keys.
"""

import ast
import sys
from pathlib import Path

from decouple import UndefinedValueError, config
from pyairtable import Api

"""
AirTable field names for the slug and agency name.
These should match the field names in the AirTable base.
"""
SLUG_FIELD = "Slug"
AGENCY_FIELD = "Agency name"


def extract_spiders(source: str) -> list[dict]:
    tree = ast.parse(source)
    spiders: list[dict] = []

    """
    Helper function that finds `key = "..."` in a list of statements
    and return the string. Only looks at direct Assign nodes in the
    given body - doesn't recurse into nested functions or classes.
    """

    def get_str_assign(body, key):
        for stmt in body:
            if (
                isinstance(stmt, ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and stmt.targets[0].id == key
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                return stmt.value.value
        return None

    for node in ast.iter_child_nodes(tree):
        # Case 1: regular scraper
        if isinstance(node, ast.ClassDef):
            name = get_str_assign(node.body, "name")
            agency = get_str_assign(node.body, "agency")
            if name:
                spiders.append({"name": name, "agency": agency})

        # Case 2: spider factory
        elif (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "spider_configs"
                for t in node.targets
            )
            and isinstance(node.value, (ast.List, ast.Tuple))
        ):
            for element in node.value.elts:
                if not isinstance(element, ast.Dict):
                    continue
                entry = {"name": None, "agency": None}
                for k, v in zip(element.keys, element.values):
                    if not (
                        isinstance(k, ast.Constant) and isinstance(v, ast.Constant)
                    ):
                        continue
                    if k.value in ("name", "agency") and isinstance(v.value, str):
                        entry[k.value] = v.value
                if entry["name"]:
                    spiders.append(entry)

    return spiders


def sync_to_airtable(spiders: list[dict], table) -> dict:
    """
    Sync spiders to Airtable, keyed on agency name.
    Agency name is considered the source of truth for
    matching records.

    Workflow for each spider:
      - If the agency is already in the table and the slug matches: skip.
      - If the agency is in the table but the slug differs: update the slug.
      - If the agency is not in the table: create a new record.

    Note:
    If the agency name for the same slug changes, a new record
    will be created and the table will end up with multiple
    records for the same slug but different agency names.
    There would have to be some manual cleanup to remove the
    old record with the outdated slug, but this is a safer
    approach than accidentally overwriting an existing record
    with a new slug that belongs to a different agency.
    """
    existing: dict[str, tuple[str, str]] = {}
    for row in table.all(fields=[SLUG_FIELD, AGENCY_FIELD]):
        agency = row["fields"].get(AGENCY_FIELD)
        if agency:
            existing[agency] = (row["id"], row["fields"].get(SLUG_FIELD, ""))

    to_create = []
    to_update = []
    skipped = []

    for spider in spiders:
        slug = spider["name"]
        agency = spider.get("agency")
        if not agency:
            # Can't key on agency if it's missing — log and move on.
            print(f"[INFO] skipping spider '{slug}' — no agency name found")
            continue

        if agency in existing:
            record_id, current_slug = existing[agency]
            if current_slug == slug:
                skipped.append(agency)
            else:
                to_update.append({"id": record_id, "fields": {SLUG_FIELD: slug}})
        else:
            to_create.append(
                {
                    SLUG_FIELD: slug,
                    AGENCY_FIELD: agency,
                }
            )
            # Track in-memory so duplicates within this same run don't double-create.
            existing[agency] = ("", slug)

    created = []
    if to_create:
        created_records = table.batch_create(to_create)
        created = [row["fields"].get(AGENCY_FIELD) for row in created_records]

    updated = []
    if to_update:
        table.batch_update(to_update)
        updated = [row["fields"][SLUG_FIELD] for row in to_update]

    return {"created": created, "updated": updated, "skipped": skipped}


def main():
    try:
        pat = config("AIRTABLE_PAT")
        base_id = config("AIRTABLE_BASE_ID")
        table_name = config("AIRTABLE_TABLE_ID")
    except UndefinedValueError as e:
        sys.exit(f"[ERROR] Missing env var: {e}")

    files = [
        Path(p) for p in sys.argv[1:] if Path(p).suffix == ".py" and Path(p).exists()
    ]
    if not files:
        print("[INFO] No spider files to process.")
        return

    # Collect spiders across all changed files. Dedupe by slug in case the
    # same spider name somehow shows up in multiple changed files.
    all_spiders: dict[str, dict] = {}
    for path in files:
        try:
            spiders = extract_spiders(path.read_text(encoding="utf-8"))
        except SyntaxError as e:
            print(f"[ERROR] skipping {path} — syntax error: {e}")
            continue
        print(f"[INFO] {path}: found {len(spiders)} spider(s)")
        for s in spiders:
            all_spiders.setdefault(s["name"], s)

    if not all_spiders:
        print("[INFO] No spiders extracted.")
        return

    table = Api(pat).table(base_id, table_name)
    result = sync_to_airtable(list(all_spiders.values()), table)

    print(f"[INFO] Created {len(result['created'])}: {result['created']}")
    print(f"[INFO] Updated {len(result['updated'])}: {result['updated']}")
    print(
        f"[INFO] Skipped {len(result['skipped'])} (already up to date): {result['skipped']}"  # noqa
    )


if __name__ == "__main__":
    main()
