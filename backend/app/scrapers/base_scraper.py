"""
Base scraper class for job aggregation
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import time

from app.core.config import settings


class BaseScraper(ABC):
    """Base class for VC firm job scrapers"""

    def __init__(self, vc_firm_name: str):
        self.vc_firm_name = vc_firm_name
        self.rate_limit = settings.SCRAPING_RATE_LIMIT  # requests per second
        self.user_agent = settings.SCRAPING_USER_AGENT
        self.last_request_time = 0

    async def rate_limit_wait(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        wait_time = (1.0 / self.rate_limit) - elapsed

        if wait_time > 0:
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def fetch_page(self, url: str, session: aiohttp.ClientSession) -> str:
        """
        Fetch a web page with rate limiting

        Args:
            url: URL to fetch
            session: aiohttp session

        Returns:
            Page HTML content
        """
        await self.rate_limit_wait()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()

    @abstractmethod
    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of portfolio company job URLs

        Args:
            session: aiohttp session

        Returns:
            List of job page URLs
        """
        pass

    @abstractmethod
    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape a single job posting

        Args:
            url: Job posting URL
            session: aiohttp session

        Returns:
            Job data dict or None if failed
        """
        pass

    async def scrape_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Scrape all jobs from this VC firm's portfolio

        Returns:
            List of job data dicts
        """
        async with aiohttp.ClientSession() as session:
            # Get all job URLs
            job_urls = await self.get_portfolio_companies(session)

            # Scrape each job
            jobs = []
            for url in job_urls:
                try:
                    job_data = await self.scrape_job(url, session)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue

            return jobs

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, "lxml")

    def categorize_job(self, title: str, description: str) -> str:
        """
        Categorize job based on title and description

        Args:
            title: Job title
            description: Job description

        Returns:
            Job category (e.g., "Engineering", "Product", etc.)
        """
        title_lower = title.lower()
        desc_lower = description.lower()

        # Engineering
        if any(keyword in title_lower for keyword in ["engineer", "developer", "swe", "software"]):
            return "Engineering"

        # Product
        if any(keyword in title_lower for keyword in ["product manager", "pm", "product"]):
            return "Product"

        # Design
        if any(keyword in title_lower for keyword in ["designer", "design", "ux", "ui"]):
            return "Design"

        # Data
        if any(keyword in title_lower for keyword in ["data scientist", "data analyst", "ml", "machine learning"]):
            return "Data Science"

        # Operations
        if any(keyword in title_lower for keyword in ["operations", "ops", "business operations"]):
            return "Operations"

        # Sales
        if any(keyword in title_lower for keyword in ["sales", "account executive", "ae"]):
            return "Sales"

        # Marketing
        if any(keyword in title_lower for keyword in ["marketing", "growth"]):
            return "Marketing"

        # Customer Success
        if any(keyword in title_lower for keyword in ["customer success", "support"]):
            return "Customer Success"

        return "Other"

    def determine_sector(self, company_name: str, description: str) -> str:
        """
        Determine sector/industry based on company and description

        Args:
            company_name: Company name
            description: Job/company description

        Returns:
            Sector name
        """
        desc_lower = description.lower()

        if any(keyword in desc_lower for keyword in ["fintech", "financial", "banking", "payments"]):
            return "Fintech"

        if any(keyword in desc_lower for keyword in ["healthcare", "health", "medical", "biotech"]):
            return "Healthcare"

        if any(keyword in desc_lower for keyword in ["ai", "machine learning", "artificial intelligence", "ml"]):
            return "AI/ML"

        if any(keyword in desc_lower for keyword in ["ecommerce", "e-commerce", "marketplace"]):
            return "E-commerce"

        if any(keyword in desc_lower for keyword in ["saas", "software as a service", "enterprise software"]):
            return "SaaS"

        if any(keyword in desc_lower for keyword in ["consumer", "b2c"]):
            return "Consumer"

        if any(keyword in desc_lower for keyword in ["cybersecurity", "security", "infosec"]):
            return "Cybersecurity"

        if any(keyword in desc_lower for keyword in ["climate", "sustainability", "clean energy"]):
            return "Climate Tech"

        if any(keyword in desc_lower for keyword in ["crypto", "blockchain", "web3"]):
            return "Crypto/Web3"

        if any(keyword in desc_lower for keyword in ["education", "edtech", "learning"]):
            return "EdTech"

        return "Technology"

    def detect_ats_platform(self, url: str, html: str) -> str:
        """
        Detect which ATS platform the job posting uses

        Args:
            url: Job posting URL
            html: Page HTML

        Returns:
            ATS platform name
        """
        if "greenhouse.io" in url or "greenhouse" in html.lower():
            return "greenhouse"

        if "lever.co" in url or "lever" in html.lower():
            return "lever"

        if "ashbyhq.com" in url or "ashby" in html.lower():
            return "ashby"

        if "workable.com" in url:
            return "workable"

        if "breezy.hr" in url:
            return "breezy"

        return "custom"
