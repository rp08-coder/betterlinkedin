"""
Example scraper implementation (template for VC firm scrapers)

This is a template showing how to implement a scraper for a specific VC firm.
Actual implementation will vary based on the website structure.
"""

from typing import List, Dict, Any, Optional
import aiohttp
from datetime import datetime

from app.scrapers.base_scraper import BaseScraper


class ExampleVCScraper(BaseScraper):
    """
    Example VC firm job scraper

    Implementation notes:
    1. Override get_portfolio_companies() to extract job URLs from VC's portfolio page
    2. Override scrape_job() to extract job details from individual job pages
    3. Use the inherited utility methods for categorization and ATS detection
    """

    def __init__(self):
        super().__init__("Example VC Firm")
        self.portfolio_url = "https://example-vc.com/portfolio/jobs"

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of job URLs from the VC's portfolio page

        Example implementation for a hypothetical portfolio page
        """
        html = await self.fetch_page(self.portfolio_url, session)
        soup = self.parse_html(html)

        job_urls = []

        # Example: Find all job links
        # Actual implementation depends on website structure
        job_links = soup.find_all("a", class_="job-link")
        for link in job_links:
            href = link.get("href")
            if href:
                # Make absolute URL if needed
                if href.startswith("/"):
                    href = f"https://example-vc.com{href}"
                job_urls.append(href)

        return job_urls

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape details from a single job posting

        Returns job data dict matching the Job model schema
        """
        try:
            html = await self.fetch_page(url, session)
            soup = self.parse_html(html)

            # Extract job details
            # Actual selectors depend on website structure

            # Example extraction (adjust selectors based on actual HTML)
            company_name = soup.find("h2", class_="company-name")
            company_name = company_name.text.strip() if company_name else "Unknown Company"

            job_title = soup.find("h1", class_="job-title")
            job_title = job_title.text.strip() if job_title else "Unknown Position"

            description_elem = soup.find("div", class_="job-description")
            description = description_elem.text.strip() if description_elem else ""

            requirements_elem = soup.find("div", class_="job-requirements")
            requirements = requirements_elem.text.strip() if requirements_elem else ""

            location_elem = soup.find("span", class_="location")
            location = location_elem.text.strip() if location_elem else "Remote"

            # Get company logo if available
            logo_elem = soup.find("img", class_="company-logo")
            company_logo_url = logo_elem.get("src") if logo_elem else None

            # Categorize the job
            job_category = self.categorize_job(job_title, description)
            sector = self.determine_sector(company_name, description)

            # Detect ATS platform
            application_platform = self.detect_ats_platform(url, html)

            # Find application URL
            apply_button = soup.find("a", class_="apply-button")
            application_url = apply_button.get("href") if apply_button else url

            # Build job data dict
            job_data = {
                "source_url": url,
                "vc_firm": self.vc_firm_name,
                "company_name": company_name,
                "company_logo_url": company_logo_url,
                "job_title": job_title,
                "description": description[:5000],  # Limit length
                "requirements": requirements[:2000],  # Limit length
                "job_category": job_category,
                "sector": sector,
                "location": location,
                "date_posted": None,  # Extract if available on page
                "application_url": application_url,
                "application_platform": application_platform,
                "custom_questions": None,  # Parse if available
            }

            return job_data

        except Exception as e:
            print(f"Error scraping job at {url}: {e}")
            return None


# TODO: Implement scrapers for each VC firm:
# - SequoiaCapitalScraper
# - AndreessenHorowitzScraper
# - KleinerPerkinsScraper
# - IndexVenturesScraper
# - KhoslaScraper
# - FirstRoundScraper
# - BessemerScraper
# - IVPScraper
# - GreylockScraper
# - AccelScraper
