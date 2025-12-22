"""
Smart job queue population with intelligent matching

Scores jobs based on user profile and only adds relevant matches
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db, engine
from app.models.job import Job, JobQueue
from app.models.user import User


def calculate_job_score(job: Job, user: User) -> float:
    """
    Calculate relevance score for a job based on user profile

    Returns score from 0.0 to 1.0
    """
    score = 0.0
    max_score = 0.0

    # Job category matching (40% weight)
    max_score += 40
    job_category_lower = job.job_category.lower() if job.job_category else ""
    user_job_types_lower = [jt.lower() for jt in user.job_types] if user.job_types else []

    # Direct category matches
    category_keywords = {
        "finance": ["finance", "fp&a", "financial"],
        "corporate development": ["corporate development", "corp dev", "m&a"],
        "business operations": ["business operations", "bizops", "biz ops"],
        "strategy": ["strategy", "strategic"],
        "partnerships": ["partnerships", "partnership", "business development", "bd"],
        "revenue operations": ["revenue operations", "revops", "rev ops", "sales operations", "sales ops"],
        "gtm strategy": ["gtm", "go-to-market", "growth"],
    }

    for user_type in user_job_types_lower:
        for keyword_category, keywords in category_keywords.items():
            if any(kw in user_type for kw in keywords):
                if any(kw in job_category_lower or kw in (job.job_title.lower() if job.job_title else "") for kw in keywords):
                    score += 40
                    break
        if score >= 40:
            break

    # Sector matching (30% weight)
    max_score += 30
    if user.sectors:
        user_sectors_lower = [s.lower() for s in user.sectors]
        job_sector_lower = job.sector.lower() if job.sector else ""

        for user_sector in user_sectors_lower:
            if user_sector in job_sector_lower:
                score += 30
                break
            # Partial matches
            elif any(word in job_sector_lower for word in user_sector.split()):
                score += 15
                break

    # Skills matching (20% weight)
    max_score += 20
    if user.skills and job.requirements:
        user_skills_lower = [s.lower() for s in user.skills]
        requirements_lower = job.requirements.lower()

        skill_matches = sum(1 for skill in user_skills_lower if skill in requirements_lower)
        if skill_matches > 0:
            score += min(20, skill_matches * 4)  # 4 points per skill, max 20

    # Title/description relevance (10% weight)
    max_score += 10
    if job.job_title and job.description:
        title_desc_lower = f"{job.job_title} {job.description}".lower()

        finance_keywords = [
            "finance", "financial", "fp&a", "corporate development", "m&a",
            "business operations", "bizops", "strategy", "partnerships",
            "revenue operations", "revops", "gtm", "go-to-market",
            "business development", "corp dev"
        ]

        keyword_matches = sum(1 for kw in finance_keywords if kw in title_desc_lower)
        if keyword_matches > 0:
            score += min(10, keyword_matches * 2)

    # Normalize score to 0-1 range
    final_score = score / max_score if max_score > 0 else 0.0

    return final_score


async def smart_populate_queue():
    """
    Intelligently populate user queue with relevant jobs only

    Only adds jobs with score >= 0.6 (60% match)
    """
    print("\n=== Smart Job Queue Population ===\n")

    async for db in get_db():
        # Get the user
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found! Please register an account first.")
            return

        print(f"✓ Found user: {user.email}")
        print(f"  Profile: {', '.join(user.job_types[:3]) if user.job_types else 'Not set'}")
        print(f"  Sectors: {', '.join(user.sectors[:3]) if user.sectors else 'Not set'}\n")

        # Get all active jobs
        result = await db.execute(
            select(Job).where(Job.is_active == True)
        )
        jobs = result.scalars().all()

        print(f"Analyzing {len(jobs)} jobs...\n")

        added_count = 0
        skipped_low_score = 0
        skipped_exists = 0

        job_scores = []

        for job in jobs:
            # Calculate relevance score
            score = calculate_job_score(job, user)
            job_scores.append((job, score))

        # Sort by score (highest first)
        job_scores.sort(key=lambda x: x[1], reverse=True)

        # Only add jobs with score >= 0.6
        THRESHOLD = 0.6

        for job, score in job_scores:
            if score < THRESHOLD:
                print(f"⊘ Low match ({score:.0%}): {job.job_title} at {job.company_name}")
                skipped_low_score += 1
                continue

            # Check if job is already in user's queue
            existing = await db.execute(
                select(JobQueue).where(
                    JobQueue.user_id == user.user_id,
                    JobQueue.job_id == job.job_id
                )
            )

            if existing.scalar_one_or_none():
                print(f"⊘ Already in queue: {job.job_title} at {job.company_name}")
                skipped_exists += 1
                continue

            # Add to queue with calculated score
            queue_item = JobQueue(
                user_id=user.user_id,
                job_id=job.job_id,
                relevance_score=score,
                shown=False
            )

            db.add(queue_item)
            print(f"✓ Added ({score:.0%} match): {job.job_title} at {job.company_name} [{job.job_category}]")
            added_count += 1

        await db.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  High-quality matches added: {added_count}")
        print(f"  Already in queue: {skipped_exists}")
        print(f"  Low relevance (< {THRESHOLD:.0%}): {skipped_low_score}")
        print(f"  Total analyzed: {len(jobs)}")
        print(f"{'='*60}\n")

        if added_count > 0:
            print(f"✅ {added_count} relevant jobs added to your queue!")
        else:
            print("⚠️ No new relevant jobs found. Try updating your profile or adding more jobs to the database.")

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(smart_populate_queue())
