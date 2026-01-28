"""Main Flask application for Keepa to Slack Alert Service"""

import time
import threading
import sys
import os
from datetime import datetime
from flask import Flask, request, jsonify
import logging
from typing import Set

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from slack_service import SlackService
from rss_service import RSSService

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Suppress werkzeug development server warnings and startup messages
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.CRITICAL)  # Only show critical errors

# Suppress Flask startup messages
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

app = Flask(__name__)

# Suppress Flask startup messages
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Completely disable Flask's default logging
import logging
logging.getLogger('flask').setLevel(logging.CRITICAL)

# Global set to track sent alerts
sent_alerts: Set[str] = set()

# Initialize services
slack_service = SlackService()
rss_service = RSSService()


def check_and_send_alerts():
    """Check for new alerts and send notifications"""
    global sent_alerts
    
    alerts = rss_service.parse_keepa_rss()
    new_alerts_count = 0
    
    for alert in alerts:
        alert_id = alert['id']
        
        if alert_id not in sent_alerts:
            success = slack_service.send_notification(
                title=alert['title'],
                link=alert['link'],
                price=alert['price'],
                description=alert['description'],
                image_url=alert.get('image_url')
            )
            
            if success:
                sent_alerts.add(alert_id)
                new_alerts_count += 1
    
    if new_alerts_count > 0:
        logger.info(f"Sent {new_alerts_count} new alerts to Slack")
    else:
        logger.info("No new alerts found")
    
    return new_alerts_count


def run_scheduled_check():
    """Run scheduled check every 5 minutes"""
    while True:
        try:
            logger.info("Running scheduled alert check...")
            check_and_send_alerts()
            logger.info(f"Scheduled check completed. Waiting {Config.POLL_INTERVAL} seconds...")
            time.sleep(Config.POLL_INTERVAL)
        except Exception as e:
            logger.error(f"Error in scheduled check: {e}")
            time.sleep(60)  # Wait 1 minute before retrying


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "sent_alerts_count": len(sent_alerts),
        "version": "1.0.0"
    })


@app.route('/check', methods=['POST'])
def manual_check():
    """Manual trigger for checking alerts"""
    try:
        new_alerts = check_and_send_alerts()
        return jsonify({
            "status": "success",
            "new_alerts_sent": new_alerts,
            "total_sent_alerts": len(sent_alerts)
        })
    except Exception as e:
        logger.error(f"Error in manual check: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """Generic webhook receiver for external triggers"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        
        # Trigger alert check
        new_alerts = check_and_send_alerts()
        
        return jsonify({
            "status": "success",
            "new_alerts_sent": new_alerts,
            "received_data": data
        })
    except Exception as e:
        logger.error(f"Error in webhook receiver: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/test', methods=['POST'])
def test_slack():
    """Test Slack integration"""
    try:
        success = slack_service.send_test_notification()
        return jsonify({
            "status": "success" if success else "error",
            "message": "Test notification sent" if success else "Failed to send test notification"
        })
    except Exception as e:
        logger.error(f"Error in Slack test: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def create_app():
    """Application factory"""
    try:
        Config.validate()
        logger.info("Starting Keepa to Slack alert service...")
        
        # Start the scheduled check in a background thread
        scheduler_thread = threading.Thread(target=run_scheduled_check, daemon=True)
        scheduler_thread.start()
        
        return app
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Keepa to Slack Alert Service')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--port', type=int, default=None, help='Override default port')
    args = parser.parse_args()
    
    # Update log level if specified
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Override port if specified
    if args.port:
        Config.PORT = args.port
    
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=False, use_reloader=False)
