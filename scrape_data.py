#!/usr/bin/env python
# Script to scrape vehicle registration data from public sources

from data_scraper import VehicleDataScraper
import sys

def main():
    print("Starting data scraping process...")
    try:
        scraper = VehicleDataScraper()
        data_file = scraper.scrape_and_save_data()
        print(f"\nData scraping completed successfully!")
        print(f"Data saved to: {data_file}")
        return 0
    except Exception as e:
        print(f"\nError during data scraping: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())