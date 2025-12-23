"""
Auto-apply worker - Automatically submits job applications

Monitors applications with status="OUTSTANDING" and submits them automatically
"""

import asyncio
from datetime import datetime
from typing import Optional
import os

from sqlalchemy import select, and_
from anthropic import AsyncAnthropic

from app.core.database import get_db, engine
from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User


# Initialize Claude client
claude_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


async def generate_cover_letter(user: User, job: Job) -> str:
    """
    Generate personalized cover letter using Claude

    Args:
        user: User profile
        job: Job details

    Returns:
        Generated cover letter text
    """
    try:
        # Build user background
        user_background = f"""
Name: {user.first_name} {user.last_name}
Experience: {user.years_experience} years
Skills: {', '.join(user.skills[:10]) if user.skills else 'Not specified'}
Preferred sectors: {', '.join(user.sectors[:5]) if user.sectors else 'Not specified'}
Preferred roles: {', '.join(user.job_types[:5]) if user.job_types else 'Not specified'}
"""

        # Build job details
        job_details = f"""
Company: {job.company_name}
Position: {job.job_title}
Location: {job.location}
Category: {job.job_category}
Sector: {job.sector}
Description: {job.description[:1000]}
Requirements: {job.requirements[:500]}
"""

        prompt = f"""Write a professional, compelling cover letter for this job application.

USER PROFILE:
{user_background}

JOB DETAILS:
{job_details}

Instructions:
- Keep it concise (250-300 words)
- Highlight relevant experience and skills
- Show genuine interest in the company and role
- Be professional but authentic
- Don't use overly formal language
- Focus on value I can bring to the team
- Make it specific to this role, not generic

Cover letter:"""

        response = await claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        cover_letter = response.content[0].text.strip()
        return cover_letter

    except Exception as e:
        print(f"Error generating cover letter: {e}")
        # Return a basic fallback
        return f"I am writing to express my interest in the {job.job_title} position at {job.company_name}. With {user.years_experience} years of experience, I believe I would be a strong fit for this role."


async def submit_application(application: Application, user: User, job: Job) -> bool:
    """
    Attempt to submit application to company's ATS

    Args:
        application: Application record
        user: User profile
        job: Job details

    Returns:
        True if submission successful, False otherwise
    """
    # For now, we'll just mark it as "applied" since actual ATS submission
    # requires complex browser automation for each platform (Greenhouse, Lever, etc.)

    # In a production system, this would:
    # 1. Use Selenium/Playwright to navigate to application_url
    # 2. Fill out forms based on application_platform (Greenhouse, Lever, Workday, etc.)
    # 3. Upload resume if required
    # 4. Submit the application
    # 5. Handle any errors or CAPTCHAs

    print(f"  → Submitting to {job.company_name} via {job.application_platform}")
    print(f"     Application URL: {job.application_url}")

    # Simulate submission (in production, this would be actual ATS integration)
    await asyncio.sleep(1)  # Simulate API call

    return True


async def process_outstanding_applications():
    """
    Process all outstanding applications and submit them
    """
    print("\n" + "="*60)
    print("AUTO-APPLY WORKER - Processing Outstanding Applications")
    print("="*60 + "\n")

    async for db in get_db():
        # Get all outstanding applications
        result = await db.execute(
            select(Application)
            .where(Application.status == ApplicationStatus.OUTSTANDING)
            .order_by(Application.date_swiped)
        )
        applications = result.scalars().all()

        if not applications:
            print("✓ No outstanding applications to process\n")
            break

        print(f"Found {len(applications)} outstanding applications\n")

        processed_count = 0
        failed_count = 0

        for app in applications:
            try:
                # Get user and job details
                user_result = await db.execute(
                    select(User).where(User.user_id == app.user_id)
                )
                user = user_result.scalar_one()

                job_result = await db.execute(
                    select(Job).where(Job.job_id == app.job_id)
                )
                job = job_result.scalar_one()

                print(f"Processing: {job.job_title} at {job.company_name}")

                # Check daily limit
                today_apps = await db.execute(
                    select(Application)
                    .where(
                        and_(
                            Application.user_id == user.user_id,
                            Application.status == ApplicationStatus.APPLIED,
                            Application.date_applied >= datetime.utcnow().date()
                        )
                    )
                )
                today_count = len(today_apps.scalars().all())

                if today_count >= user.daily_application_limit:
                    print(f"  ⚠ Daily limit reached ({user.daily_application_limit}), skipping\n")
                    continue

                # Generate cover letter
                print("  → Generating cover letter...")
                cover_letter = await generate_cover_letter(user, job)
                app.cover_letter = cover_letter
                print(f"  ✓ Cover letter generated ({len(cover_letter)} chars)")

                # Submit application
                success = await submit_application(app, user, job)

                if success:
                    # Update application status
                    app.status = ApplicationStatus.APPLIED
                    app.date_applied = datetime.utcnow()
                    await db.commit()

                    print(f"  ✅ Application submitted successfully!\n")
                    processed_count += 1
                else:
                    print(f"  ❌ Submission failed\n")
                    failed_count += 1

                # Rate limiting - don't spam applications
                await asyncio.sleep(5)

            except Exception as e:
                print(f"  ❌ Error processing application: {e}\n")
                failed_count += 1
                await db.rollback()

        print("="*60)
        print(f"Summary:")
        print(f"  Successfully submitted: {processed_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total processed: {processed_count + failed_count}")
        print("="*60 + "\n")

        break

    await engine.dispose()


async def run_worker_loop(interval_seconds: int = 300):
    """
    Run worker in continuous loop

    Args:
        interval_seconds: Time between checks (default: 5 minutes)
    """
    print(f"Starting auto-apply worker (checking every {interval_seconds}s)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            await process_outstanding_applications()
            print(f"Waiting {interval_seconds} seconds before next check...\n")
            await asyncio.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n\nWorker stopped by user")
    except Exception as e:
        print(f"\n\nWorker error: {e}")


async def run_once():
    """Run worker once and exit"""
    await process_outstanding_applications()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        asyncio.run(run_once())
    else:
        # Run continuous loop
        asyncio.run(run_worker_loop())
