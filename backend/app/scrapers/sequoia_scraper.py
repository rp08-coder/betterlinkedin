"""
Sequoia Capital job scraper

Scrapes jobs from Sequoia portfolio companies
"""

from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime

from app.scrapers.base_scraper import BaseScraper


class SequoiaScraper(BaseScraper):
    """
    Sequoia Capital portfolio company job scraper

    Scrapes jobs from Sequoia portfolio companies via their career pages
    """

    def __init__(self):
        super().__init__("Sequoia Capital")
        self.base_url = "https://www.sequoiacap.com"
        self.portfolio_url = f"{self.base_url}/companies"

        # Known Sequoia portfolio companies with direct job pages
        # This is a curated list of top companies - you can expand this
        self.portfolio_companies = [
            {"name": "Apple", "jobs_url": "https://jobs.apple.com/en-us/search"},
            {"name": "Google", "jobs_url": "https://careers.google.com/jobs/results/"},
            {"name": "WhatsApp", "jobs_url": "https://www.whatsapp.com/join"},
            {"name": "Instagram", "jobs_url": "https://about.instagram.com/about-us/careers"},
            {"name": "YouTube", "jobs_url": "https://careers.google.com/jobs/results/?company=YouTube"},
            {"name": "LinkedIn", "jobs_url": "https://careers.linkedin.com/"},
            {"name": "Zoom", "jobs_url": "https://careers.zoom.us/"},
            {"name": "DoorDash", "jobs_url": "https://careers.doordash.com/jobs/"},
            {"name": "Unity", "jobs_url": "https://careers.unity.com/"},
            {"name": "Snowflake", "jobs_url": "https://careers.snowflake.com/us/en"},
            {"name": "MongoDB", "jobs_url": "https://www.mongodb.com/careers"},
            {"name": "ServiceNow", "jobs_url": "https://careers.servicenow.com/"},
            {"name": "Klarna", "jobs_url": "https://jobs.lever.co/klarna"},
            {"name": "Nubank", "jobs_url": "https://nubank.com.br/careers/"},
            {"name": "Block", "jobs_url": "https://careers.block.xyz/"},
            {"name": "Toast", "jobs_url": "https://careers.toasttab.com/"},
            {"name": "Deel", "jobs_url": "https://www.deel.com/careers"},
            {"name": "Palo Alto Networks", "jobs_url": "https://jobs.paloaltonetworks.com/"},
        ]

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of job URLs from Sequoia portfolio companies

        For now, we use a curated list of known portfolio companies.
        Future enhancement: scrape the portfolio page dynamically
        """
        job_urls = []

        for company in self.portfolio_companies:
            job_urls.append(company["jobs_url"])

        print(f"Found {len(job_urls)} Sequoia portfolio company job pages")
        return job_urls

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape job details from Sequoia portfolio company careers page

        This is a generic scraper - may need company-specific adjustments
        """
        try:
            html = await self.fetch_page(url, session)
            soup = self.parse_html(html)

            # Try to find company name from URL or page
            company_name = self.extract_company_from_url(url)

            # Look for job listings on the page
            jobs = []

            # Common patterns for job listings
            job_elements = (
                soup.find_all("div", class_=lambda x: x and ("job" in x.lower() or "position" in x.lower())) or
                soup.find_all("li", class_=lambda x: x and "opening" in x.lower()) or
                soup.find_all("tr", class_=lambda x: x and "job" in x.lower()) or
                soup.find_all("a", href=lambda x: x and ("/job/" in x or "/position/" in x))
            )

            # Limit to avoid overwhelming the database
            for job_elem in job_elements[:15]:  # First 15 jobs per company
                try:
                    # Extract job title
                    title_elem = (
                        job_elem.find("h2") or
                        job_elem.find("h3") or
                        job_elem.find("h4") or
                        job_elem.find("a") or
                        job_elem.find("span", class_=lambda x: x and "title" in x.lower())
                    )
                    job_title = title_elem.text.strip() if title_elem else "Position at " + company_name

                    # Skip if title is empty or too short
                    if not job_title or len(job_title) < 3:
                        continue

                    # Extract job link
                    link_elem = job_elem.find("a", href=True)
                    job_url = link_elem.get("href") if link_elem else url
                    if job_url and not job_url.startswith("http"):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        job_url = urljoin(url, job_url)

                    # Extract location if available
                    location_keywords = ["location", "office", "remote", "city"]
                    location_elem = None
                    for keyword in location_keywords:
                        location_elem = job_elem.find("span", class_=lambda x: x and keyword in x.lower())
                        if location_elem:
                            break

                    location = location_elem.text.strip() if location_elem else "Remote"

                    # Extract description if available
                    desc_elem = job_elem.find("p") or job_elem.find("div", class_=lambda x: x and "description" in x.lower())
                    description = desc_elem.text.strip() if desc_elem else f"Position at {company_name}, a portfolio company of Sequoia Capital"

                    # Categorize the job
                    job_category = self.categorize_job(job_title, description)

                    # Build job data
                    job_data = {
                        "source_url": job_url,
                        "vc_firm": self.vc_firm_name,
                        "company_name": company_name,
                        "company_logo_url": None,
                        "job_title": job_title,
                        "description": description[:5000],  # Limit description length
                        "requirements": "",
                        "job_category": job_category,
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

            if jobs:
                print(f"  → Found {len(jobs)} jobs at {company_name}")

            return jobs if jobs else None

        except Exception as e:
            print(f"Error scraping Sequoia company page at {url}: {e}")
            return None

    def extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        for company in self.portfolio_companies:
            if company["jobs_url"] in url or url in company["jobs_url"]:
                return company["name"]

        # Fallback: extract from domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        # Remove common prefixes/suffixes
        domain = domain.replace("www.", "").replace("careers.", "").replace("jobs.", "")
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

                # Rate limiting to be respectful
                await self.rate_limit()

        return all_jobs
