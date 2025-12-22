"""
Test script to add sample jobs to database
This demonstrates the scraper functionality with mock data
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.job import Job


# Sample jobs from Y Combinator
YC_JOBS = [
    {
        "source_url": "https://www.workatastartup.com/jobs/12345",
        "vc_firm": "Y Combinator",
        "company_name": "Stripe",
        "company_logo_url": "https://logo.clearbit.com/stripe.com",
        "job_title": "Senior Software Engineer - Backend",
        "description": "Join Stripe's platform team to build payment infrastructure for the internet. Work on high-scale distributed systems processing billions of dollars.",
        "requirements": "5+ years Python/Go experience, distributed systems knowledge, strong CS fundamentals",
        "job_category": "Engineering",
        "sector": "FinTech",
        "location": "San Francisco, CA / Remote",
        "date_posted": None,
        "application_url": "https://stripe.com/jobs/listing/senior-software-engineer",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://www.workatastartup.com/jobs/12346",
        "vc_firm": "Y Combinator",
        "company_name": "Airbnb",
        "company_logo_url": "https://logo.clearbit.com/airbnb.com",
        "job_title": "Product Manager - Trust & Safety",
        "description": "Lead product initiatives to make Airbnb the most trusted community marketplace. Define strategy for identity verification, fraud prevention, and user safety.",
        "requirements": "3+ years PM experience, marketplace/platform experience preferred, data-driven mindset",
        "job_category": "Product",
        "sector": "Marketplace",
        "location": "San Francisco, CA",
        "date_posted": None,
        "application_url": "https://careers.airbnb.com/positions/12346",
        "application_platform": "Lever",
        "custom_questions": None,
    },
    {
        "source_url": "https://www.workatastartup.com/jobs/12347",
        "vc_firm": "Y Combinator",
        "company_name": "DoorDash",
        "company_logo_url": "https://logo.clearbit.com/doordash.com",
        "job_title": "Data Scientist - Growth",
        "description": "Drive DoorDash's growth through experimentation and analytics. Build models to optimize user acquisition, retention, and monetization.",
        "requirements": "MS/PhD in quantitative field, Python/R/SQL expertise, A/B testing experience, 2+ years industry experience",
        "job_category": "Data",
        "sector": "Logistics",
        "location": "San Francisco, CA / New York, NY",
        "date_posted": None,
        "application_url": "https://careers.doordash.com/jobs/12347",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
]

# Sample jobs from Andreessen Horowitz
A16Z_JOBS = [
    {
        "source_url": "https://jobs.lever.co/coinbase/abc123",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Coinbase",
        "company_logo_url": "https://logo.clearbit.com/coinbase.com",
        "job_title": "Senior Backend Engineer - Blockchain Infrastructure",
        "description": "Build the future of cryptocurrency infrastructure. Work on systems that handle billions in crypto transactions securely and reliably.",
        "requirements": "5+ years backend engineering, distributed systems experience, blockchain knowledge a plus",
        "job_category": "Engineering",
        "sector": "Crypto",
        "location": "Remote",
        "date_posted": None,
        "application_url": "https://www.coinbase.com/careers/positions/abc123",
        "application_platform": "Lever",
        "custom_questions": None,
    },
    {
        "source_url": "https://github.com/about/careers/xyz789",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "GitHub",
        "company_logo_url": "https://logo.clearbit.com/github.com",
        "job_title": "Product Designer - Developer Experience",
        "description": "Design experiences that empower millions of developers. Shape the tools that developers use every day to build software.",
        "requirements": "4+ years product design, portfolio showing developer tools work, Figma proficiency",
        "job_category": "Design",
        "sector": "Developer Tools",
        "location": "Remote",
        "date_posted": None,
        "application_url": "https://github.com/about/careers/xyz789",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://instacart.careers/def456",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Instacart",
        "company_logo_url": "https://logo.clearbit.com/instacart.com",
        "job_title": "Machine Learning Engineer - Recommendations",
        "description": "Build ML systems that recommend products to millions of shoppers. Improve grocery discovery through personalization and search.",
        "requirements": "MS in CS/ML or equivalent, Python/TensorFlow/PyTorch, production ML experience, 3+ years",
        "job_category": "Engineering",
        "sector": "E-commerce",
        "location": "San Francisco, CA / Remote",
        "date_posted": None,
        "application_url": "https://instacart.careers/positions/def456",
        "application_platform": "Lever",
        "custom_questions": None,
    },
]

# Sample jobs from Sequoia Capital
SEQUOIA_JOBS = [
    {
        "source_url": "https://www.linkedin.com/jobs/view/111222333",
        "vc_firm": "Sequoia Capital",
        "company_name": "LinkedIn",
        "company_logo_url": "https://logo.clearbit.com/linkedin.com",
        "job_title": "Staff Software Engineer - Feed Ranking",
        "description": "Lead the development of LinkedIn's feed ranking systems. Impact how millions of professionals discover content and opportunities.",
        "requirements": "8+ years engineering, machine learning systems at scale, Java/Scala experience",
        "job_category": "Engineering",
        "sector": "Social Network",
        "location": "Sunnyvale, CA",
        "date_posted": None,
        "application_url": "https://careers.linkedin.com/jobs/111222333",
        "application_platform": "Internal ATS",
        "custom_questions": None,
    },
    {
        "source_url": "https://careers.zoom.us/positions/444555666",
        "vc_firm": "Sequoia Capital",
        "company_name": "Zoom",
        "company_logo_url": "https://logo.clearbit.com/zoom.us",
        "job_title": "Senior Product Manager - Enterprise Features",
        "description": "Drive enterprise product strategy for Zoom. Build features that help large organizations communicate and collaborate effectively.",
        "requirements": "5+ years PM experience, enterprise SaaS background, technical depth, MBA preferred",
        "job_category": "Product",
        "sector": "Video Communications",
        "location": "San Jose, CA / Remote",
        "date_posted": None,
        "application_url": "https://careers.zoom.us/apply/444555666",
        "application_platform": "Workday",
        "custom_questions": None,
    },
    {
        "source_url": "https://snowflake.com/careers/777888999",
        "vc_firm": "Sequoia Capital",
        "company_name": "Snowflake",
        "company_logo_url": "https://logo.clearbit.com/snowflake.com",
        "job_title": "Solutions Architect - Financial Services",
        "description": "Help financial institutions modernize their data infrastructure with Snowflake. Design cloud data architectures and drive technical wins.",
        "requirements": "6+ years solutions architecture, financial services domain expertise, cloud platforms knowledge",
        "job_category": "Sales",
        "sector": "Data & Analytics",
        "location": "New York, NY",
        "date_posted": None,
        "application_url": "https://careers.snowflake.com/apply/777888999",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
]


async def add_sample_jobs():
    """Add sample jobs to the database"""

    all_jobs = YC_JOBS + A16Z_JOBS + SEQUOIA_JOBS

    print(f"\nAdding {len(all_jobs)} sample jobs to database...\n")

    saved_count = 0
    duplicate_count = 0

    async for db in get_db():
        for job_data in all_jobs:
            try:
                # Check if job already exists
                result = await db.execute(
                    select(Job).where(Job.source_url == job_data["source_url"])
                )
                existing_job = result.scalar_one_or_none()

                if existing_job:
                    print(f"✓ Already exists: {job_data['job_title']} at {job_data['company_name']}")
                    duplicate_count += 1
                    continue

                # Create new job
                job = Job(**job_data)
                db.add(job)
                await db.commit()

                print(f"✓ Added: {job_data['job_title']} at {job_data['company_name']}")
                saved_count += 1

            except Exception as e:
                print(f"✗ Error: {e}")
                await db.rollback()

        break  # Only need one iteration

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  New jobs added: {saved_count}")
    print(f"  Duplicates skipped: {duplicate_count}")
    print(f"  Total: {len(all_jobs)}")
    print(f"{'='*60}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_sample_jobs())
