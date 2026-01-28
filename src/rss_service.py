"""RSS feed parsing service for Keepa alerts"""

import requests
import xml.etree.ElementTree as ET
import re
import logging
import sys
import os
from typing import List, Dict, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

logger = logging.getLogger(__name__)


class RSSService:
    """Service for parsing Keepa RSS feeds"""
    
    def __init__(self, rss_url: Optional[str] = None):
        self.rss_url = rss_url or Config.KEEPA_RSS_URL
    
    def parse_keepa_rss(self) -> List[Dict]:
        """Parse Keepa RSS feed and return list of alerts"""
        try:
            response = requests.get(self.rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML using ElementTree
            root = ET.fromstring(response.content)
            
            alerts = []
            
            # Find all entry items
            for entry in root.findall('.//item'):
                # Extract image URL from description or enclosure
                image_url = self._extract_image_url(entry)
                
                alert = {
                    'id': entry.findtext('link', ''),
                    'title': entry.findtext('title', ''),
                    'link': entry.findtext('link', ''),
                    'description': entry.findtext('description', ''),
                    'published': entry.findtext('pubDate', ''),
                    'price': self._extract_price_from_title(entry.findtext('title', '')),
                    'image_url': image_url
                }
                alerts.append(alert)
            
            logger.info(f"Found {len(alerts)} alerts in RSS feed")
            return alerts
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch RSS feed: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS XML: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            return []
    
    def _extract_price_from_title(self, title: str) -> str:
        """Extract price information from title"""
        # Look for price patterns like $19.99, €19.99, £19.99, etc.
        price_patterns = [
            r'[$€£]\s?\d+(?:,\d{3})*(?:\.\d{2})?',  # $19.99, €1,999.99
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s?[$€£]',  # 19.99$, 1,999.99€
            r'USD\s?\d+(?:,\d{3})*(?:\.\d{2})?',    # USD 19.99
            r'EUR\s?\d+(?:,\d{3})*(?:\.\d{2})?',    # EUR 19.99
            r'GBP\s?\d+(?:,\d{3})*(?:\.\d{2})?',    # GBP 19.99
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Price not specified"
    
    def _extract_image_url(self, entry) -> Optional[str]:
        """Extract image URL from RSS entry"""
        # Try to get image from enclosure tag (common for RSS feeds)
        enclosure = entry.find('enclosure')
        if enclosure is not None:
            url = enclosure.get('url', '')
            if url and ('jpg' in url.lower() or 'png' in url.lower() or 'jpeg' in url.lower()):
                return url
        
        # Try to get image from description (look for img tags)
        description = entry.findtext('description', '')
        if description:
            # Look for img src pattern
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description, re.IGNORECASE)
            if img_match:
                img_url = img_match.group(1)
                # Clean up URL (remove query params if needed)
                img_url = re.sub(r'\?.*$', '', img_url)
                return img_url
        
        # Try to get image from media:content or media:thumbnail
        namespaces = {'media': 'http://search.yahoo.com/mrss/'}
        media_content = entry.find('media:content', namespaces)
        if media_content is not None:
            url = media_content.get('url', '')
            if url:
                return url
        
        media_thumbnail = entry.find('media:thumbnail', namespaces)
        if media_thumbnail is not None:
            url = media_thumbnail.get('url', '')
            if url:
                return url
        
        return None
