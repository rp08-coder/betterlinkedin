"""
AI-powered job matching and categorization using Claude

Uses Claude to intelligently match user profiles to jobs and categorize jobs
"""

import asyncio
from typing import Dict, List, Tuple
from anthropic import AsyncAnthropic

from app.models.job import Job
from app.models.user import User
from app.core.config import settings


# Initialize Claude client with API key from settings
claude_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def categorize_job_with_ai(job: Job) -> Dict[str, str]:
    """
    Use AI to determine the actual job category and profile type

    Returns:
        Dict with 'job_category' and 'target_profile' (e.g., 'investment_banker', 'software_engineer', 'consultant')
    """
    try:
        prompt = f"""Analyze this job posting and determine:
1. What is the PRIMARY job function/category?
2. What type of candidate profile would be the BEST fit?

Job Title: {job.job_title}
Company: {job.company_name}
Location: {job.location}
Description: {job.description[:1500]}
Requirements: {job.requirements[:800]}

Respond in this exact format:
JOB_CATEGORY: [one of: Finance, Corporate Development, Strategy, Business Operations, Partnerships, Revenue Operations, GTM Strategy, Sales Operations, Business Development, Product Management, Engineering, Design, Data Science, Sales, Marketing, Operations, Other]

TARGET_PROFILE: [one of: investment_banker, consultant, software_engineer, product_manager, sales_gtm, designer, data_scientist, generalist]

REASONING: [1-2 sentences explaining why]
"""

        response = await claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result_text = response.content[0].text.strip()

        # Parse response
        lines = result_text.split('\n')
        job_category = "Other"
        target_profile = "generalist"

        for line in lines:
            if line.startswith("JOB_CATEGORY:"):
                job_category = line.replace("JOB_CATEGORY:", "").strip()
            elif line.startswith("TARGET_PROFILE:"):
                target_profile = line.replace("TARGET_PROFILE:", "").strip()

        return {
            "job_category": job_category,
            "target_profile": target_profile,
            "reasoning": result_text
        }

    except Exception as e:
        print(f"Error categorizing job with AI: {e}")
        return {
            "job_category": job.job_category or "Other",
            "target_profile": "generalist",
            "reasoning": "Error during AI analysis"
        }


async def match_user_to_job(user: User, job: Job, job_ai_category: Dict) -> float:
    """
    Use AI to score how well a user matches a job

    Returns:
        Score from 0.0 to 1.0
    """
    try:
        # Determine user profile type
        user_profile_type = determine_user_profile_type(user)

        prompt = f"""You are a career matching expert. Score how well this candidate matches this job opportunity.

CANDIDATE PROFILE:
Name: {user.first_name} {user.last_name}
Profile Type: {user_profile_type}
Experience: {user.years_experience} years
Skills: {', '.join(user.skills[:15]) if user.skills else 'Not specified'}
Preferred Sectors: {', '.join(user.sectors[:8]) if user.sectors else 'Not specified'}
Preferred Roles: {', '.join(user.job_types[:8]) if user.job_types else 'Not specified'}

JOB OPPORTUNITY:
Company: {job.company_name}
Title: {job.job_title}
Category: {job_ai_category['job_category']}
Target Profile: {job_ai_category['target_profile']}
Sector: {job.sector}
Location: {job.location}
Description: {job.description[:1000]}
Requirements: {job.requirements[:600]}

MATCHING RULES:
- Investment bankers should see: Finance, Corporate Development, Strategy, Business Operations, Partnerships, GTM Strategy, Revenue Operations roles
- Consultants should see: Strategy, Business Operations, GTM Strategy, Product Management, Partnerships, Revenue Operations roles
- Software engineers should see: Engineering, Product Management (technical), Data Science roles
- Be INCLUSIVE - if there's any reasonable fit, give a good score
- Only give very low scores (< 0.5) for completely mismatched profiles (e.g., banker for pure engineering role)

Respond with ONLY a number between 0.0 and 1.0:
- 0.0-0.4 = Wrong profile (e.g., banker for pure engineering job)
- 0.5-0.6 = Possible match (some transferable skills)
- 0.7-0.8 = Good match (profile aligns well)
- 0.9-1.0 = Excellent match (perfect fit)

Score:"""

        response = await claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        score_text = response.content[0].text.strip()

        # Extract number from response
        try:
            score = float(score_text)
            return max(0.0, min(1.0, score))  # Clamp between 0 and 1
        except:
            # Fallback if parsing fails
            return 0.0

    except Exception as e:
        print(f"Error matching user to job with AI: {e}")
        return 0.0


def determine_user_profile_type(user: User) -> str:
    """
    Determine user's primary profile type based on their preferences
    """
    if not user.job_types:
        return "generalist"

    job_types_lower = [jt.lower() for jt in user.job_types]
    skills_lower = [s.lower() for s in user.skills] if user.skills else []

    # Investment banker indicators
    banker_keywords = ['finance', 'corporate development', 'corp dev', 'm&a', 'investment banking', 'financial modeling']
    if any(kw in ' '.join(job_types_lower + skills_lower) for kw in banker_keywords):
        return "investment_banker"

    # Consultant indicators
    consultant_keywords = ['strategy', 'consulting', 'business operations', 'bizops']
    if any(kw in ' '.join(job_types_lower + skills_lower) for kw in consultant_keywords):
        return "consultant"

    # Software engineer indicators
    engineer_keywords = ['engineering', 'software', 'backend', 'frontend', 'full stack', 'developer']
    if any(kw in ' '.join(job_types_lower + skills_lower) for kw in engineer_keywords):
        return "software_engineer"

    # Product manager indicators
    pm_keywords = ['product manager', 'product management', 'pm']
    if any(kw in ' '.join(job_types_lower) for kw in pm_keywords):
        return "product_manager"

    return "generalist"


async def batch_categorize_jobs(jobs: List[Job]) -> Dict[str, Dict]:
    """
    Categorize multiple jobs in parallel for efficiency
    """
    print(f"\n🤖 Using AI to categorize {len(jobs)} jobs...")

    tasks = [categorize_job_with_ai(job) for job in jobs]
    results = await asyncio.gather(*tasks)

    categorizations = {}
    for job, result in zip(jobs, results):
        categorizations[str(job.job_id)] = result
        print(f"  ✓ {job.company_name} - {job.job_title}")
        print(f"    Category: {result['job_category']}, Target: {result['target_profile']}")

    return categorizations


async def batch_match_user_to_jobs(user: User, jobs: List[Job], categorizations: Dict) -> List[Tuple[Job, float]]:
    """
    Match user to multiple jobs in parallel
    """
    print(f"\n🎯 Matching jobs to {user.first_name}'s profile...")

    tasks = []
    for job in jobs:
        job_category = categorizations.get(str(job.job_id), {"job_category": "Other", "target_profile": "generalist"})
        tasks.append(match_user_to_job(user, job, job_category))

    scores = await asyncio.gather(*tasks)

    matches = []
    for job, score in zip(jobs, scores):
        if score >= 0.5:  # Include possible matches and above (lowered from 0.6)
            matches.append((job, score))
            print(f"  ✓ {score:.0%} match: {job.job_title} at {job.company_name}")
        else:
            print(f"  ✗ {score:.0%} match: {job.job_title} at {job.company_name} (filtered out)")

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches
