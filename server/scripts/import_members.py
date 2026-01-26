#!/usr/bin/env python3
"""
Script to mass import members from a CSV file into the database.

Usage:
    python scripts/import_members.py data_migrations/members.csv
    python scripts/import_members.py data_migrations/members.csv --dry-run
    python scripts/import_members.py data_migrations/members.csv --skip-duplicates

For production, set the DATABASE_URL environment variable:
    DATABASE_URL="postgresql://user:pass@host:5432/db" python scripts/import_members.py members.csv

CSV Format:
    The script supports two formats:
    1. Columns: first, last (will be combined as "FIRST LAST")
    2. Column: name (used directly)

Run from project root: python3 scripts/import_members.py <csv_file>
"""

import argparse
import csv
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal  # noqa: E402
from app.models import Member  # noqa: E402


def parse_csv(csv_path: Path) -> list[dict]:
    """
    Parse CSV file and return list of member data.

    Supports two formats:
    - first, last columns -> combined into name
    - name column -> used directly
    """
    members = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Normalize keys to lowercase
            row = {k.lower().strip(): v.strip() for k, v in row.items()}

            if "first" in row and "last" in row:
                # Combine first and last name
                first = row.get("first", "").strip()
                last = row.get("last", "").strip()
                name = f"{first} {last}".strip()
            elif "name" in row:
                name = row.get("name", "").strip()
            else:
                print(f"⚠ Warning: Could not determine name from row: {row}")
                continue

            if not name:
                print(f"⚠ Warning: Empty name in row: {row}")
                continue

            member_data = {
                "name": name,
                "email": row.get("email", "").strip() or None,
                "phone": row.get("phone", "").strip() or None,
            }
            members.append(member_data)

    return members


def get_existing_members(db) -> set[str]:
    """Get set of existing member names (normalized to uppercase for comparison)."""
    existing = db.query(Member.name).all()
    return {name.upper() for (name,) in existing}


def import_members(
    csv_path: Path,
    dry_run: bool = False,
    skip_duplicates: bool = True,
    csv_only: bool = False,
) -> dict:
    """
    Import members from CSV file.

    Args:
        csv_path: Path to CSV file
        dry_run: If True, don't actually import, just show what would happen
        skip_duplicates: If True, skip members that already exist (by name)
        csv_only: If True, only validate/preview CSV without database connection

    Returns:
        Dictionary with import statistics
    """
    stats = {
        "total_in_csv": 0,
        "created": 0,
        "skipped_duplicate": 0,
        "skipped_empty": 0,
        "errors": 0,
    }

    # Parse CSV
    members_data = parse_csv(csv_path)
    stats["total_in_csv"] = len(members_data)

    if not members_data:
        print("⚠ No valid members found in CSV file")
        return stats

    # CSV-only mode: just show what's in the CSV without database
    if csv_only:
        seen_names = set()
        for member_data in members_data:
            name = member_data["name"]
            if name.upper() in seen_names:
                stats["skipped_duplicate"] += 1
                print(f"⊘ Duplicate in CSV: {name}")
            else:
                stats["created"] += 1
                print(f"◎ Would create: {name}")
                seen_names.add(name.upper())
        return stats

    db = SessionLocal()

    try:
        # Get existing members for duplicate detection
        existing_names = get_existing_members(db) if skip_duplicates else set()

        created_members = []

        for member_data in members_data:
            name = member_data["name"]

            # Check for duplicate
            if skip_duplicates and name.upper() in existing_names:
                stats["skipped_duplicate"] += 1
                print(f"⊘ Skipped (already exists): {name}")
                continue

            if dry_run:
                stats["created"] += 1
                print(f"◎ Would create: {name}")
                # Add to existing to catch duplicates within the CSV
                existing_names.add(name.upper())
            else:
                try:
                    member = Member(**member_data)
                    db.add(member)
                    db.flush()  # Get the auto-generated ID
                    created_members.append(member)
                    stats["created"] += 1
                    print(f"✓ Created: {name} (ID: {member.id})")
                    # Add to existing to catch duplicates within the CSV
                    existing_names.add(name.upper())
                except Exception as e:
                    stats["errors"] += 1
                    print(f"✗ Error creating {name}: {e}")
                    db.rollback()

        if not dry_run and created_members:
            db.commit()
            print(f"\n✓ Committed {len(created_members)} new members to database")

    finally:
        db.close()

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Import members from a CSV file into the database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview CSV contents without database connection
    python scripts/import_members.py data_migrations/members.csv --csv-only

    # Dry run to preview against database (checks for duplicates)
    python scripts/import_members.py data_migrations/members.csv --dry-run

    # Import members (skip duplicates by default)
    python scripts/import_members.py data_migrations/members.csv

    # Import to production (set DATABASE_URL first)
    DATABASE_URL="postgresql://..." python scripts/import_members.py members.csv
        """,
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to the CSV file containing member data",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be imported without making changes",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Allow importing members with names that already exist in the database",
    )
    parser.add_argument(
        "--csv-only",
        action="store_true",
        help="Only validate/preview the CSV file without connecting to database",
    )

    args = parser.parse_args()

    # Validate CSV file exists
    if not args.csv_file.exists():
        print(f"✗ Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    # Show configuration
    print("=" * 60)
    print("Member Import Script")
    print("=" * 60)
    print(f"CSV File: {args.csv_file}")

    if args.csv_only:
        print("Mode: CSV PREVIEW ONLY (no database connection)")
    elif args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    else:
        print("Mode: LIVE IMPORT")

    print(f"Skip Duplicates: {not args.allow_duplicates}")

    # Show database info (mask password) - only if not csv-only mode
    if not args.csv_only:
        from app.config import settings

        db_url = settings.database_url
        if "@" in db_url:
            # Mask password in URL for display
            parts = db_url.split("@")
            prefix = parts[0].rsplit(":", 1)[0]  # Remove password
            masked_url = f"{prefix}:****@{parts[1]}"
        else:
            masked_url = db_url
        print(f"Database: {masked_url}")

    print("=" * 60)

    if not args.dry_run and not args.csv_only:
        # Confirmation prompt for live import
        response = input("\nProceed with import? [y/N]: ").strip().lower()
        if response != "y":
            print("Import cancelled.")
            sys.exit(0)

    print()

    # Run import
    stats = import_members(
        csv_path=args.csv_file,
        dry_run=args.dry_run,
        skip_duplicates=not args.allow_duplicates,
        csv_only=args.csv_only,
    )

    # Print summary
    print()
    print("=" * 60)
    print("Import Summary")
    print("=" * 60)
    print(f"Total rows in CSV:     {stats['total_in_csv']}")
    print(f"Created:               {stats['created']}")
    print(f"Skipped (duplicates):  {stats['skipped_duplicate']}")
    print(f"Errors:                {stats['errors']}")
    print("=" * 60)

    if args.csv_only:
        print("\n⚠ This was a CSV PREVIEW. No database connection was made.")
        print("Run without --csv-only to check against database or perform import.")
    elif args.dry_run:
        print("\n⚠ This was a DRY RUN. No changes were made to the database.")
        print("Run without --dry-run to perform the actual import.")
    elif stats["created"] > 0:
        print("\n✓ Import completed successfully!")
    else:
        print("\n⚠ No new members were imported.")

    # Exit with error if there were errors
    if stats["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
