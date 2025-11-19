import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
from typing import Dict, Optional
import json

class MoMAScraper:
    def __init__(self):
        # Use cloudscraper instead of requests to bypass Cloudflare
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object, or None if page doesn't exist"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            elif response.status_code == 404:
                print(f"Page not found: {url}")
                return None
            else:
                print(f"Error {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"Request failed for {url}: {str(e)}")
            return None

    def extract_text_safe(self, soup, selector: str, attribute: str = None) -> str:
        """Safely extract text from a selector"""
        try:
            element = soup.select_one(selector)
            if element:
                if attribute:
                    return element.get(attribute, '').strip()
                return element.get_text(strip=True)
            return ''
        except:
            return ''

    def extract_multiple(self, soup, selector: str) -> list:
        """Extract multiple elements matching selector"""
        try:
            elements = soup.select(selector)
            return [elem.get_text(strip=True) for elem in elements]
        except:
            return []

    def count_elements(self, soup, selector: str) -> int:
        """Count elements matching selector"""
        try:
            return len(soup.select(selector))
        except:
            return 0

    def scrape_page(self, url: str, page_type: str) -> Dict:
        """Scrape a single page and return structured data"""
        soup = self.fetch_page(url)

        if soup is None:
            return None

        data = {
            'url': url,
            'title': '',
            'date': '',
            'location': '',
            'type': page_type,
            'artist_name': '',
            'no_artists': 0,
            'artist_bio': '',
            'artist_link': '',
            'artist_image': '',
            'artist_no_works': '',
            'sponsor_text': '',
            'no_sponsor_paragraphs': 0,
            'promo_link': '',
            'no_promos': 0,
            'promo_link_data': '',
            'promo_image': '',
            'promo_category': '',
            'promo_title': '',
            'promo_description': '',
            'promo_date': '',
            'promo_author': '',
            'video': '',
            'no_videos': 0,
            'no_pubs': 0,
            'event_catch_all': '',
            'no_events': 0,
            'description': '',
            'credits': '',
            'location_tag': '',
            'location_donor': '',
            'location_selbst': '',
            'no_locations': 0,
            'miscellaneous_third_uneven': '',
            'works_online_links': '',
            'no_works_online': 0,
            'works_online_text': ''
        }

        # Extract title
        h1_tag = soup.find('h1')
        if h1_tag:
            data['title'] = h1_tag.get_text(strip=True)
        else:
            title_tag = soup.find('title')
            data['title'] = title_tag.get_text(strip=True) if title_tag else ''

        # Extract date - look for p.balance-text.typography with date format
        date_found = False
        for p in soup.find_all('p', class_='balance-text'):
            text = p.get_text(strip=True)
            # Check if it looks like a date (contains month names or numbers with commas/dashes)
            if any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']) or \
               (',' in text and any(char.isdigit() for char in text)):
                data['date'] = text
                date_found = True
                break

        if not date_found:
            # Fallback to meta tag
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content', '')
                # Try to extract date from description (format: "Exhibition. Nov 15, 2006–Mar 26, 2007.")
                if '.' in content:
                    parts = content.split('.')
                    if len(parts) > 1:
                        date_part = parts[1].strip()
                        if any(month in date_part for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                            data['date'] = date_part

        # Extract location - look for short p.typography elements containing location words
        for p in soup.find_all('p', class_='typography'):
            text = p.get_text(strip=True)
            if len(text) < 50 and ('MoMA' in text or 'Museum' in text or 'Gallery' in text or 'Floor' in text):
                data['location'] = text
                break

        # Extract artists - look for artist links with proper structure
        artist_links = []
        artist_names = []
        artist_bios = []
        artist_works_info = []

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/artists/' in href and href != '/artists/':
                # Try to find artist name in the structured span
                name_span = link.find('span', class_='artist-term--in-list__title__text')
                if name_span:
                    artist_name = name_span.get_text(strip=True)

                    # Get bio info
                    bio_span = link.find('span', class_='artist-term--in-list__info__text')
                    bio = bio_span.get_text(strip=True) if bio_span else ''

                    # Get works count info
                    count_span = link.find('span', class_='artist-term--in-list__count__text')
                    works_info = count_span.get_text(strip=True) if count_span else ''

                    artist_names.append(artist_name)
                    artist_links.append(href)
                    artist_bios.append(bio)
                    artist_works_info.append(works_info)
                else:
                    # Fallback: just get the text if no structured span found
                    text = link.get_text(strip=True)
                    # Exclude generic "Artists" links and very long descriptions
                    if text and text.lower() != 'artists' and len(text) < 200:
                        # Try to be smart about what looks like an artist name vs description
                        # If it doesn't have common non-name phrases, include it
                        if not any(phrase in text.lower() for phrase in
                                 ['view all', 'see more', 'back to', 'learn more', 'read more']):
                            artist_names.append(text)
                            artist_links.append(href)
                            artist_bios.append('')
                            artist_works_info.append('')

        # Remove duplicates while preserving order
        seen = set()
        unique_artists = []
        unique_links = []
        unique_bios = []
        unique_works = []

        for name, link, bio, works in zip(artist_names, artist_links, artist_bios, artist_works_info):
            if name not in seen:
                seen.add(name)
                unique_artists.append(name)
                unique_links.append(link)
                unique_bios.append(bio)
                unique_works.append(works)

        data['artist_name'] = '|'.join(unique_artists) if unique_artists else ''
        data['artist_link'] = '|'.join(unique_links) if unique_links else ''
        data['no_artists'] = len(unique_artists)

        # Store bio and works info
        if unique_bios and any(unique_bios):
            data['artist_bio'] = '|'.join(unique_bios)
        if unique_works and any(unique_works):
            data['artist_no_works'] = '|'.join(unique_works)

        # Extract description - prefer meta tags as they have clean text
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            data['description'] = meta_desc.get('content', '')
        else:
            # Fallback to article content
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                data['description'] = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        # Extract additional artist bio if available (more detailed than the list bio)
        bio_elem = soup.find(class_='artist-bio') or soup.find(class_='bio')
        if bio_elem:
            detailed_bio = bio_elem.get_text(strip=True)
            # If we already have bio from artist list, append; otherwise use this
            if data['artist_bio']:
                data['artist_bio'] = data['artist_bio'] + ' | ' + detailed_bio
            else:
                data['artist_bio'] = detailed_bio

        # Extract artist image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            data['artist_image'] = og_image.get('content', '')

        # Extract credits
        data['credits'] = self.extract_text_safe(soup, '.credits') or \
                         self.extract_text_safe(soup, '.event-detail__credits')

        # Extract sponsor information
        sponsors = self.extract_multiple(soup, '.sponsor') or \
                  self.extract_multiple(soup, '.event-detail__sponsor')
        data['sponsor_text'] = '|'.join(sponsors) if sponsors else ''
        data['no_sponsor_paragraphs'] = len(sponsors)

        # Extract promos
        promos = soup.select('.promo') or soup.select('.related-content')
        data['no_promos'] = len(promos)

        if promos:
            promo_data = []
            for promo in promos:
                promo_dict = {
                    'title': self.extract_text_safe(promo, '.promo__title'),
                    'description': self.extract_text_safe(promo, '.promo__description'),
                    'link': self.extract_text_safe(promo, 'a', 'href'),
                    'category': self.extract_text_safe(promo, '.promo__category'),
                    'date': self.extract_text_safe(promo, '.promo__date'),
                    'author': self.extract_text_safe(promo, '.promo__author'),
                    'image': self.extract_text_safe(promo, 'img', 'src')
                }
                promo_data.append(promo_dict)

            if promo_data:
                data['promo_title'] = '|'.join([p['title'] for p in promo_data])
                data['promo_description'] = '|'.join([p['description'] for p in promo_data])
                data['promo_link'] = '|'.join([p['link'] for p in promo_data])
                data['promo_category'] = '|'.join([p['category'] for p in promo_data])
                data['promo_date'] = '|'.join([p['date'] for p in promo_data])
                data['promo_author'] = '|'.join([p['author'] for p in promo_data])
                data['promo_image'] = '|'.join([p['image'] for p in promo_data])
                data['promo_link_data'] = json.dumps(promo_data)

        # Extract videos
        videos = soup.select('video') or soup.select('iframe[src*="youtube"]') or \
                soup.select('iframe[src*="vimeo"]')
        data['no_videos'] = len(videos)
        video_urls = []
        for video in videos:
            src = video.get('src', '')
            if src:
                video_urls.append(src)
        data['video'] = '|'.join(video_urls)

        # Extract publications
        data['no_pubs'] = self.count_elements(soup, '.publication') or \
                         self.count_elements(soup, 'a[href*="/publications/"]')

        # Extract events
        events = self.extract_multiple(soup, '.event') or \
                self.extract_multiple(soup, '.related-event')
        data['event_catch_all'] = '|'.join(events) if events else ''
        data['no_events'] = len(events)

        # Extract location details
        location_tags = self.extract_multiple(soup, '.location-tag')
        data['location_tag'] = '|'.join(location_tags) if location_tags else ''
        data['no_locations'] = len(location_tags)

        data['location_donor'] = self.extract_text_safe(soup, '.location-donor')
        data['location_selbst'] = self.extract_text_safe(soup, '.location-selbst')

        # Extract works online (for galleries/exhibitions)
        works_online = soup.select('.work-online') or soup.select('a[href*="/collection/works/"]')
        data['no_works_online'] = len(works_online)
        works_online_links = [w.get('href', '') for w in works_online if w.get('href')]
        data['works_online_links'] = '|'.join(works_online_links)
        works_online_texts = [w.get_text(strip=True) for w in works_online]
        data['works_online_text'] = '|'.join(works_online_texts)

        return data

    def scrape_all(self, start: int = 1, end: int = 8000, delay: float = 0.5):
        """Scrape all pages from start to end and save to CSV, skipping already-scraped URLs"""

        url_patterns = [
            ('film', 'https://www.moma.org/calendar/film/{}'),
            ('galleries', 'https://www.moma.org/calendar/galleries/{}'),
            ('exhibitions', 'https://www.moma.org/calendar/exhibitions/{}')
        ]

        # Read existing data if main.csv exists
        existing_data = []
        existing_urls = set()
        try:
            with open('main.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
                existing_urls = {row['url'] for row in existing_data}
                print(f"Loaded {len(existing_data)} existing rows from main.csv")
        except FileNotFoundError:
            print("main.csv not found, starting fresh")

        # Parse existing URLs to determine which IDs are already scraped
        scraped_ids = {'film': set(), 'galleries': set(), 'exhibitions': set()}
        for url in existing_urls:
            for page_type, url_pattern in url_patterns:
                pattern_base = url_pattern.format('')
                if pattern_base[:-2] in url:  # Remove the '{}' part
                    try:
                        # Extract ID from URL
                        id_num = int(url.split('/')[-1])
                        scraped_ids[page_type].add(id_num)
                    except (ValueError, IndexError):
                        pass

        # Print statistics about what's already scraped
        print("\n=== Already Scraped ===")
        for page_type in ['film', 'galleries', 'exhibitions']:
            count = len(scraped_ids[page_type])
            print(f"  {page_type}: {count} pages")

        total_already_scraped = sum(len(ids) for ids in scraped_ids.values())
        print(f"  TOTAL: {total_already_scraped} pages already in main.csv")

        # Calculate what needs to be scraped
        total_to_check = (end - start + 1) * 3  # 3 categories
        total_already_in_range = 0
        for page_type in ['film', 'galleries', 'exhibitions']:
            total_already_in_range += len([id for id in scraped_ids[page_type] if start <= id <= end])

        print(f"\n=== To Process ===")
        print(f"  ID range: {start} to {end}")
        print(f"  Total URLs to check: {total_to_check}")
        print(f"  Already scraped in this range: {total_already_in_range}")
        print(f"  Remaining to scrape: {total_to_check - total_already_in_range}")
        print()

        results = existing_data.copy()
        new_pages_scraped = 0
        new_pages_found = 0
        pages_skipped_existing = 0
        pages_not_found = 0

        for n in range(start, end + 1):
            print(f"\n--- Processing ID: {n} ---")

            for page_type, url_pattern in url_patterns:
                url = url_pattern.format(n)

                # Check if already scraped
                if n in scraped_ids[page_type]:
                    pages_skipped_existing += 1
                    print(f"⊘ Already scraped {page_type}/{n} - skipping")
                    continue

                print(f"Scraping {page_type}/{n}...")

                data = self.scrape_page(url, page_type)

                if data:
                    results.append(data)
                    new_pages_scraped += 1
                    new_pages_found += 1
                    print(f"✓ Successfully scraped {page_type}/{n} (NEW #{new_pages_found})")
                else:
                    pages_not_found += 1
                    print(f"✗ Page not found {page_type}/{n}")

                # Be respectful with requests
                time.sleep(delay)

            # Save progress every 10 IDs
            if n % 10 == 0:
                self.save_to_csv(results)
                print(f"\n=== Progress saved ===")
                print(f"  New pages scraped: {new_pages_found}")
                print(f"  Already existed: {pages_skipped_existing}")
                print(f"  Not found (404): {pages_not_found}")
                print(f"  Total in CSV: {len(results)}")

        # Final save
        self.save_to_csv(results)
        print(f"\n{'='*60}")
        print(f"=== SCRAPING COMPLETE ===")
        print(f"{'='*60}")
        print(f"  New pages successfully scraped: {new_pages_found}")
        print(f"  Pages already existed: {pages_skipped_existing}")
        print(f"  Pages not found (404): {pages_not_found}")
        print(f"  Total pages now in main.csv: {len(results)}")
        print(f"{'='*60}")

    def save_to_csv(self, data: list):
        """Save data to CSV file"""
        if not data:
            print("No data to save")
            return

        fieldnames = [
            'url', 'title', 'date', 'location', 'type', 'artist_name', 'no_artists',
            'artist_bio', 'artist_link', 'artist_image', 'artist_no_works',
            'sponsor_text', 'no_sponsor_paragraphs', 'promo_link', 'no_promos',
            'promo_link_data', 'promo_image', 'promo_category', 'promo_title',
            'promo_description', 'promo_date', 'promo_author', 'video', 'no_videos',
            'no_pubs', 'event_catch_all', 'no_events', 'description', 'credits',
            'location_tag', 'location_donor', 'location_selbst', 'no_locations',
            'miscellaneous_third_uneven', 'works_online_links', 'no_works_online',
            'works_online_text'
        ]

        with open('main.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Saved {len(data)} rows to main.csv")


if __name__ == '__main__':
    scraper = MoMAScraper()

    # You can adjust these parameters:
    # - start: starting ID number (default: 1)
    # - end: ending ID number (default: 8000)
    # - delay: delay between requests in seconds (default: 0.5)

    scraper.scrape_all(start=5780, end=8000, delay=0.1)
