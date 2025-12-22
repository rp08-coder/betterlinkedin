"""
Script to run job scrapers and save results to database

Usage:
    python app/scrapers/run_scraper.py
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.job import Job
from app.scrapers.yc_scraper import YCombinatorScraper


async def save_jobs_to_db(jobs_data: list, db: AsyncSession):
    """
    Save scraped jobs to the database

    Args:
        jobs_data: List of job dictionaries
        db: Database session
    """
    saved_count = 0
    duplicate_count = 0
    error_count = 0

    for job_data in jobs_data:
        try:
            # Check if job already exists (by source_url)
            result = await db.execute(
                select(Job).where(Job.source_url == job_data["source_url"])
            )
            existing_job = result.scalar_one_or_none()

            if existing_job:
                print(f"Job already exists: {job_data['job_title']} at {job_data['company_name']}")
                duplicate_count += 1
                continue

            # Create new job
            job = Job(**job_data)
            db.add(job)
            await db.commit()

            print(f"✓ Saved: {job_data['job_title']} at {job_data['company_name']}")
            saved_count += 1

        except Exception as e:
            print(f"✗ Error saving job {job_data.get('job_title', 'Unknown')}: {e}")
            error_count += 1
            await db.rollback()

    print(f"\n=== Summary ===")
    print(f"Saved: {saved_count}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(jobs_data)}")


async def run_yc_scraper():
    """
    Run the Y Combinator scraper and save jobs to database
    """
    print("=== Starting Y Combinator Job Scraper ===\n")

    # Initialize scraper
    scraper = YCombinatorScraper()

    # Scrape all jobs
    print("Scraping jobs from Y Combinator...")
    jobs = await scraper.scrape_all_jobs()

    print(f"\nFound {len(jobs)} jobs")

    if not jobs:
        print("No jobs found. The scraper may need adjustment for YC's website structure.")
        return

    # Save to database
    print("\nSaving jobs to database...")
    async for db in get_db():
        await save_jobs_to_db(jobs, db)
        break  # Only need one iteration

    print("\n=== Scraping Complete ===")


async def main():
    """
    Main function - runs all scrapers
    """
    # For now, just run YC scraper
    # Later we can add more: await run_sequoia_scraper(), etc.

    await run_yc_scraper()

    # Close database connection
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
