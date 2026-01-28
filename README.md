# Keepa to Slack Alert Service

This service monitors your Keepa RSS feed and sends notifications to Slack when new price alerts are available.

## Setup Instructions

### 1. Create Slack Webhook

1. Go to your Slack workspace
2. Navigate to **Apps** → **Manage Apps** → **Custom Integrations** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Choose a channel to post messages
5. Copy the webhook URL

### 2. Configure Environment Variables

Update your `.env` file with your Slack webhook URL:

```bash
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
KEEPA_RSS_URL=https://rss.keepa.com/3tnsab4a9nobj82tkqi2nigo2cpcrkju
PORT=5000
```

### 3. Deploy to Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize project: `railway init`
4. Deploy: `railway up`

Or connect your GitHub repository to Railway for automatic deployments.

### 4. Set Environment Variables in Railway

In your Railway project dashboard:
1. Go to **Settings** → **Variables**
2. Add your `SLACK_WEBHOOK_URL`
3. Add your `KEEPA_RSS_URL` (optional, uses your URL by default)

## Features

- **Automatic Polling**: Checks RSS feed every 5 minutes
- **Duplicate Prevention**: Tracks sent alerts to avoid duplicates
- **Price Extraction**: Automatically extracts price information from alert titles
- **Health Check**: `/` endpoint for monitoring service status
- **Manual Trigger**: `/check` endpoint to manually check for new alerts
- **Webhook Receiver**: `/webhook` endpoint for external triggers

## API Endpoints

- `GET /` - Health check and status
- `POST /check` - Manual alert check trigger
- `POST /webhook` - Generic webhook receiver

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SLACK_WEBHOOK_URL="your_webhook_url"

# Run the service
python app.py
```

## Monitoring

The service logs:
- New alerts found and sent
- Failed notifications
- RSS feed parsing errors
- Scheduled check status

## Troubleshooting

1. **No notifications**: Check your Slack webhook URL is correct
2. **RSS errors**: Verify your Keepa RSS URL is accessible
3. **Deployment issues**: Ensure all environment variables are set in Railway
