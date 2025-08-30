import os
from typing import List

class Config:
    # Bot Configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
    BESTDEBRID_API_KEY: str = os.getenv('BESTDEBRID_API_KEY', '68b2aceac3d4e1756540138aW1lZHVzYQ==')

    # Authorized user IDs (can be set via environment variables)
    AUTHORIZED_USERS: List[int] = [
        int(x.strip()) for x in os.getenv('AUTHORIZED_USERS', '123456789,987654321,555666777').split(',') if x.strip()
    ]

    # API Configuration
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'https://bestdebrid.com/api/v1/')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate_config(cls):
        """Validate configuration on startup"""
        if cls.BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
            raise ValueError("BOT_TOKEN environment variable must be set")

        if not cls.AUTHORIZED_USERS:
            raise ValueError("AUTHORIZED_USERS environment variable must be set")

        print(f"✅ Configuration loaded successfully")
        print(f"📊 Authorized users: {len(cls.AUTHORIZED_USERS)}")
        print(f"🔑 API Key configured: {'Yes' if cls.BESTDEBRID_API_KEY else 'No'}")
