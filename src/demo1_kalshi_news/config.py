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
    """GitHub Models / OpenAI configuration."""
    # GitHub Models endpoint
    ENDPOINT = os.getenv('OPENAI_ENDPOINT', 'https://models.inference.ai.azure.com')
    API_KEY = os.getenv('GITHUB_TOKEN')
    DEPLOYMENT_NAME = os.getenv('OPENAI_MODEL', 'gpt-5-chat')
    API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    @classmethod
    def validate(cls):
        """Validate that all required credentials are present."""
        if not cls.API_KEY:
            raise ValueError(
                "Missing required credential: GITHUB_TOKEN. "
                "Please check your .env file."
            )


class KalshiConfig:
    """Kalshi API configuration."""
    # Public endpoint (no auth required for read-only access)
    API_URL = os.getenv('KALSHI_API_URL', 'https://api.elections.kalshi.com/v1')
    # Optional API key for authenticated access (trading, full historical data)
    API_KEY = os.getenv('KALSHI_API_KEY', None)
    
    @classmethod
    def validate(cls):
        """Validate Kalshi configuration (API key is optional for public access)."""
        # No validation needed - public endpoint works without auth
        pass


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


class TextAnalyticsConfig:
    """Azure Language Text Analytics configuration."""
    ENDPOINT = os.getenv('AZURE_TEXT_ANALYTICS_ENDPOINT')
    API_KEY = os.getenv('AZURE_TEXT_ANALYTICS_KEY')
    # Secondary key for failover
    API_KEY_2 = os.getenv('AZURE_TEXT_ANALYTICS_KEY_2')
    REGION = 'switzerlandnorth'
    
    @classmethod
    def validate(cls):
        """Validate that Text Analytics credentials are present."""
        if not cls.ENDPOINT:
            raise ValueError(
                "Missing required Text Analytics credential: AZURE_TEXT_ANALYTICS_ENDPOINT. "
                "Please check your .env file."
            )
        if not cls.API_KEY:
            raise ValueError(
                "Missing required Text Analytics credential: AZURE_TEXT_ANALYTICS_KEY. "
                "Please check your .env file."
            )


def validate_all_configs():
    """Validate all configuration objects."""
    AzureConfig.validate()
    KalshiConfig.validate()
    NewsConfig.validate()
    TextAnalyticsConfig.validate()
    print("✓ All configuration validated successfully")
