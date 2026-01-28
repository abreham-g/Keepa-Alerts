"""Configuration management for Keepa Alert Service"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Slack configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    
    # Keepa RSS configuration
    KEEPA_RSS_URL = os.getenv('KEEPA_RSS_URL', 'https://rss.keepa.com/3tnsab4a9nobj82tkqi2nigo2cpcrkju')
    
    # Server configuration
    PORT = int(os.getenv('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Polling configuration
    POLL_INTERVAL = 300  # 5 minutes in seconds
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.SLACK_WEBHOOK_URL:
            raise ValueError("SLACK_WEBHOOK_URL environment variable is required")
        
        if not cls.KEEPA_RSS_URL:
            raise ValueError("KEEPA_RSS_URL environment variable is required")
