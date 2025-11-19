# MoMA Web Scraper

A Python-based web scraper designed to collect calendar data from the Museum of Modern Art (MoMA) website across three content categories: Films, Galleries, and Exhibitions.

## Project Overview

This scraper systematically collects data from MoMA's calendar pages, extracting 37 different fields including titles, dates, locations, artist information, sponsors, promotional content, media, and related events. The project includes automatic resumption capabilities and progress tracking to support long-running scraping sessions.

**Target URLs:**
- Films: `https://www.moma.org/calendar/film/{ID}`
- Galleries: `https://www.moma.org/calendar/galleries/{ID}`
- Exhibitions: `https://www.moma.org/calendar/exhibitions/{ID}`

**Scraping Range:** IDs 1-8000 (24,000 total URLs across 3 categories)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

The project requires three main packages:
- `cloudscraper>=1.2.71` - Bypasses Cloudflare protection
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - Fast XML/HTML processing

## Configuration Settings

### MoMAScraper Class Configuration

The scraper can be configured by modifying parameters in the `MoMAScraper` class:

```python
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',      # Browser to emulate
        'platform': 'windows',    # Platform to emulate
        'mobile': False           # Mobile vs desktop
    }
)
```

### Scraping Parameters

All scraping functions accept the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | int | 1 | Starting ID number for scraping |
| `end` | int | 8000 | Ending ID number for scraping |
| `delay` | float | 0.5 | Delay between requests in seconds |

**Examples:**
```python
# Scrape IDs 1-1000 with 0.5 second delay
scrape_all(start=1, end=1000, delay=0.5)

# Scrape IDs 5000-6000 with 1 second delay (more respectful)
scrape_all(start=5000, end=6000, delay=1.0)

# Quick scrape with minimal delay (use cautiously)
scrape_all(start=1, end=100, delay=0.1)
```

### Request Configuration

Built-in request settings:
- **Timeout:** 30 seconds per request
- **Encoding:** UTF-8
- **User Agent:** Chrome on Windows (via cloudscraper)

## How to Run

### Option 1: Main Scraper (First Time)

Run the main scraper to start collecting data:

```bash
python moma_scraper.py
```

**Default behavior:**
- Scrapes IDs 5780 to 8000
- Uses 0.1 second delay between requests
- Creates/appends to `main.csv`

**To customize the range, edit `moma_scraper.py`:**
```python
if __name__ == "__main__":
    scraper = MoMAScraper()
    scraper.scrape_all(start=1, end=8000, delay=0.5)  # Modify these values
```

### Option 2: Test Scraper (Recommended First)

Test the scraper on sample URLs before running a full scrape:

```bash
python test_scraper.py
```

**What it does:**
- Tests 6 sample URLs to verify scraper functionality
- Checks if HTML structure has changed
- Saves results to `main.csv`
- Useful for validating your setup

**Sample test URLs:**
- Film: 6958, 6871
- Galleries: 6954, 6966
- Exhibitions: 6940, 6961

### Option 3: Resume Scraper (Continue Interrupted Scrapes)

Resume or continue an interrupted scraping session:

```bash
python resume_scrape.py
```

**Features:**
- Automatically detects already-scraped URLs in `main.csv`
- Skips completed pages to avoid duplicates
- Scrapes only missing IDs from 1 to 8000
- Uses 0.5 second delay (more conservative)

**How it works:**
1. Loads existing `main.csv`
2. Extracts all previously scraped URLs
3. Identifies missing IDs in the range
4. Continues scraping from where you left off

## Output Format

### CSV Structure

Data is saved to `main.csv` with the following characteristics:
- **Encoding:** UTF-8
- **Delimiter:** Comma (`,`)
- **Multi-value delimiter:** Pipe (`|`)
- **Array fields:** JSON formatted

### Extracted Fields (37 total)

