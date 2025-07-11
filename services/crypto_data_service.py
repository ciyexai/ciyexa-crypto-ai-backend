import httpx
from typing import List, Dict, Optional
from ciyexa_backend.core.config import settings
from ciyexa_backend.utils.logger import get_logger
from ciyexa_backend.api.v1.schemas.crypto import CryptoData, HistoricalPriceData, TopCrypto

logger = get_logger(__name__)

class CryptoDataService:
    def __init__(self):
        self.base_url = settings.COINGECKO_API_BASE_URL
        self.supported_cryptos = settings.SUPPORTED_CRYPTOS
        self.vs_currency = settings.DEFAULT_VS_CURRENCY
        self.headers = {}
        if settings.COINGECKO_API_KEY:
            self.headers["x-cg-pro-api-key"] = settings.COINGECKO_API_KEY # For paid CoinGecko API

    async def _make_request(self, url: str) -> Optional[Dict]:
        """Helper for making HTTP requests to CoinGecko API."""
        try:
            async with httpx.AsyncClient(headers=self.headers) as client:
                response = await client.get(url, timeout=15.0)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"CoinGecko API request failed for {url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"CoinGecko API returned error status {e.response.status_code} for {url}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during CoinGecko API call to {url}: {e}")
            return None

    async def get_current_prices(self, crypto_ids: List[str], vs_currencies: str = None) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Fetches current prices for a list of cryptocurrency IDs.
        """
        if not crypto_ids:
            return None
        
        vs_currencies = vs_currencies or self.vs_currency
        ids_str = ",".join(crypto_ids)
        url = f"{self.base_url}/simple/price?ids={ids_str}&vs_currencies={vs_currencies}"
        return await self._make_request(url)

    async def get_market_data(self, crypto_id: str, vs_currencies: str = None) -> Optional[CryptoData]:
        """
        Fetches detailed market data for a single cryptocurrency.
        """
        vs_currencies = vs_currencies or self.vs_currency
        url = f"{self.base_url}/coins/{crypto_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
        data = await self._make_request(url)
        return CryptoData(**data) if data else None

    async def get_historical_prices(self, crypto_id: str, days: int = 7, vs_currency: str = None) -> Optional[HistoricalPriceData]:
        """
        NEW: Fetches historical market data (prices, market caps, volumes) for a cryptocurrency.
        'days' can be 1, 7, 14, 30, 90, 180, 365, max.
        """
        vs_currencies = vs_currencies or self.vs_currency
        url = f"{self.base_url}/coins/{crypto_id}/market_chart?vs_currency={vs_currencies}&days={days}"
        data = await self._make_request(url)
        return HistoricalPriceData(**data) if data else None

    async def get_top_n_cryptos_by_market_cap(self, top_n: int = 10, vs_currency: str = None) -> Optional[List[TopCrypto]]:
        """
        NEW: Fetches a list of top N cryptocurrencies by market capitalization.
        """
        vs_currencies = vs_currencies or self.vs_currency
        url = f"{self.base_url}/coins/markets?vs_currency={vs_currencies}&order=market_cap_desc&per_page={top_n}&page=1&sparkline=false"
        data = await self._make_request(url)
        return [TopCrypto(**item) for item in data] if data else None

    def get_supported_cryptos_list(self) -> List[str]:
        """Returns the list of supported cryptocurrency IDs."""
        return self.supported_cryptos

    def get_crypto_id_from_name(self, name: str) -> Optional[str]:
        """
        Simple helper to map common names to CoinGecko IDs.
        In a real app, you'd use a more robust mapping or a search API.
        """
        name_lower = name.lower()
        for crypto_id in self.supported_cryptos:
            if name_lower in crypto_id.lower() or name_lower == crypto_id.lower().replace('-', ''):
                return crypto_id
        return None
