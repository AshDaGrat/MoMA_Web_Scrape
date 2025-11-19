"""
Test script to verify the scraper works on a few sample URLs
before running the full scrape
"""
from moma_scraper import MoMAScraper

def test_scraper():
    scraper = MoMAScraper()

    # Test URLs
    test_urls = [
        ('film', 'https://www.moma.org/calendar/film/1'),
        ('film', 'https://www.moma.org/calendar/film/100'),
        ('galleries', 'https://www.moma.org/calendar/galleries/1'),
        ('galleries', 'https://www.moma.org/calendar/galleries/50'),
        ('exhibitions', 'https://www.moma.org/calendar/exhibitions/1'),
        ('exhibitions', 'https://www.moma.org/calendar/exhibitions/75'),
    ]

    print("Testing scraper on sample URLs...\n")

    results = []
    for page_type, url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)

        data = scraper.scrape_page(url, page_type)

        if data:
            print(f"✓ Successfully scraped!")
            print(f"  Title: {data['title']}")
            print(f"  Date: {data['date']}")
            print(f"  Location: {data['location']}")
            print(f"  Artists: {data['artist_name']}")
            print(f"  No. of Artists: {data['no_artists']}")
            print(f"  Description (first 100 chars): {data['description'][:100]}...")
            results.append(data)
        else:
            print(f"✗ Failed to scrape (page may not exist)")

    if results:
        print(f"\n{'='*60}")
        print(f"Test complete! Successfully scraped {len(results)}/{len(test_urls)} pages")
        print('='*60)

        # Save test results
        scraper.save_to_csv(results)
        print("\nTest results saved to main.csv")

        print("\nYou can now run the full scraper with:")
        print("  python moma_scraper.py")
        print("\nOr adjust the range in moma_scraper.py if needed.")
    else:
        print("\n" + "="*60)
        print("WARNING: No pages were successfully scraped!")
        print("="*60)
        print("\nThis could mean:")
        print("1. The website is blocking requests (try adjusting headers)")
        print("2. The HTML structure has changed (need to update selectors)")
        print("3. Network connectivity issues")
        print("\nPlease check the error messages above for details.")

if __name__ == '__main__':
    test_scraper()
