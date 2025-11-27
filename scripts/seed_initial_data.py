#!/usr/bin/env python3
"""
Script to seed initial data into the database.

This is useful for development and testing.
Run from project root with: python3 scripts/seed_initial_data.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import Member, EntryLog, PaymentLog


def seed_members():
    """Create sample members"""
    db = SessionLocal()
    
    members_data = [
        {
            "member_id": "M001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-1001"
        },
        {
            "member_id": "M002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "+1-555-1002"
        },
        {
            "member_id": "M003",
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "phone": "+1-555-1003"
        },
        {
            "member_id": "M004",
            "name": "Diana Prince",
            "email": "diana@example.com",
            "phone": "+1-555-1004"
        },
        {
            "member_id": "M005",
            "name": "Edward Norton",
            "email": "edward@example.com",
            "phone": "+1-555-1005"
        },
    ]
    
    for member_data in members_data:
        # Check if member already exists
        existing = db.query(Member).filter(
            Member.member_id == member_data["member_id"]
        ).first()
        
        if not existing:
            member = Member(**member_data)
            db.add(member)
            print(f"✓ Created member: {member_data['name']} ({member_data['member_id']})")
        else:
            print(f"⊘ Member already exists: {member_data['name']} ({member_data['member_id']})")
    
    db.commit()
    db.close()


def seed_entry_logs():
    """Create sample entry logs"""
    db = SessionLocal()
    
    member_ids = ["M001", "M002", "M003", "M004", "M005"]
    base_date = datetime.utcnow()
    
    entry_count = 0
    for i in range(50):  # 50 sample entries
        member_id = member_ids[i % len(member_ids)]
        timestamp = base_date - timedelta(days=i // 5, hours=i % 24)
        courts = ["Court A", "Court B", "Court C", "Court D"]
        
        entry = EntryLog(
            member_id=member_id,
            timestamp=timestamp,
            notes=f"Entry at {courts[i % len(courts)]}"
        )
        db.add(entry)
        entry_count += 1
    
    db.commit()
    print(f"✓ Created {entry_count} entry logs")
    db.close()


def seed_payment_logs():
    """Create sample payment logs"""
    db = SessionLocal()
    
    member_ids = ["M001", "M002", "M003", "M004", "M005"]
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
            notes="Court rental fee" if i % 3 == 0 else "Monthly membership"
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
        seed_members()
        seed_entry_logs()
        seed_payment_logs()
        
        print("=" * 50)
        print("✓ Seeding completed successfully!")
        print("=" * 50)
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

