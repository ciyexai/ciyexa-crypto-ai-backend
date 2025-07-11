import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ciyexa AI LLM Crypto Agent Backend"
    VERSION: str = "0.2.0" # Updated version
    DESCRIPTION: str = "Backend for Ciyexa, an AI LLM Crypto Agent with advanced data features."
    LLM_API_BASE_URL: str = "http://localhost:3000/api/chat" # URL to your Next.js LLM API

    # CoinGecko API configuration
    COINGECKO_API_BASE_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: Optional[str] = None # Optional API key for CoinGecko (for higher rate limits)
    DEFAULT_VS_CURRENCY: str = "usd" # Default currency for price comparisons

    # List of supported cryptocurrencies (CoinGecko IDs)
    SUPPORTED_CRYPTOS: list[str] = [
        "bitcoin", "ethereum", "ripple", "cardano", "solana",
        "dogecoin", "polkadot", "litecoin", "chainlink", "stellar",
        "binancecoin", "tron", "avalanche-2", "shiba-inu", "uniswap",
        "cosmos", "near-protocol", "algorand", "vechain", "elrond-egld" # Added more
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
