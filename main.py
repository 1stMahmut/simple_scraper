#!/usr/bin/env python3
"""
Profile Scraper → Airtable

Usage:
    python main.py --username elonmusk
    python main.py --username alexrivera --demo
    python main.py --username alexrivera --headed
"""

import argparse
import logging
import os
from dataclasses import asdict

from twitter_scraper import TwitterScraper
from airtable_sender import AirtableSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape a public Twitter/X profile and push the data to Airtable."
    )
    parser.add_argument("--username", "-u", required=True,
                        help="Twitter/X username (with or without @)")
    parser.add_argument("--demo", action="store_true",
                        help="Skip live scraping, use demo data")
    parser.add_argument("--headed", action="store_true",
                        help="Run browser in visible mode (useful for debugging)")
    return parser.parse_args()


def main():
    args = parse_args()
    username = args.username.lstrip("@")

    print(f"\n{'='*50}")
    print(f"  Scraping @{username}")
    print(f"{'='*50}\n")

    # ── Scrape ────────────────────────────────────────
    scraper = TwitterScraper(headless=not args.headed)

    if args.demo:
        logger.info("Demo mode: using synthetic data.")
        profile = scraper._demo_profile(username)
    else:
        logger.info("Scraping live profile...")
        profile = scraper.scrape(username)

    profile_dict = asdict(profile)

    print(f"Scraped: {profile.display_name} (@{profile.username})")
    print(f"  Followers: {profile.followers:,}  |  Following: {profile.following:,}")
    print(f"  Tweets captured: {len(profile.recent_tweets)}\n")

    # ── Send to Airtable ──────────────────────────────
    sender = AirtableSender()
    result = sender.send(profile_dict)

    print(f"Sent to Airtable — record ID: {result.get('id')}")
    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    main()
