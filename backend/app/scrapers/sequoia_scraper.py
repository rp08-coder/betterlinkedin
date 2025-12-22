"""
Sequoia Capital job scraper - Version 2

Scrapes jobs from Sequoia's official job board: https://jobs.sequoiacap.com/jobs/
"""

from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

from app.scrapers.base_scraper import BaseScraper


class SequoiaScraper(BaseScraper):
    """
    Sequoia Capital job scraper using their official job board
    """

    def __init__(self):
        super().__init__("Sequoia Capital")
        self.base_url = "https://jobs.sequoiacap.com"
        self.jobs_url = f"{self.base_url}/jobs"

    async def get_portfolio_companies(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Get list of job URLs from Sequoia's job board

        Returns URLs to individual job postings
        """
        job_urls = []

        try:
            # Fetch the main jobs page
            html = await self.fetch_page(self.jobs_url, session)
            soup = self.parse_html(html)

            # Look for job listing links
            # The structure will depend on how Sequoia's site is built
            # Common patterns: links with /jobs/ in href, job cards, etc.

            # Try to find all job links
            job_links = soup.find_all("a", href=True)

            for link in job_links:
                href = link.get("href", "")

                # Filter for job detail pages
                # Look for patterns like /jobs/company-name or /jobs/12345
                if "/jobs/" in href and href != "/jobs" and href != "/jobs/":
                    # Make it a full URL if it's relative
                    if href.startswith("/"):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith("http"):
                        full_url = href
                    else:
                        full_url = f"{self.base_url}/jobs/{href}"

                    # Avoid duplicates
                    if full_url not in job_urls:
                        job_urls.append(full_url)

            # Remove duplicates
            job_urls = list(set(job_urls))

            print(f"Found {len(job_urls)} job URLs from Sequoia Capital")

        except Exception as e:
            print(f"Error fetching Sequoia job board: {e}")

        return job_urls

    async def scrape_job(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """
        Scrape details from a single Sequoia job posting

        Returns job data dict matching the Job model schema
        """
        try:
            html = await self.fetch_page(url, session)
            soup = self.parse_html(html)

            # Extract company name
            # Try multiple selectors
            company_elem = (
                soup.find("h1") or
                soup.find("div", class_="company-name") or
                soup.find("span", class_="company") or
                soup.find("a", class_="company-link")
            )
            company_name = company_elem.text.strip() if company_elem else "Sequoia Portfolio Company"

            # Extract job title
            # Usually in h1 or h2
            title_elem = (
                soup.find("h2") or
                soup.find("h1", class_="job-title") or
                soup.find("div", class_="job-title")
            )
            job_title = title_elem.text.strip() if title_elem else "Position"

            # If title contains company name, try to separate them
            if " - " in job_title:
                parts = job_title.split(" - ")
                if len(parts) == 2:
                    company_name = parts[0].strip()
                    job_title = parts[1].strip()

            # Extract description
            # Look for main job description section
            desc_elem = (
                soup.find("div", class_="description") or
                soup.find("div", class_="job-description") or
                soup.find("div", {"id": "job-description"}) or
                soup.find("section", class_="content")
            )

            if desc_elem:
                description = desc_elem.get_text(separator="\n", strip=True)
            else:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all("p")
                description = "\n\n".join([p.get_text(strip=True) for p in paragraphs[:5]])

            # Extract location
            location_elem = (
                soup.find("span", class_="location") or
                soup.find("div", class_="location") or
                soup.find("p", class_="location")
            )
            location = location_elem.text.strip() if location_elem else "Remote"

            # Extract requirements (if in a separate section)
            req_elem = (
                soup.find("div", class_="requirements") or
                soup.find("div", {"id": "requirements"}) or
                soup.find("section", class_="qualifications")
            )
            requirements = req_elem.get_text(separator="\n", strip=True) if req_elem else ""

            # Get company logo if available
            logo_elem = soup.find("img", class_="company-logo") or soup.find("img", alt=company_name)
            company_logo_url = None
            if logo_elem and logo_elem.get("src"):
                logo_url = logo_elem.get("src")
                if logo_url.startswith("/"):
                    company_logo_url = f"{self.base_url}{logo_url}"
                elif logo_url.startswith("http"):
                    company_logo_url = logo_url

            # Categorize job
            job_category = self.categorize_job(job_title, description)

            # Determine sector based on company/description
            sector = self.determine_sector(company_name, description)

            # Detect ATS platform
            application_platform = self.detect_ats_platform(url, html)

            # Application URL - usually same as source URL
            apply_button = soup.find("a", class_=lambda x: x and "apply" in x.lower()) if soup else None
            if apply_button and apply_button.get("href"):
                application_url = apply_button.get("href")
                if not application_url.startswith("http"):
                    application_url = f"{self.base_url}{application_url}" if application_url.startswith("/") else url
            else:
                application_url = url

            # Build job data
            job_data = {
                "source_url": url,
                "vc_firm": self.vc_firm_name,
                "company_name": company_name,
                "company_logo_url": company_logo_url,
                "job_title": job_title,
                "description": description[:5000],  # Limit to 5000 chars
                "requirements": requirements[:2000],  # Limit to 2000 chars
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
            print(f"Error scraping Sequoia job at {url}: {e}")
            return None
