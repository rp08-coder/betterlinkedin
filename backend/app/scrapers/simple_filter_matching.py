"""
Simple filter-based job matching

Matches jobs to users based on:
1. Industry/Sector match (job.sector vs user.sectors)
2. Job type match (job.job_category vs user.job_types)

Scoring:
- Both match → 90%
- One matches → 70%
- Neither matches → filtered out (not shown)
"""

import asyncio
from sqlalchemy import select
from typing import List, Tuple

from app.core.database import get_db, engine
from app.models.user import User
from app.models.job import Job, JobQueue


def calculate_match_score(job: Job, user: User) -> int:
    """
    Calculate match score based on simple filters

    Returns:
        int: Match score as percentage (0-100), or 0 if should be filtered
    """
    sector_match = job.sector in user.sectors if user.sectors else False
    job_type_match = job.job_category in user.job_types if user.job_types else False

    # Both match → 90%
    if sector_match and job_type_match:
        return 90

    # One matches → 70%
    if sector_match or job_type_match:
        return 70

    # Neither matches → filter out
    return 0


async def filter_based_matching():
    """
    Simple filter-based job matching

    Matches jobs based on user preferences:
    - Industry/sector preference
    - Job type preference
    """
    print("\n" + "="*60)
    print("🎯 FILTER-BASED JOB MATCHING")
    print("="*60 + "\n")

    async for db in get_db():
        # Get first user
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found! Please register an account first.")
            return

        print(f"👤 User: {user.first_name} {user.last_name}")
        print(f"📋 Industry Preferences: {', '.join(user.sectors) if user.sectors else 'None'}")
        print(f"🎯 Job Type Preferences: {', '.join(user.job_types) if user.job_types else 'None'}")
        print()

        # Get all active jobs
        result = await db.execute(
            select(Job).where(Job.is_active == True)
        )
        jobs = result.scalars().all()

        print(f"📊 Found {len(jobs)} total jobs in database\n")

        if not jobs:
            print("❌ No jobs found in database!")
            return

        # Match jobs
        matches: List[Tuple[Job, int]] = []
        filtered_out = 0

        for job in jobs:
            score = calculate_match_score(job, user)

            if score > 0:
                matches.append((job, score))
                print(f"✓ {score}% match: {job.job_title} at {job.company_name}")
                print(f"  Sector: {job.sector}, Category: {job.job_category}")
            else:
                filtered_out += 1
                print(f"✗ Filtered: {job.job_title} at {job.company_name}")
                print(f"  Sector: {job.sector}, Category: {job.job_category}")

        print(f"\n📊 Matches: {len(matches)}, Filtered: {filtered_out}\n")

        if not matches:
            print("❌ No matching jobs found!")
            print("\nTips:")
            print("- Make sure your sectors list includes the job sectors")
            print("- Make sure your job_types list includes the job categories")
            return

        # Sort by score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)

        # Add to queue
        print("="*60)
        print("Adding to Queue")
        print("="*60 + "\n")

        added_count = 0
        skipped_count = 0

        for job, score in matches:
            # Check if already in queue
            existing = await db.execute(
                select(JobQueue).where(
                    JobQueue.user_id == user.user_id,
                    JobQueue.job_id == job.job_id
                )
            )

            if existing.scalar_one_or_none():
                print(f"⊘ Already in queue: {job.job_title} at {job.company_name}")
                skipped_count += 1
                continue

            # Add to queue
            queue_item = JobQueue(
                user_id=user.user_id,
                job_id=job.job_id,
                relevance_score=score,
                shown=False
            )

            db.add(queue_item)
            print(f"✅ Added ({score}%): {job.job_title} at {job.company_name}")
            added_count += 1

        await db.commit()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✅ Jobs added: {added_count}")
        print(f"⊘ Already in queue: {skipped_count}")
        print(f"✗ Filtered out: {filtered_out}")
        print(f"📊 Total jobs analyzed: {len(jobs)}")
        print("="*60 + "\n")

        if added_count > 0:
            print(f"🎉 {added_count} matching jobs added to your queue!")

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(filter_based_matching())
