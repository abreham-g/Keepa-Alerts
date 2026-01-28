import requests
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv('SLACK_WEBHOOK_URL')

# Test with minimal payload first
minimal_payload = {
    "text": "🧪 Simple test message"
}

print("Testing minimal payload...")
try:
    response = requests.post(webhook_url, json=minimal_payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test with our current payload
current_payload = {
    "text": "🛒 Keepa Alert: Test Product",
    "attachments": [
        {
            "color": "good",
            "fields": [
                {
                    "title": "Product",
                    "value": "*Test Product*",
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
            "footer": "Keepa Alerts",
            "ts": 1738033980
        }
    ]
}

print("Testing current payload...")
try:
    response = requests.post(webhook_url, json=current_payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test with blocks format (newer Slack format)
blocks_payload = {
    "text": "🛒 Keepa Alert: Test Product",
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🛒 Keepa Alert: Test Product"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Product:*\nTest Product"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Price:*\n$19.99"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Product"
                    },
                    "url": "https://example.com"
                }
            ]
        }
    ]
}

print("Testing blocks payload...")
try:
    response = requests.post(webhook_url, json=blocks_payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
