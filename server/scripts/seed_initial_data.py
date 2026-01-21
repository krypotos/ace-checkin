#!/usr/bin/env python3
"""
Script to seed initial data into the database.

This is useful for development and testing.
Run from project root with: python3 scripts/seed_initial_data.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal  # noqa: E402
from app.models import EntryLog, Member, PaymentLog  # noqa: E402


def seed_members():
    """Create sample members"""
    db = SessionLocal()

    members_data = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-1001",
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "+1-555-1002",
        },
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "phone": "+1-555-1003",
        },
        {
            "name": "Diana Prince",
            "email": "diana@example.com",
            "phone": "+1-555-1004",
        },
        {
            "name": "Edward Norton",
            "email": "edward@example.com",
            "phone": "+1-555-1005",
        },
    ]

    created_ids = []
    for member_data in members_data:
        # Check if member already exists by name
        existing = db.query(Member).filter(Member.name == member_data["name"]).first()

        if not existing:
            member = Member(**member_data)
            db.add(member)
            db.flush()  # Get the auto-generated ID
            created_ids.append(member.id)
            print(f"✓ Created member: {member_data['name']} (ID: {member.id})")
        else:
            created_ids.append(existing.id)
            print(f"⊘ Member already exists: {member_data['name']} (ID: {existing.id})")

    db.commit()
    db.close()
    return created_ids


def seed_entry_logs(member_ids: list[int]):
    """Create sample entry logs"""
    db = SessionLocal()

    base_date = datetime.utcnow()

    entry_count = 0
    for i in range(50):  # 50 sample entries
        member_id = member_ids[i % len(member_ids)]
        timestamp = base_date - timedelta(days=i // 5, hours=i % 24)
        courts = ["Court A", "Court B", "Court C", "Court D"]

        entry = EntryLog(
            member_id=member_id, timestamp=timestamp, notes=f"Entry at {courts[i % len(courts)]}"
        )
        db.add(entry)
        entry_count += 1

    db.commit()
    print(f"✓ Created {entry_count} entry logs")
    db.close()


def seed_payment_logs(member_ids: list[int]):
    """Create sample payment logs"""
    db = SessionLocal()

    base_date = datetime.utcnow()

    payment_count = 0
    for i in range(25):  # 25 sample payments
        member_id = member_ids[i % len(member_ids)]
        timestamp = base_date - timedelta(days=i * 7)  # Weekly payments
        amount = int(25.50 * 100) if i % 2 == 0 else int(50.00 * 100)  # in cents

        payment = PaymentLog(
            member_id=member_id,
            amount=amount,
            timestamp=timestamp,
            notes="Court rental fee" if i % 3 == 0 else "Monthly membership",
        )
        db.add(payment)
        payment_count += 1

    db.commit()
    print(f"✓ Created {payment_count} payment logs")
    db.close()


def main():
    """Main seed function"""
    print("=" * 50)
    print("Seeding Initial Data")
    print("=" * 50)

    try:
        member_ids = seed_members()
        seed_entry_logs(member_ids)
        seed_payment_logs(member_ids)

        print("=" * 50)
        print("✓ Seeding completed successfully!")
        print("=" * 50)
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
