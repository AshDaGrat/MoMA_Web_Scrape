#!/usr/bin/env python3
"""
Resume scraping script - automatically detects and scrapes only missing URLs
"""
from moma_scraper import MoMAScraper

if __name__ == '__main__':
    scraper = MoMAScraper()

    print("="*60)
    print("MoMA Web Scraper - Resume Mode")
    print("="*60)
    print("\nThis script will:")
    print("  1. Load existing data from main.csv")
    print("  2. Identify which IDs are missing")
    print("  3. Scrape ONLY the missing IDs")
    print("  4. Keep a running total of NEW pages scraped")
    print("  5. Save progress every 10 IDs")
    print("\n")

    # You can adjust these parameters:
    # - start: starting ID number (default: 1)
    # - end: ending ID number (default: 8000)
    # - delay: delay between requests in seconds (default: 0.5)

    scraper.scrape_all(start=1, end=8000, delay=0.5)
