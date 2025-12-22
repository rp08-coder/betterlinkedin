"""
Y Combinator job scraper

Scrapes jobs from https://www.workatastartup.com/companies
"""

from typing import List, Dict, Any, Optional
import aiohttp
import json
from datetime import datetime

from app.scrapers.base_scraper import BaseScraper


class YCombinatorScraper(BaseScraper):
    """
    Y Combinator job scraper for workatastartup.com

    This scraper fetches jobs from YC's Work at a Startup platform.
    The site loads jobs dynamically, so we'll need to handle their API/data structure.
    """

    def __init__(self):
        super().__init__("Y Combinator")
        self.base_url = "https://www.workatastartup.com"
        self.companies_url = f"{self.base_url}/companies"

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of job URLs from YC's Work at a Startup platform

        Note: This site may use JavaScript to load jobs dynamically.
        We'll try to extract company pages and then get their job listings.
        """
        job_urls = []

        try:
            # Fetch the main companies page
            html = await self.fetch_page(self.companies_url, session)
            soup = self.parse_html(html)

            # Look for company links
            # The actual selectors will depend on the site's HTML structure
            company_links = soup.find_all("a", href=True)

            for link in company_links:
                href = link.get("href", "")

                # Filter for company job pages
                if "/companies/" in href and "/jobs" in href:
                    full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                    job_urls.append(full_url)
                elif href.startswith("/jobs/"):
                    # Direct job links
                    full_url = f"{self.base_url}{href}"
                    job_urls.append(full_url)

            # Remove duplicates
            job_urls = list(set(job_urls))

            print(f"Found {len(job_urls)} job URLs from Y Combinator")

        except Exception as e:
            print(f"Error fetching YC portfolio companies: {e}")

        return job_urls

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape details from a single YC job posting

        Returns job data dict matching the Job model schema
        """
        try:
            html = await self.fetch_page(url, session)
            soup = self.parse_html(html)

            # Extract job details based on YC's HTML structure
            # These selectors are examples and may need adjustment

            # Company name
            company_elem = soup.find("h1") or soup.find("h2", class_="company-name")
            company_name = company_elem.text.strip() if company_elem else "Unknown Company"

            # Job title
            title_elem = soup.find("h1", class_="job-title") or soup.find("h2")
            job_title = title_elem.text.strip() if title_elem else "Unknown Position"

            # Description
            desc_elem = soup.find("div", class_="description") or soup.find("div", {"id": "job-description"})
            description = desc_elem.text.strip() if desc_elem else ""

            # Requirements
            req_elem = soup.find("div", class_="requirements") or soup.find("div", {"id": "requirements"})
            requirements = req_elem.text.strip() if req_elem else ""

            # Location
            location_elem = soup.find("span", class_="location") or soup.find("div", class_="location")
            location = location_elem.text.strip() if location_elem else "Remote"

            # Company logo
            logo_elem = soup.find("img", class_="company-logo") or soup.find("img", alt=company_name)
            company_logo_url = logo_elem.get("src") if logo_elem else None
            if company_logo_url and not company_logo_url.startswith("http"):
                company_logo_url = f"{self.base_url}{company_logo_url}"

            # Categorize job
            job_category = self.categorize_job(job_title, description)

            # Determine sector
            sector = self.determine_sector(company_name, description)

            # Detect ATS platform
            application_platform = self.detect_ats_platform(url, html)

            # Application URL
            apply_elem = soup.find("a", class_="apply") or soup.find("button", class_="apply")
            if apply_elem:
                application_url = apply_elem.get("href", url)
                if not application_url.startswith("http"):
                    application_url = f"{self.base_url}{application_url}"
            else:
                application_url = url

            # Build job data
            job_data = {
                "source_url": url,
                "vc_firm": self.vc_firm_name,
                "company_name": company_name,
                "company_logo_url": company_logo_url,
                "job_title": job_title,
                "description": description[:5000],
                "requirements": requirements[:2000],
                "job_category": job_category,
                "sector": sector,
                "location": location,
                "date_posted": None,
                "application_url": application_url,
                "application_platform": application_platform,
                "custom_questions": None,
            }

            return job_data

        except Exception as e:
            print(f"Error scraping YC job at {url}: {e}")
            return None


# Alternative approach: If the site uses an API
class YCombinatorAPIScraper(BaseScraper):
    """
    Alternative scraper that uses YC's API if available

    Some job boards expose JSON APIs that are easier to parse than HTML
    """

    def __init__(self):
        super().__init__("Y Combinator")
        # This is a hypothetical API endpoint - needs investigation
        self.api_url = "https://www.workatastartup.com/api/jobs"

    async def get_jobs_from_api(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """
        Fetch jobs directly from API if available
        """
        try:
            async with session.get(self.api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_api_response(data)
        except Exception as e:
            print(f"Error fetching from YC API: {e}")

        return []

    def parse_api_response(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse JSON response into job data dicts
        """
        jobs = []

        # This structure depends on the actual API response
        # Adjust based on what the API returns
        if isinstance(data, list):
            job_list = data
        elif isinstance(data, dict) and "jobs" in data:
            job_list = data["jobs"]
        else:
            return jobs

        for item in job_list:
            try:
                job_data = {
                    "source_url": item.get("url", ""),
                    "vc_firm": self.vc_firm_name,
                    "company_name": item.get("company", {}).get("name", "Unknown"),
                    "company_logo_url": item.get("company", {}).get("logo_url"),
                    "job_title": item.get("title", "Unknown Position"),
                    "description": item.get("description", "")[:5000],
                    "requirements": item.get("requirements", "")[:2000],
                    "job_category": self.categorize_job(
                        item.get("title", ""),
                        item.get("description", "")
                    ),
                    "sector": self.determine_sector(
                        item.get("company", {}).get("name", ""),
                        item.get("description", "")
                    ),
                    "location": item.get("location", "Remote"),
                    "date_posted": item.get("posted_date"),
                    "application_url": item.get("apply_url", item.get("url", "")),
                    "application_platform": "Y Combinator",
                    "custom_questions": None,
                }
                jobs.append(job_data)
            except Exception as e:
                print(f"Error parsing job item: {e}")
                continue

        return jobs

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """Not needed for API approach"""
        return []

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Not needed for API approach"""
        return None