| Category | Fields |
|----------|--------|
| **Basic Info** | url, title, date, location, type |
| **Artists** | artist_name, no_artists, artist_bio, artist_link, artist_image, artist_no_works |
| **Sponsors** | sponsor_text, no_sponsor_paragraphs |
| **Promotions** | promo_link, promo_link_data, promo_image, promo_category, promo_title, promo_description, promo_date, promo_author, no_promos |
| **Media** | video, no_videos |
| **Related** | no_pubs, event_catch_all, no_events, credits |
| **Locations** | location_tag, location_donor, location_selbst, no_locations |
| **Works** | works_online_links, no_works_online, works_online_text |
| **Other** | description, miscellaneous_third_uneven |

### Sample Output

```csv
url,title,date,location,artist_name,...
https://www.moma.org/calendar/film/6958,Modern Mondays,Dec 10–24 2025,The Roy and Niuta Titus Theater,...
```

## Progress Tracking

The scraper provides real-time progress information:

```
Starting resume scrape...
Total URLs in CSV: 5632
Already scraped: 5000
Not found (404): 500
Missing to scrape: 2500

Processing Film ID 1234...
Found page! Total new pages: 15
```

**Auto-save:** Progress is saved every 10 IDs to prevent data loss in case of interruption.

## Error Handling

The scraper gracefully handles common errors:

- **404 Errors:** Skipped (page doesn't exist)
- **Network Timeouts:** Request times out after 30 seconds
- **Cloudflare Blocks:** Handled automatically by cloudscraper
- **Malformed HTML:** Returns None and continues
- **Connection Errors:** Logged and skipped

## Best Practices

### Respectful Scraping

1. **Use appropriate delays:**
   - Development/testing: 0.1-0.5 seconds
   - Production: 0.5-1.0 seconds
   - Conservative: 1.0-2.0 seconds

2. **Monitor your scraping:**
   - Watch for error messages
   - Check if success rate drops significantly
   - Adjust delay if you encounter blocks

3. **Run during off-peak hours:**
   - Reduces load on MoMA's servers
   - Less likely to be rate-limited

### Data Management

1. **Backup regularly:**
   ```bash
   cp main.csv main_backup_$(date +%Y%m%d).csv
   ```

2. **Use resume script for interruptions:**
   - Don't restart from scratch
   - Resume script automatically detects progress

3. **Validate data periodically:**
   - Check for missing required fields
   - Verify data quality on sample rows

## Troubleshooting

### Common Issues

**Problem:** "Module not found" error
```
Solution: Activate virtual environment and reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** Scraper getting blocked
```
Solution: Increase delay parameter
scraper.scrape_all(start=1, end=8000, delay=1.0)  # Slower but safer
```

**Problem:** CSV encoding errors
```
Solution: File is already UTF-8 encoded. Use Excel's "Import Data" feature instead of double-clicking
```

**Problem:** Duplicate data in CSV
```
Solution: Use resume_scrape.py which automatically deduplicates
```

## Project Statistics

**Current Progress:**
- 5,632 pages scraped
- ~23% of potential URLs covered
- Data size: 14.6 MB

**Performance:**
- ~0.1-0.5 seconds per request
- ~7,200-36,000 requests per hour (with delay)
- Estimated time for full scrape: 7-35 hours

## File Structure

```
web_scrape/
├── moma_scraper.py       # Main scraper script
├── test_scraper.py       # Testing utility
├── resume_scrape.py      # Resume/continuation script
├── requirements.txt      # Python dependencies
├── main.csv             # Output data (generated)
├── venv/                # Virtual environment (generated)
└── README.md            # This file
```

## License

This project is for educational and research purposes. Please respect MoMA's terms of service and robots.txt when using this scraper.

## Contributing

To modify the scraper:

1. Test changes with `test_scraper.py` first
2. Use small ID ranges for testing
3. Check output data quality in `main.csv`
4. Update this README if adding new features

## Support

For issues or questions:
- Check the troubleshooting section above
- Review code comments in `moma_scraper.py`
- Verify HTML structure hasn't changed at target URLs
