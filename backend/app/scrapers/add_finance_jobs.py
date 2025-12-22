"""
Add finance, bizops, and GTM focused jobs from top startups
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, engine
from app.models.job import Job


# Finance, BizOps, and GTM jobs from top startups
FINANCE_GTM_JOBS = [
    {
        "source_url": "https://stripe.com/jobs/corp-dev-001",
        "vc_firm": "Sequoia Capital",
        "company_name": "Stripe",
        "company_logo_url": "https://logo.clearbit.com/stripe.com",
        "job_title": "Corporate Development Associate",
        "description": "Drive strategic partnerships and M&A initiatives for Stripe. Evaluate acquisition targets, structure deals, and support post-merger integration. Work directly with executive leadership on high-impact strategic initiatives.",
        "requirements": "Investment banking or management consulting experience, MBA or equivalent, financial modeling expertise, deal experience, strong communication skills",
        "job_category": "Finance",
        "sector": "FinTech",
        "location": "San Francisco, CA",
        "date_posted": None,
        "application_url": "https://stripe.com/jobs/corp-dev-001",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://airbnb.com/careers/bizops-002",
        "vc_firm": "Sequoia Capital",
        "company_name": "Airbnb",
        "company_logo_url": "https://logo.clearbit.com/airbnb.com",
        "job_title": "Business Operations Manager - Growth",
        "description": "Lead cross-functional initiatives to accelerate Airbnb's growth. Build financial models, analyze business metrics, and drive strategic projects. Partner with Product, Engineering, and Marketing to launch new features.",
        "requirements": "3+ years consulting, investment banking, or tech bizops, strong analytical skills, Excel/SQL proficiency, MBA preferred",
        "job_category": "Business Operations",
        "sector": "Marketplace",
        "location": "San Francisco, CA",
        "date_posted": None,
        "application_url": "https://careers.airbnb.com/positions/bizops-002",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://coinbase.com/careers/partnerships-003",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Coinbase",
        "company_logo_url": "https://logo.clearbit.com/coinbase.com",
        "job_title": "Head of Strategic Partnerships",
        "description": "Build and manage strategic partnerships that drive Coinbase's institutional business. Negotiate complex deals with financial institutions, fintechs, and crypto protocols. Own partnership P&L and revenue targets.",
        "requirements": "8+ years partnerships or BD experience, FinTech/crypto background, deal negotiation skills, executive presence, proven track record of closing large deals",
        "job_category": "Partnerships",
        "sector": "Crypto",
        "location": "New York, NY / Remote",
        "date_posted": None,
        "application_url": "https://www.coinbase.com/careers/positions/partnerships-003",
        "application_platform": "Lever",
        "custom_questions": None,
    },
    {
        "source_url": "https://robinhood.com/careers/finance-004",
        "vc_firm": "Sequoia Capital",
        "company_name": "Robinhood",
        "company_logo_url": "https://logo.clearbit.com/robinhood.com",
        "job_title": "Senior Finance Manager - FP&A",
        "description": "Lead financial planning and analysis for Robinhood's core brokerage business. Build forecast models, analyze unit economics, and support strategic decision-making. Partner with executive team on business strategy.",
        "requirements": "5+ years FP&A experience, investment banking or consulting background, advanced Excel/SQL, FinTech experience preferred, CFA or MBA a plus",
        "job_category": "Finance",
        "sector": "FinTech",
        "location": "Menlo Park, CA",
        "date_posted": None,
        "application_url": "https://robinhood.com/careers/openings/finance-004",
        "application_platform": "Lever",
        "custom_questions": None,
    },
    {
        "source_url": "https://instacart.com/careers/revops-005",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Instacart",
        "company_logo_url": "https://logo.clearbit.com/instacart.com",
        "job_title": "Revenue Operations Lead",
        "description": "Build and scale Instacart's revenue operations function. Define sales processes, implement tools, analyze pipeline metrics, and drive revenue growth. Work cross-functionally with Sales, Marketing, and Finance.",
        "requirements": "4+ years RevOps or sales operations, SaaS/marketplace experience, Salesforce expertise, strong analytical skills, process optimization mindset",
        "job_category": "Revenue Operations",
        "sector": "E-commerce",
        "location": "San Francisco, CA / Remote",
        "date_posted": None,
        "application_url": "https://instacart.careers/positions/revops-005",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://notion.so/careers/gtm-006",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Notion",
        "company_logo_url": "https://logo.clearbit.com/notion.so",
        "job_title": "GTM Strategy & Operations Manager",
        "description": "Define and execute Notion's go-to-market strategy. Analyze market opportunities, build business cases, and launch new products. Support executive team with strategic planning and business operations.",
        "requirements": "3+ years strategy consulting or GTM operations, SaaS experience, strong analytical and communication skills, MBA or equivalent",
        "job_category": "GTM Strategy",
        "sector": "Productivity Software",
        "location": "San Francisco, CA / New York, NY",
        "date_posted": None,
        "application_url": "https://www.notion.so/careers/gtm-006",
        "application_platform": "Ashby",
        "custom_questions": None,
    },
    {
        "source_url": "https://plaid.com/careers/bd-007",
        "vc_firm": "Andreessen Horowitz",
        "company_name": "Plaid",
        "company_logo_url": "https://logo.clearbit.com/plaid.com",
        "job_title": "Business Development Manager - FinTech",
        "description": "Drive partnerships with FinTech companies to expand Plaid's network. Source and close strategic deals, negotiate terms, and manage partner relationships. Build Plaid's ecosystem of financial applications.",
        "requirements": "3+ years BD or partnerships, FinTech industry knowledge, deal closing experience, relationship building skills, technical aptitude",
        "job_category": "Business Development",
        "sector": "FinTech",
        "location": "San Francisco, CA / New York, NY",
        "date_posted": None,
        "application_url": "https://plaid.com/careers/openings/bd-007",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
    {
        "source_url": "https://brex.com/careers/strategy-008",
        "vc_firm": "Y Combinator",
        "company_name": "Brex",
        "company_logo_url": "https://logo.clearbit.com/brex.com",
        "job_title": "Strategy & Operations Lead - New Products",
        "description": "Lead strategic initiatives for new product launches at Brex. Conduct market analysis, build business cases, and drive cross-functional execution. Partner with Product and Engineering on go-to-market strategy.",
        "requirements": "4+ years consulting, investment banking, or tech strategy, FinTech experience preferred, strong quantitative skills, entrepreneurial mindset",
        "job_category": "Strategy",
        "sector": "FinTech",
        "location": "San Francisco, CA",
        "date_posted": None,
        "application_url": "https://www.brex.com/careers/strategy-008",
        "application_platform": "Ashby",
        "custom_questions": None,
    },
    {
        "source_url": "https://ramp.com/careers/corpdev-009",
        "vc_firm": "Sequoia Capital",
        "company_name": "Ramp",
        "company_logo_url": "https://logo.clearbit.com/ramp.com",
        "job_title": "Corporate Development - M&A",
        "description": "Lead M&A strategy and execution for Ramp's growth initiatives. Source acquisition opportunities, conduct due diligence, structure transactions, and drive integration. Work with CEO and CFO on strategic priorities.",
        "requirements": "Investment banking M&A experience required, FinTech sector knowledge, financial modeling expertise, deal execution skills, MBA preferred",
        "job_category": "Corporate Development",
        "sector": "FinTech",
        "location": "New York, NY",
        "date_posted": None,
        "application_url": "https://ramp.com/careers/corpdev-009",
        "application_platform": "Ashby",
        "custom_questions": None,
    },
    {
        "source_url": "https://chime.com/careers/sales-ops-010",
        "vc_firm": "Sequoia Capital",
        "company_name": "Chime",
        "company_logo_url": "https://logo.clearbit.com/chime.com",
        "job_title": "Sales Operations Manager - Enterprise",
        "description": "Build sales operations infrastructure for Chime's B2B business. Design sales processes, implement CRM systems, analyze sales metrics, and drive operational excellence. Enable the sales team to scale efficiently.",
        "requirements": "3+ years sales operations, SaaS or FinTech background, Salesforce admin experience, data analysis skills, process-oriented mindset",
        "job_category": "Sales Operations",
        "sector": "FinTech",
        "location": "San Francisco, CA",
        "date_posted": None,
        "application_url": "https://www.chime.com/careers/sales-ops-010",
        "application_platform": "Greenhouse",
        "custom_questions": None,
    },
]


async def add_finance_jobs():
    """Add finance/GTM jobs to database"""

    print(f"\n=== Adding {len(FINANCE_GTM_JOBS)} Finance/GTM Jobs ===\n")

    saved_count = 0
    duplicate_count = 0

    async for db in get_db():
        for job_data in FINANCE_GTM_JOBS:
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

        break

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  New jobs added: {saved_count}")
    print(f"  Duplicates skipped: {duplicate_count}")
    print(f"  Total: {len(FINANCE_GTM_JOBS)}")
    print(f"{'='*60}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_finance_jobs())
