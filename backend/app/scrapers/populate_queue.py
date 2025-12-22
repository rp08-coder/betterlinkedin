"""
Script to populate user job queue with all available jobs

This adds all jobs from the jobs table to a user's personal queue
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db, engine
from app.models.job import Job, JobQueue
from app.models.user import User


async def populate_queue():
    """Add all jobs to the user's queue"""

    print("\n=== Populating User Job Queue ===\n")

    async for db in get_db():
        # Get the user (assuming there's only one user - update this if needed)
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found! Please register an account first.")
            return

        print(f"✓ Found user: {user.email}")
        print(f"  User ID: {user.user_id}\n")

        # Get all active jobs
        result = await db.execute(
            select(Job).where(Job.is_active == True)
        )
        jobs = result.scalars().all()

        print(f"Found {len(jobs)} jobs in database\n")

        added_count = 0
        skipped_count = 0

        for job in jobs:
            # Check if job is already in user's queue
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

            # Add to queue with a default relevance score
            queue_item = JobQueue(
                user_id=user.user_id,
                job_id=job.job_id,
                relevance_score=0.75,  # Default score
                shown=False
            )

            db.add(queue_item)
            print(f"✓ Added to queue: {job.job_title} at {job.company_name}")
            added_count += 1

        await db.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Added to queue: {added_count}")
        print(f"  Already in queue: {skipped_count}")
        print(f"  Total jobs: {len(jobs)}")
        print(f"{'='*60}\n")

        print("✅ Jobs are now in your queue and should appear in the app!")
        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(populate_queue())
