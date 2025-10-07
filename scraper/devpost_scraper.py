import requests
import json
from datetime import datetime, UTC
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.database import SessionLocal, Hackathon, init_db


class DevpostScraper:
    def __init__(self):
        self.api_url = "https://devpost.com/api/hackathons"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_hackathons(self):
        """Scrape hackathons from Devpost API"""
        print(f"Fetching hackathons from API: {self.api_url}")

        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            hackathons = data.get("hackathons", [])

            print(f"Found {len(hackathons)} hackathons")

            parsed_hackathons = []
            for hackathon in hackathons:
                try:
                    parsed_data = self._parse_hackathon_json(hackathon)
                    if parsed_data:
                        parsed_hackathons.append(parsed_data)
                except Exception as e:
                    print(f"Error parsing hackathon: {e}")
                    continue

            return parsed_hackathons

        except requests.RequestException as e:
            print(f"Error fetching from API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return []

    def _parse_hackathon_json(self, hack_json):
        """Parse individual hackathon data from API JSON object"""
        data = {}

        # Essential fields
        data["title"] = hack_json.get("title", "").strip()
        data["url"] = hack_json.get("url", "")

        if not data["title"] or not data["url"]:
            return None

        # Basic info
        data["tagline"] = hack_json.get("analytics_identifier", "")
        data["status"] = hack_json.get("open_state", "unknown").lower()

        # Location
        displayed_location = hack_json.get("displayed_location", {})
        if isinstance(displayed_location, dict):
            data["location"] = displayed_location.get("location", "Not specified")
        else:
            data["location"] = "Not specified"

        # Dates
        data["submission_deadline"] = hack_json.get("submission_period_dates", "")
        data["start_date"] = None  # Not directly available in API
        data["end_date"] = None  # Not directly available in API

        # Prize information
        prize_amount = hack_json.get("prize_amount", "")
        if prize_amount:
            prize_amount = prize_amount.replace(
                "<span data-currency-value>", ""
            ).replace("</span>", "")
            data["prizes"] = {"total": prize_amount}
        else:
            data["prizes"] = {}

        # Participants
        data["participants_count"] = hack_json.get("registrations_count", 0)

        # Organizer
        data["organizer"] = hack_json.get("organization_name", "")

        # Tags/themes
        themes = hack_json.get("themes", [])
        if isinstance(themes, list):
            data["tags"] = [
                theme.get("name", "")
                for theme in themes
                if isinstance(theme, dict) and theme.get("name")
            ]
        else:
            data["tags"] = []

        # Additional fields
        data["visibility"] = (
            "invite_only" if hack_json.get("invite_only", False) else "public"
        )
        data["description"] = ""  # Not available in listing API
        data["requirements"] = hack_json.get(
            "eligibility_requirement_invite_only_description", ""
        )

        # Additional API-specific fields
        data["featured"] = hack_json.get("featured", False)
        data["winners_announced"] = hack_json.get("winners_announced", False)
        data["thumbnail_url"] = hack_json.get("thumbnail_url", "")
        data["submission_gallery_url"] = hack_json.get("submission_gallery_url", "")
        data["time_left"] = hack_json.get("time_left_to_submission", "")

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
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.now(UTC)
                    updated_count += 1
                else:
                    # Create new record
                    hackathon_kwargs = {
                        "url": hack_data.get("url"),
                        "title": hack_data.get("title"),
                        "tagline": hack_data.get("tagline"),
                        "status": hack_data.get("status"),
                        "location": hack_data.get("location"),
                        "participants_count": hack_data.get("participants_count", 0),
                        "organizer": hack_data.get("organizer"),
                        "tags": hack_data.get("tags", []),
                        "scraped_at": datetime.now(UTC),
                    }

                    # Add optional fields if they exist in the model and data
                    optional_fields = [
                        "start_date",
                        "end_date",
                        "submission_deadline",
                        "visibility",
                        "prizes",
                        "description",
                        "requirements",
                    ]
                    for field in optional_fields:
                        if hack_data.get(field) is not None:
                            hackathon_kwargs[field] = hack_data.get(field)

                    hackathon = Hackathon(**hackathon_kwargs)
                    db.add(hackathon)
                    saved_count += 1

            db.commit()
            print(f"\nDatabase operation completed:")
            print(f"  - Saved {saved_count} new hackathons")
            print(f"  - Updated {updated_count} existing hackathons")

        except Exception as e:
            print(f"Error saving to database: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def print_sample_data(self, hackathons, count=3):
        """Print sample hackathon data for verification"""
        print(f"\nSample data from {len(hackathons)} hackathons:")
        print("-" * 50)

        for i, hack in enumerate(hackathons[:count]):
            print(f"\n{i + 1}. {hack.get('title')}")
            print(f"   URL: {hack.get('url')}")
            print(f"   Status: {hack.get('status')}")
            print(f"   Location: {hack.get('location')}")
            print(f"   Organizer: {hack.get('organizer')}")
            print(f"   Participants: {hack.get('participants_count')}")
            print(f"   Prize: {hack.get('prizes', {}).get('total', 'N/A')}")
            print(f"   Themes: {', '.join(hack.get('tags', []))}")
            print(f"   Time left: {hack.get('time_left', 'N/A')}")


def main():
    """Main execution function"""
    print("Starting Devpost API scraper...")
    print("=" * 50)

    # Initialize database
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return

    # Create scraper and fetch data
    scraper = DevpostScraper()
    hackathons = scraper.scrape_hackathons()

    if hackathons:
        print(f"\nSuccessfully scraped {len(hackathons)} hackathons from API")

        # Print sample data
        scraper.print_sample_data(hackathons)

        # Save to database
        print(f"\nSaving hackathons to database...")
        try:
            scraper.save_to_database(hackathons)
            print("Scraping completed successfully!")
        except Exception as e:
            print(f"Failed to save to database: {e}")
    else:
        print("No hackathons found or error occurred during scraping")


if __name__ == "__main__":
    main()
