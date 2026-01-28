"""Slack integration service"""

import requests
import logging
import sys
import os
from typing import Dict, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

logger = logging.getLogger(__name__)


class SlackService:
    """Service for sending notifications to Slack"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or Config.SLACK_WEBHOOK_URL
    
    def send_notification(self, title: str, link: str, price: str, description: str = "", image_url: str = None) -> bool:
        """Send notification to Slack"""
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return False
        
        # Build the payload with image support
        payload = {
            "text": f"🛒 Keepa Alert: {title}",
            "blocks": []
        }
        
        # Add header with product image if available
        if image_url:
            payload["blocks"].append({
                "type": "image",
                "image_url": image_url,
                "alt_text": f"Product image for {title}"
            })
        
        # Add product information
        payload["blocks"].extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🛒 {title}*"
                }
            }
        ])
        
        # Only add price section if price is specified
        if price and price != "Price not specified":
            payload["blocks"].append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*💰 Price:*\n{price}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🔗 Link:*\n<{link}|View Product>"
                    }
                ]
            })
        else:
            # Only show link if no price
            payload["blocks"].append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*🔗 Link:*\n<{link}|View Product>"
                    }
                ]
            })
        
        # Add description if available
        if description and len(description.strip()) > 0:
            clean_desc = description.strip()
            if len(clean_desc) > 300:
                clean_desc = clean_desc[:300] + "..."
            
            payload["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 Details:*\n{clean_desc}"
                }
            })
        
        # Add action button
        payload["blocks"].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🛍️ View Product"
                    },
                    "url": link
                }
            ]
        })
        
        # Add footer
        payload["blocks"].append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🤖 Keepa Alerts • {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        })
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully sent Slack notification for: {title}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def send_test_notification(self) -> bool:
        """Send a test notification to verify Slack integration"""
        # Test with a sample product image
        sample_image = "https://images-na.ssl-images-amazon.com/images/I/51RkXeTHbbL._SX300_SY300_QL70_FMwebp_.jpg"
        
        return self.send_notification(
            title="Test Notification - Product with Image",
            link="https://example.com/test-product",
            price="$19.99",
            description="This is a test notification with product image to verify the new image feature works correctly.",
            image_url=sample_image
        )
