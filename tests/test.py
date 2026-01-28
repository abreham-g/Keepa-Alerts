import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Test RSS feed with basic requests
rss_url = os.getenv('KEEPA_RSS_URL')
print(f'Testing RSS feed access: {rss_url}')
try:
    response = requests.get(rss_url, timeout=10)
    print(f'RSS feed status: {response.status_code}')
    print(f'Content type: {response.headers.get("content-type", "unknown")}')
    print(f'Content length: {len(response.content)} bytes')
    
    if response.status_code == 200:
        print('✅ RSS feed is accessible')
    else:
        print(f'❌ RSS feed error: {response.status_code}')
        
except Exception as e:
    print(f'❌ RSS error: {e}')

# Test Slack webhook
webhook_url = os.getenv('SLACK_WEBHOOK_URL')
print(f'\nTesting Slack webhook...')
if webhook_url:
    try:
        payload = {
            'text': '🧪 Test notification from Keepa Alert Service',
            'attachments': [{
                'color': 'good',
                'fields': [{
                    'title': 'Status',
                    'value': 'Service is working correctly!',
                    'short': False
                }]
            }]
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        print(f'Slack webhook status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Test message sent to Slack successfully!')
        else:
            print(f'Slack error: {response.text}')
    except Exception as e:
        print(f'Slack error: {e}')
else:
    print('❌ SLACK_WEBHOOK_URL not found')
