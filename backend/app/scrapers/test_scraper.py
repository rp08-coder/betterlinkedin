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
        "source_url": "https://boards.greenhouse.io/spacex/jobs/123001",
        "vc_firm": "Sequoia Capital",
        "company_name": "SpaceX",
        "company_logo_url": "https://logo.clearbit.com/spacex.com",
        "job_title": "Software Engineer - Starlink",
        "description": "Join SpaceX's Starlink team to build the world's largest satellite constellation. Work on software that connects millions of users to high-speed internet from space. Build reliable, low-latency networking systems and user-facing applications.",
        "requirements": "Bachelor's in CS or equivalent, 3+ years software development, strong C++/Go/Python skills, networking protocols knowledge",
        "job_category": "Engineering",
        "sector": "Aerospace",
        "location": "Hawthorne, CA",
        "date_posted": None,
        "application_url": "https://boards.greenhouse.io/spacex/jobs/123001",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://stripe.com/jobs/listing/senior-backend-engineer",
        "vc_firm": "Sequoia Capital",
        "company_name": "Stripe",
        "company_logo_url": "https://logo.clearbit.com/stripe.com",
        "job_title": "Senior Backend Engineer - Payments",
        "description": "Build the financial infrastructure that powers millions of businesses. Work on high-scale distributed systems processing billions of dollars in payments daily. Solve complex problems in money movement, fraud detection, and global compliance.",
        "requirements": "5+ years backend engineering, distributed systems experience, Ruby/Go/Java proficiency, strong CS fundamentals",
        "job_category": "Engineering",
        "sector": "FinTech",
        "location": "San Francisco, CA / New York, NY / Remote",
        "date_posted": None,
        "application_url": "https://stripe.com/jobs/listing/senior-backend-engineer",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://mongodb.com/careers/jobs/789456",
        "vc_firm": "Sequoia Capital",
        "company_name": "MongoDB",
        "company_logo_url": "https://logo.clearbit.com/mongodb.com",
        "job_title": "Product Manager - Atlas Database",
        "description": "Shape the future of MongoDB Atlas, the leading cloud database platform. Define product strategy for features used by thousands of companies. Work with engineering to build developer-friendly database solutions.",
        "requirements": "4+ years PM experience, technical background preferred, B2B SaaS experience, strong analytical skills",
        "job_category": "Product",
        "sector": "Database",
        "location": "New York, NY / Palo Alto, CA",
        "date_posted": None,
        "application_url": "https://www.mongodb.com/careers/jobs/789456",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://zoom.us/careers/001122",
        "vc_firm": "Sequoia Capital",
        "company_name": "Zoom",
        "company_logo_url": "https://logo.clearbit.com/zoom.us",
        "job_title": "Machine Learning Engineer - Video Quality",
        "description": "Build ML systems that optimize video quality for millions of Zoom users. Work on real-time video processing, bandwidth optimization, and noise cancellation algorithms.",
        "requirements": "MS/PhD in CS/ML, 3+ years ML engineering, video processing experience, Python/C++ skills, deep learning frameworks",
        "job_category": "Engineering",
        "sector": "Video Communications",
        "location": "San Jose, CA",
        "date_posted": None,
        "application_url": "https://careers.zoom.us/apply/001122",
        "application_platform": "Workday",
        "custom_questions": None,
    },
    {
        "source_url": "https://snowflake.com/careers/332211",
        "vc_firm": "Sequoia Capital",
        "company_name": "Snowflake",
        "company_logo_url": "https://logo.clearbit.com/snowflake.com",
        "job_title": "Sales Engineer - Enterprise",
        "description": "Help enterprise customers understand and adopt Snowflake's data cloud platform. Design technical solutions, deliver demos, and partner with sales to close strategic deals.",
        "requirements": "5+ years SE/solutions consulting, data warehousing knowledge, SQL expertise, presentation skills, technical degree",
        "job_category": "Sales",
        "sector": "Data & Analytics",
        "location": "San Francisco, CA / New York, NY",
        "date_posted": None,
        "application_url": "https://careers.snowflake.com/apply/332211",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://block.xyz/careers/554433",
        "vc_firm": "Sequoia Capital",
        "company_name": "Block (Square)",
        "company_logo_url": "https://logo.clearbit.com/block.xyz",
        "job_title": "Product Designer - Cash App",
        "description": "Design delightful experiences for Cash App's 50M+ users. Work on features including peer-to-peer payments, Bitcoin, stocks, and banking. Shape the future of mobile-first finance.",
        "requirements": "4+ years product design, mobile app design portfolio, Figma proficiency, user research skills, FinTech interest",
        "job_category": "Design",
        "sector": "FinTech",
        "location": "San Francisco, CA / New York, NY",
        "date_posted": None,
        "application_url": "https://block.xyz/careers/jobs/554433",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://robinhood.com/careers/665544",
        "vc_firm": "Sequoia Capital",
        "company_name": "Robinhood",
        "company_logo_url": "https://logo.clearbit.com/robinhood.com",
        "job_title": "Data Scientist - Growth",
        "description": "Drive Robinhood's user growth through data. Build models for user acquisition, retention, and engagement. Run experiments to optimize conversion funnels and identify growth opportunities.",
        "requirements": "MS/PhD in quantitative field, 3+ years data science, A/B testing expertise, Python/SQL/R proficiency, FinTech interest",
        "job_category": "Data",
        "sector": "FinTech",
        "location": "Menlo Park, CA",
        "date_posted": None,
        "application_url": "https://robinhood.com/careers/openings/665544",
        "application_platform": "Lever",
        "custom_questions": None,
    },
    {
        "source_url": "https://servicenow.com/careers/776655",
        "vc_firm": "Sequoia Capital",
        "company_name": "ServiceNow",
        "company_logo_url": "https://logo.clearbit.com/servicenow.com",
        "job_title": "Senior Software Engineer - AI/ML Platform",
        "description": "Build ServiceNow's AI platform that powers automation across IT, HR, and customer workflows. Work on NLP, ML infrastructure, and AI-driven insights for enterprise customers.",
        "requirements": "6+ years engineering, ML/AI experience, Java/Python, distributed systems, enterprise software background",
        "job_category": "Engineering",
        "sector": "Enterprise Software",
        "location": "Santa Clara, CA / Remote",
        "date_posted": None,
        "application_url": "https://careers.servicenow.com/jobs/776655",
        "application_platform": "Workday",
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
