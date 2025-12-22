"""
Script to update user profile with career preferences

This sets up your profile to match jobs to your background
"""

import asyncio
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.user import User


async def update_user_profile():
    """
    Update user profile with finance/GTM background preferences
    """
    print("\n=== Updating User Profile ===\n")

    async for db in get_db():
        # Get the user
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found!")
            return

        print(f"✓ Found user: {user.email}\n")

        # Update profile with finance/GTM preferences
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

        user.years_experience = 3  # Adjust based on your actual experience

        await db.commit()

        print("✅ Profile updated with finance/GTM preferences!\n")
        print("Sectors:", user.sectors)
        print("\nJob Types:", user.job_types)
        print("\nSkills:", user.skills[:5], "...")

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_user_profile())
