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
from app.scrapers.a16z_scraper import A16zScraper
from app.scrapers.sequoia_scraper import SequoiaScraper


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


async def run_scraper(scraper_name: str, scraper):
    """
    Run a scraper and save jobs to database

    Args:
        scraper_name: Name of the VC firm
        scraper: Scraper instance
    """
    print(f"\n{'='*60}")
    print(f"Starting {scraper_name} Job Scraper")
    print(f"{'='*60}\n")

    # Scrape all jobs
    jobs = await scraper.scrape_all_jobs()

    print(f"\nFound {len(jobs)} jobs from {scraper_name}")

    if not jobs:
        print(f"No jobs found from {scraper_name}. The scraper may need adjustment.")
        return 0

    # Save to database
    print(f"\nSaving {scraper_name} jobs to database...")
    async for db in get_db():
        await save_jobs_to_db(jobs, db)
        break  # Only need one iteration

    return len(jobs)


async def run_yc_scraper():
    """Run the Y Combinator scraper"""
    scraper = YCombinatorScraper()
    return await run_scraper("Y Combinator", scraper)


async def run_a16z_scraper():
    """Run the Andreessen Horowitz scraper"""
    scraper = A16zScraper()
    return await run_scraper("Andreessen Horowitz", scraper)


async def run_sequoia_scraper():
    """Run the Sequoia Capital scraper"""
    scraper = SequoiaScraper()
    return await run_scraper("Sequoia Capital", scraper)


async def main():
    """
    Main function - runs all scrapers
    """
    print("\n" + "="*60)
    print("JOB SCRAPER - Multi-VC Firm Job Aggregator")
    print("="*60)
    print("\nScraping jobs from:")
    print("  • Sequoia Capital (https://jobs.sequoiacap.com)")
    print("\nThis may take a few minutes...\n")

    total_jobs = 0

    # Run Sequoia scraper (testing new version)
    try:
        sequoia_count = await run_sequoia_scraper()
        total_jobs += sequoia_count
    except Exception as e:
        print(f"Error running Sequoia scraper: {e}")

    # Commenting out other scrapers for now
    # try:
    #     yc_count = await run_yc_scraper()
    #     total_jobs += yc_count
    # except Exception as e:
    #     print(f"Error running YC scraper: {e}")

    # try:
    #     a16z_count = await run_a16z_scraper()
    #     total_jobs += a16z_count
    # except Exception as e:
    #     print(f"Error running a16z scraper: {e}")

    # Final summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    print(f"\nTotal jobs scraped: {total_jobs}")
    print("\nJobs are now available in your database and will appear")
    print("in the Founded iOS app! 🎉\n")

    # Close database connection
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
