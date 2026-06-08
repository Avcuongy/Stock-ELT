import os
from dotenv import load_dotenv

load_dotenv()

# API
SEC_API_KEY = os.getenv("SEC_API_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
