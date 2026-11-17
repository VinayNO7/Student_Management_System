#!/usr/bin/env python
"""
Student Management System Database Seeder
Populates initial sample departments, courses, students, enrollments, and attendance.
Usage:
    python database/seed_data.py
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, init_db, seed_initial_data
from app.config import db_info

def main():
    print("=" * 60)
    print(f"🌱 Seeding database: {db_info['database']} ({db_info['engine'].upper()})")
    print("=" * 60)
    
    init_db()
    db = SessionLocal()
    try:
        seed_initial_data(db)
        print("✅ Sample data populated successfully!")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

