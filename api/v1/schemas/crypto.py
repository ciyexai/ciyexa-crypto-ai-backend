from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class MarketData(BaseModel):
    current_price: Dict[str, float] = Field(..., description="Current price in various currencies.")
    market_cap: Dict[str, float] = Field(..., description="Market capitalization in various currencies.")
    total_volume: Dict[str, float] = Field(..., description="Total trading volume in various currencies.")
    price_change_percentage_24h: Optional[float] = Field(None, description="24-hour price change percentage.")

class CryptoData(BaseModel):
    id: str = Field(..., description="CoinGecko ID of the cryptocurrency.")
    symbol: str = Field(..., description="Symbol of the cryptocurrency.")
    name: str = Field(..., description="Name of the cryptocurrency.")
    market_data: Optional[MarketData] = Field(None, description="Market data for the cryptocurrency.")

class CryptoPricesResponse(BaseModel):
    data: Dict[str, Dict[str, float]] = Field(..., description="Dictionary of crypto IDs to their prices in USD.")

# NEW: Schema for Historical Price Data
class HistoricalPriceData(BaseModel):
    prices: List[List[float]] = Field(..., description="List of [timestamp, price] pairs.")
    market_caps: List[List[float]] = Field(..., description="List of [timestamp, market_cap] pairs.")
    total_volumes: List[List[float]] = Field(..., description="List of [timestamp, total_volume] pairs.")

# NEW: Schema for Top Cryptos
class TopCrypto(BaseModel):
    id: str
    symbol: str
    name: str
    image: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    total_volume: float
    price_change_percentage_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    ath: Optional[float] = None
    ath_change_percentage: Optional[float] = None
    ath_date: Optional[str] = None
    atl: Optional[float] = None
    atl_change_percentage: Optional[float] = None
    atl_date: Optional[str] = None
    roi: Optional[Dict] = None
    last_updated: Optional[str] = None

class TopCryptosResponse(BaseModel):
    data: List[TopCrypto] = Field(..., description="List of top cryptocurrencies by market cap.")
