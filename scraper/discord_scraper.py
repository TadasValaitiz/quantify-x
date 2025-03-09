import json
import time
import os
from typing import Optional, List
import requests

from dotenv import load_dotenv
from shared.discord_types import MessageType
from database.database import Database

load_dotenv()

USER_TOKEN = os.getenv("USER_TOKEN")
USER_SUPER = os.getenv("USER_SUPER")
CHANNEL_ID = os.getenv("CHANNEL_ID")


BASE_URL = "https://discord.com/api/v9"
HEADERS = {
    "Authorization": USER_TOKEN,
    "X-Super-Properties": USER_SUPER,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0",
}
OUTPUT_CSV = "messages.csv"
OUTPUT_JSON = "messages.json"
STATE_FILE = "last_state.json"

db = Database()

def save_messages(messages: List[MessageType]) -> None:
    """Save messages to database and JSON"""

    # Save to database
    for msg in messages:
        db.insert_message(msg)

    # Keep JSON as backup
    with open(OUTPUT_JSON, "a", encoding="utf-8", errors="replace") as jsonfile:
        for msg in messages:
            sanitized_msg = {
                k: (
                    v.encode("utf-8", "replace").decode("utf-8")
                    if isinstance(v, str)
                    else v
                )
                for k, v in msg.items()
            }
            json.dump(sanitized_msg, jsonfile, ensure_ascii=False)
            jsonfile.write("\n")


def save_state(before: Optional[str]) -> None:
    """Save pagination state to file"""
    with open(STATE_FILE, "w") as f:
        json.dump({"channel_id": CHANNEL_ID, "before": before}, f)


def load_state() -> Optional[str]:
    """Load pagination state from file"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            return state["before"]
    return None


def scrape_channel(pages: int = 50) -> None:
    """Scrape channel messages with pagination"""
    print(f"Scraping channel: {CHANNEL_ID}")
    before = load_state()
    print(f"Loading state: {before}")
    try:
        while pages > 0:
            params = {"limit": 50}
            if before:
                params["before"] = before
            url = f"{BASE_URL}/channels/{CHANNEL_ID}/messages?{params}"
            print(f"Scraping URL: {url}")
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
            )
            print(f"Response: {response.status_code}")

            if response.status_code != 200:
                print(f"Error {response.status_code}: {response.text}")
                save_state(before)
                break

            messages = response.json()
            if not messages:
                print("No more messages to scrape")
                break

            save_messages(messages)
            before = messages[-1]["id"]  # Get oldest message ID for next page
            pages -= 1

            print(f"Saved {len(messages)} messages. Pages remaining: {pages}")
            print(f"Total messages saved: {db.message_count()}")
            time.sleep(10)  # Basic rate limiting

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        save_state(before)
        raise

    # Clear state if successful completion
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)


def __main__():
    print("Starting Discord scraper...")
    scrape_channel()
    db.close()
    print("Scraping completed")


if __name__ == "__main__":
    __main__()
