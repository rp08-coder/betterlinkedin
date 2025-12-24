"""
Setup user preferences for filter-based matching

Configure:
1. Industry preferences (sectors)
2. Job type preferences
3. Experience background
"""

import asyncio
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.user import User


async def setup_preferences():
    """
    Update user profile with clear preferences
    """
    print("\n=== Setting Up User Preferences ===\n")

    async for db in get_db():
        # Get the user
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found!")
            return

        print(f"✓ Found user: {user.email}\n")

        # Set industry/sector preferences
        user.sectors = [
            "FinTech",
            "Finance",
            "Banking",
            "Payments",
            "Crypto",
            "Enterprise Software",
            "SaaS"
        ]

        # Set job type preferences
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

        # Set experience background
        user.experience_background = [
            "Investment Banking",
            "Consulting",
            "Finance"
        ]

        # Set skills
        user.skills = [
            "Financial Modeling",
            "Strategic Partnerships",
            "Business Strategy",
            "Corporate Development",
            "M&A",
            "Go-to-Market Strategy",
            "Revenue Operations"
        ]

        await db.commit()

        print("✅ Preferences updated!\n")
        print("Industry Preferences (Sectors):")
        for sector in user.sectors:
            print(f"  • {sector}")

        print("\nJob Type Preferences:")
        for job_type in user.job_types:
            print(f"  • {job_type}")

        print("\nExperience Background:")
        for exp in user.experience_background:
            print(f"  • {exp}")

        print()

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_preferences())
