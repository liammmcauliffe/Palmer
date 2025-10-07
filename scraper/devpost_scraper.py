import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.database import SessionLocal, Hackathon, init_db


class DevpostScraper:
    def __init__(self):
        self.base_url = "https://devpost.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_listing_page(self, url="https://devpost.com/hackathons"):
        """Scrape the main hackathon listing page"""
        print(f"Scraping: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            hackathon_tiles = soup.find_all("div", class_="challenge-listing")

            if not hackathon_tiles:
                print("No hackathon tiles found.")
                return []

            hackathons = []
            print(f"Found {len(hackathon_tiles)} hackathons")

            for tile in hackathon_tiles:
                try:
                    hackathon_data = self._parse_hackathon_tile(tile)
                    if hackathon_data:
                        hackathons.append(hackathon_data)
                except Exception as e:
                    print(f"Error parsing tile: {e}")
                    continue

            return hackathons

        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return []

    def _parse_hackathon_tile(self, tile):
        """Parse individual hackathon tile from listing page"""
        data = {}

        # Get title and URL
        title_elem = tile.find("a", class_="challenge-link-overlay")
        if title_elem:
            data["title"] = title_elem.get("aria-label", "").strip()
            data["url"] = self.base_url + title_elem.get("href", "")
        else:
            return None

        # Get tagline/description
        tagline_elem = tile.find("p", class_="challenge-tagline")
        if tagline_elem:
            data["tagline"] = tagline_elem.text.strip()

        # Get status (from status badge)
        status_elem = tile.find("span", class_="submission-period")
        if status_elem:
            data["status"] = status_elem.text.strip().lower()
        else:
            data["status"] = "unknown"

        # Get location
        location_elem = tile.find("div", class_="challenge-location")
        if location_elem:
            data["location"] = location_elem.text.strip()
        else:
            data["location"] = "Not specified"

        # Get dates
        date_elem = tile.find("div", class_="challenge-date")
        if date_elem:
            data["dates"] = date_elem.text.strip()

        # Get prize amount
        prize_elem = tile.find("div", class_="prize-amount")
        if prize_elem:
            data["prize_info"] = prize_elem.text.strip()

        # Get participant count
        participants_elem = tile.find("div", class_="participants-count")
        if participants_elem:
            try:
                count_text = participants_elem.text.strip()
                data["participants_count"] = int(
                    "".join(filter(str.isdigit, count_text))
                )
            except:
                data["participants_count"] = 0

        # Get themes/tags
        theme_elems = tile.find_all("span", class_="challenge-theme")
        if theme_elems:
            data["tags"] = [theme.text.strip() for theme in theme_elems]

        # Get organizer
        organizer_elem = tile.find("div", class_="challenge-organizer")
        if organizer_elem:
            data["organizer"] = organizer_elem.text.strip()

        return data

    def save_to_database(self, hackathons):
        """Save scraped hackathons to database"""
        db = SessionLocal()
        saved_count = 0
        updated_count = 0

        try:
            for hack_data in hackathons:
                # Check if hackathon already exists
                existing = (
                    db.query(Hackathon).filter_by(url=hack_data.get("url")).first()
                )

                if existing:
                    # Update existing record
                    for key, value in hack_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    hackathon = Hackathon(
                        url=hack_data.get("url"),
                        title=hack_data.get("title"),
                        tagline=hack_data.get("tagline"),
                        status=hack_data.get("status"),
                        location=hack_data.get("location"),
                        participants_count=hack_data.get("participants_count", 0),
                        organizer=hack_data.get("organizer"),
                        tags=hack_data.get("tags", []),
                        scraped_at=datetime.utcnow(),
                    )
                    db.add(hackathon)
                    saved_count += 1

            db.commit()
            print(f"\n Saved {saved_count} new hackathons, updated {updated_count}")

        except Exception as e:
            print(f"Error saving to database: {e}")
            db.rollback()
        finally:
            db.close()


def main():
    """Main execution function"""
    print("Starting Devpost scraper...")

    # Initialize database
    init_db()

    # Create scraper and run
    scraper = DevpostScraper()
    hackathons = scraper.scrape_listing_page()

    if hackathons:
        print(f"\nScraped {len(hackathons)} hackathons")

        # Print sample
        print("\nSample data:")
        for hack in hackathons[:3]:
            print(f"\n  Title: {hack.get('title')}")
            print(f"  URL: {hack.get('url')}")
            print(f"  Status: {hack.get('status')}")
            print(f"  Location: {hack.get('location')}")

        # Save to database
        print("\nSaving to database...")
        scraper.save_to_database(hackathons)
    else:
        print("No hackathons scraped")


if __name__ == "__main__":
    main()
