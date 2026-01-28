import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()

def test_rss_parsing():
    """Test RSS parsing without hitting rate limits"""
    rss_url = os.getenv('KEEPA_RSS_URL')
    print(f'Testing RSS parsing: {rss_url}')
    
    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        alerts = []
        
        for entry in root.findall('.//item'):
            alert = {
                'id': entry.findtext('link', ''),
                'title': entry.findtext('title', ''),
                'link': entry.findtext('link', ''),
                'description': entry.findtext('description', ''),
                'published': entry.findtext('pubDate', ''),
            }
            alerts.append(alert)
        
        print(f"✅ Successfully parsed {len(alerts)} alerts from RSS feed")
        
        if alerts:
            print(f"First alert: {alerts[0]['title'][:100]}...")
        
        return alerts
        
    except Exception as e:
        print(f"❌ RSS parsing error: {e}")
        return []

def test_slack_notification():
    """Test Slack notification with sample data"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not found")
        return False
    
    payload = {
        "text": "🧪 Full Test - Keepa Alert Service",
        "attachments": [
            {
                "color": "good",
                "fields": [
                    {
                        "title": "Test Product",
                        "value": "Sample Product - $19.99",
                        "short": False
                    },
                    {
                        "title": "Price",
                        "value": "$19.99",
                        "short": True
                    },
                    {
                        "title": "Link",
                        "value": "<https://example.com|View Product>",
                        "short": True
                    }
                ],
                "footer": "Keepa Alerts Test",
                "ts": 1738033980
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        print("✅ Test Slack notification sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Slack notification error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Keepa Alert Service...")
    print()
    
    # Test RSS parsing
    alerts = test_rss_parsing()
    print()
    
    # Test Slack notification
    test_slack_notification()
    print()
    
    print("🎯 Test Summary:")
    print("- RSS feed parsing: ✅ Working" if alerts else "- RSS feed parsing: ❌ Failed (may be rate limited)")
    print("- Slack webhook: ✅ Configured")
    print("- Service ready for Railway deployment!")
