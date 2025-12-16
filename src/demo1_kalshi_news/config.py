"""
Configuration module for Demo 1: Kalshi + News API integration.
Loads environment variables and exports configuration objects.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class AzureConfig:
    """Azure OpenAI configuration."""
    ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    @classmethod
    def validate(cls):
        """Validate that all required Azure credentials are present."""
        missing = []
        if not cls.ENDPOINT:
            missing.append('AZURE_OPENAI_ENDPOINT')
        if not cls.API_KEY:
            missing.append('AZURE_OPENAI_API_KEY')
        if not cls.DEPLOYMENT_NAME:
            missing.append('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        if missing:
            raise ValueError(
                f"Missing required Azure credentials: {', '.join(missing)}. "
                "Please check your .env file."
            )


class KalshiConfig:
    """Kalshi API configuration."""
    API_URL = os.getenv('KALSHI_API_URL', 'https://api.elections.kalshi.com/trade-api/v2')
    EMAIL = os.getenv('KALSHI_EMAIL')
    PASSWORD = os.getenv('KALSHI_PASSWORD')
    
    @classmethod
    def validate(cls):
        """Validate that all required Kalshi credentials are present."""
        missing = []
        if not cls.EMAIL:
            missing.append('KALSHI_EMAIL')
        if not cls.PASSWORD:
            missing.append('KALSHI_PASSWORD')
        
        if missing:
            raise ValueError(
                f"Missing required Kalshi credentials: {', '.join(missing)}. "
                "Please check your .env file."
            )


class NewsConfig:
    """News API configuration."""
    API_KEY = os.getenv('NEWS_API_KEY')
    API_URL = os.getenv('NEWS_API_URL', 'https://newsapi.org/v2')
    
    @classmethod
    def validate(cls):
        """Validate that all required News API credentials are present."""
        if not cls.API_KEY:
            raise ValueError(
                "Missing required News API credential: NEWS_API_KEY. "
                "Please check your .env file."
            )


def validate_all_configs():
    """Validate all configuration objects."""
    AzureConfig.validate()
    KalshiConfig.validate()
    NewsConfig.validate()
    print("✓ All configuration validated successfully")
