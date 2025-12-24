"""
Script to create a new user account
"""

import asyncio
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user():
    """
    Create a new user account with finance/GTM background
    """
    print("\n=== Creating User Account ===\n")

    async for db in get_db():
        # Check if user already exists
        result = await db.execute(select(User))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✓ User already exists: {existing_user.email}\n")
            print("Updating profile instead...\n")
            user = existing_user
        else:
            # Create new user
            hashed_password = pwd_context.hash("password123")
            user = User(
                email="user@founded.com",
                password_hash=hashed_password,
                first_name="Alex",
                last_name="Johnson",
                city="San Francisco",
                years_experience=3,
                daily_application_limit=10
            )
            db.add(user)
            await db.flush()
            print(f"✓ Created new user: {user.email}\n")

        # Set profile preferences
        user.sectors = [
            "FinTech",
            "Finance",
            "Banking",
            "Payments",
            "Crypto",
            "Enterprise Software",
            "SaaS",
            "Marketplace"
        ]

        user.job_types = [
            "Business Operations",
            "Finance",
            "Corporate Development",
            "Strategy",
            "Partnerships",
            "Revenue Operations",
            "Sales Operations",
            "GTM Strategy",
            "Business Development"
        ]

        user.skills = [
            "Financial Modeling",
            "Strategic Partnerships",
            "Business Strategy",
            "Corporate Development",
            "M&A",
            "Go-to-Market Strategy",
            "Revenue Operations",
            "Deal Structuring",
            "Financial Analysis",
            "Partnership Management",
            "Sales Strategy",
            "Business Planning"
        ]

        await db.commit()

        print("✅ Profile configured with finance/GTM preferences!\n")
        print(f"Email: {user.email}")
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"Experience: {user.years_experience} years")
        print(f"\nSectors: {', '.join(user.sectors[:3])}...")
        print(f"Job Types: {', '.join(user.job_types[:3])}...")
        print(f"Skills: {', '.join(user.skills[:3])}...\n")

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_user())
