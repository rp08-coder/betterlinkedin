"""
AI-powered job queue population

Uses Claude AI to intelligently match jobs to user profile
"""

import asyncio
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.job import Job, JobQueue
from app.models.user import User
from app.services.ai_matching import batch_categorize_jobs, batch_match_user_to_jobs


async def ai_populate_queue():
    """
    Use AI to intelligently populate user queue with perfectly matched jobs

    - Uses Claude to categorize each job
    - Uses Claude to score match between user profile and each job
    - Only adds jobs with 60%+ AI match score
    """
    print("\n" + "="*60)
    print("🤖 AI-POWERED JOB MATCHING")
    print("="*60 + "\n")

    async for db in get_db():
        # Get the user
        result = await db.execute(select(User))
        user = result.scalar_one_or_none()

        if not user:
            print("❌ No user found! Please register an account first.")
            return

        print(f"👤 User: {user.first_name} {user.last_name}")
        print(f"📋 Profile Type: ", end="")

        from app.services.ai_matching import determine_user_profile_type
        profile_type = determine_user_profile_type(user)
        print(profile_type.replace('_', ' ').title())

        if user.job_types:
            print(f"🎯 Preferred Roles: {', '.join(user.job_types[:3])}")
        if user.sectors:
            print(f"🏢 Preferred Sectors: {', '.join(user.sectors[:3])}")

        # Get all active jobs
        result = await db.execute(
            select(Job).where(Job.is_active == True)
        )
        jobs = result.scalars().all()

        if not jobs:
            print("\n❌ No jobs in database. Add jobs first!")
            return

        print(f"\n📊 Found {len(jobs)} total jobs in database")

        # Step 1: Use AI to categorize all jobs
        print("\n" + "-"*60)
        print("STEP 1: AI Job Categorization")
        print("-"*60)

        categorizations = await batch_categorize_jobs(jobs)

        # Step 2: Use AI to match user to jobs
        print("\n" + "-"*60)
        print("STEP 2: AI Profile Matching")
        print("-"*60)

        matches = await batch_match_user_to_jobs(user, jobs, categorizations)

        if not matches:
            print("\n❌ No high-quality matches found!")
            print("\nThis usually means:")
            print("  - Jobs don't match your profile type")
            print("  - Need to add more relevant jobs to database")
            print(f"  - Your profile ({profile_type}) needs jobs in: Finance, Strategy, BizOps, etc.")
            return

        # Step 3: Add matched jobs to queue
        print("\n" + "-"*60)
        print("STEP 3: Adding Matches to Queue")
        print("-"*60 + "\n")

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

            # Add to queue with AI-generated score
            queue_item = JobQueue(
                user_id=user.user_id,
                job_id=job.job_id,
                relevance_score=score,
                shown=False
            )

            db.add(queue_item)
            print(f"✅ Added ({score:.0%}): {job.job_title} at {job.company_name}")
            print(f"   Category: {categorizations[str(job.job_id)]['job_category']}")
            added_count += 1

        await db.commit()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"✅ High-quality matches added: {added_count}")
        print(f"⊘ Already in queue: {skipped_count}")
        print(f"✗ Low-quality matches filtered: {len(jobs) - len(matches)}")
        print(f"📊 Total jobs analyzed: {len(jobs)}")
        print("="*60 + "\n")

        if added_count > 0:
            print(f"🎉 {added_count} perfectly matched jobs added to your queue!\n")
        else:
            print("⚠️  No new matches. Try adding more relevant jobs.\n")

        break

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(ai_populate_queue())
