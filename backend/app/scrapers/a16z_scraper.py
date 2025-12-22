"""
Andreessen Horowitz (a16z) job scraper

Scrapes jobs from a16z portfolio companies
"""

from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime

from app.scrapers.base_scraper import BaseScraper


class A16zScraper(BaseScraper):
    """
    Andreessen Horowitz portfolio company job scraper

    Scrapes jobs from a16z portfolio companies via their career pages
    """

    def __init__(self):
        super().__init__("Andreessen Horowitz")
        self.base_url = "https://a16z.com"
        self.portfolio_url = f"{self.base_url}/portfolio"

        # Known a16z portfolio companies with direct job pages
        # This is a curated list of top companies - you can expand this
        self.portfolio_companies = [
            {"name": "Airbnb", "jobs_url": "https://careers.airbnb.com/positions/"},
            {"name": "Coinbase", "jobs_url": "https://www.coinbase.com/careers/positions"},
            {"name": "GitHub", "jobs_url": "https://github.com/about/careers"},
            {"name": "Instacart", "jobs_url": "https://instacart.careers/current-openings/"},
            {"name": "Stripe", "jobs_url": "https://stripe.com/jobs/search"},
            {"name": "Roblox", "jobs_url": "https://careers.roblox.com/jobs"},
            {"name": "DoorDash", "jobs_url": "https://careers.doordash.com/jobs/"},
            {"name": "Databricks", "jobs_url": "https://www.databricks.com/company/careers/open-positions"},
            {"name": "Notion", "jobs_url": "https://www.notion.so/careers"},
            {"name": "Figma", "jobs_url": "https://www.figma.com/careers/"},
            {"name": "OpenAI", "jobs_url": "https://openai.com/careers/"},
            {"name": "Retool", "jobs_url": "https://retool.com/careers/"},
            {"name": "Scale AI", "jobs_url": "https://scale.com/careers"},
            {"name": "Anduril", "jobs_url": "https://www.anduril.com/careers/"},
            {"name": "Substack", "jobs_url": "https://substack.com/jobs"},
        ]

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of job URLs from a16z portfolio companies

        For now, we use a curated list of known portfolio companies.
        Future enhancement: scrape the portfolio page dynamically
        """
        job_urls = []

        for company in self.portfolio_companies:
            job_urls.append(company["jobs_url"])

        print(f"Found {len(job_urls)} a16z portfolio company job pages")
        return job_urls

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape job details from a16z portfolio company careers page

        This is a generic scraper - may need company-specific adjustments
        """
        try:
            html = await self.fetch_page(url, session)
            soup = self.parse_html(html)

            # Try to find company name from URL or page
            company_name = self.extract_company_from_url(url)

            # Look for job listings on the page
            # Different companies use different HTML structures
            jobs = []

            # Common patterns for job listings
            job_elements = (
                soup.find_all("div", class_=lambda x: x and "job" in x.lower()) or
                soup.find_all("li", class_=lambda x: x and "position" in x.lower()) or
                soup.find_all("a", href=lambda x: x and "/jobs/" in x)
            )

            for job_elem in job_elements[:10]:  # Limit to first 10 jobs per company
                try:
                    # Extract job title
                    title_elem = (
                        job_elem.find("h2") or
                        job_elem.find("h3") or
                        job_elem.find("a")
                    )
                    job_title = title_elem.text.strip() if title_elem else "Position at " + company_name

                    # Extract job link
                    link_elem = job_elem.find("a", href=True)
                    job_url = link_elem.get("href") if link_elem else url
                    if job_url and not job_url.startswith("http"):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        job_url = urljoin(url, job_url)

                    # Extract location if available
                    location_elem = job_elem.find("span", class_=lambda x: x and "location" in x.lower())
                    location = location_elem.text.strip() if location_elem else "Remote"

                    # Build job data
                    job_data = {
                        "source_url": job_url,
                        "vc_firm": self.vc_firm_name,
                        "company_name": company_name,
                        "company_logo_url": None,
                        "job_title": job_title,
                        "description": f"Position at {company_name}, a portfolio company of Andreessen Horowitz",
                        "requirements": "",
                        "job_category": self.categorize_job(job_title, ""),
                        "sector": "Technology",
                        "location": location,
                        "date_posted": None,
                        "application_url": job_url,
                        "application_platform": self.detect_ats_platform(job_url, html),
                        "custom_questions": None,
                    }

                    jobs.append(job_data)

                except Exception as e:
                    print(f"Error parsing job element: {e}")
                    continue

            return jobs if jobs else None

        except Exception as e:
            print(f"Error scraping a16z company page at {url}: {e}")
            return None

    def extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        for company in self.portfolio_companies:
            if company["jobs_url"] in url or url in company["jobs_url"]:
                return company["name"]

        # Fallback: extract from domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        company = domain.split('.')[0] if domain else "Unknown"
        return company.title()

    async def scrape_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Override scrape_all_jobs to handle company pages instead of individual job pages
        """
        all_jobs = []

        async with aiohttp.ClientSession() as session:
            company_urls = await self.get_portfolio_companies(session)

            for company_url in company_urls:
                print(f"Scraping jobs from {company_url}...")
                jobs = await self.scrape_job(company_url, session)

                if jobs:
                    if isinstance(jobs, list):
                        all_jobs.extend(jobs)
                    else:
                        all_jobs.append(jobs)

                # Rate limiting
                await self.rate_limit()

        return all_jobs
