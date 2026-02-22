#!/usr/bin/env python3
"""
Get top news headlines from free RSS feeds
No API key needed
"""
import subprocess
import xml.etree.ElementTree as ET
import sys

def get_rss_headlines(url, count=3):
    """Fetch and parse RSS feed"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0', url, '--max-time', '10'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0 or not result.stdout:
            return []
        
        # Parse XML
        root = ET.fromstring(result.stdout)
        
        headlines = []
        # Try RSS 2.0 format
        for item in root.findall('.//item')[:count]:
            title = item.find('title')
            if title is not None and title.text:
                headlines.append(title.text.strip())
        
        # Try Atom format if RSS didn't work
        if not headlines:
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:count]:
                title = entry.find('{http://www.w3.org/2005/Atom}title')
                if title is not None and title.text:
                    headlines.append(title.text.strip())
        
        return headlines
        
    except Exception as e:
        return []

def main():
    """Get top headlines from multiple sources"""
    
    print("🇨🇦 CANADA NEWS - TOP 3\n")
    
    # CBC News
    cbc = get_rss_headlines('https://www.cbc.ca/webfeed/rss/rss-topstories', 3)
    if cbc:
        for i, headline in enumerate(cbc, 1):
            print(f"   {i}. {headline}")
    else:
        print("   • Unable to fetch Canadian headlines")
    
    print()
    print("🇺🇸 USA NEWS - TOP 3\n")
    
    # Try multiple US sources
    us_feeds = [
        'https://feeds.nbcnews.com/nbcnews/public/news',
        'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'https://feeds.washingtonpost.com/rss/national',
    ]
    
    headlines = []
    for feed in us_feeds:
        headlines = get_rss_headlines(feed, 3)
        if headlines:
            break
    
    if headlines:
        for i, headline in enumerate(headlines, 1):
            print(f"   {i}. {headline}")
    else:
        print("   • Unable to fetch US headlines")
        print("   Manual check: https://www.reuters.com or https://apnews.com")

if __name__ == "__main__":
    main()
