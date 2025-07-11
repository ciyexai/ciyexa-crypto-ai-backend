from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from ciyexa_backend.services.crypto_data_service import CryptoDataService
from ciyexa_backend.api.v1.schemas.crypto import HistoricalPriceData, TopCryptosResponse, CryptoData
from ciyexa_backend.utils.logger import get_logger

router = APIRouter()
crypto_service = CryptoDataService()
logger = get_logger(__name__)

@router.get("/crypto/historical/{crypto_id}", response_model=HistoricalPriceData)
async def get_historical_crypto_data(
    crypto_id: str,
    days: int = Query(7, ge=1, description="Number of days for historical data (e.g., 1, 7, 30, 365, max).")
):
    """
    Retrieves historical price, market cap, and total volume data for a given cryptocurrency.
    """
    logger.info(f"Fetching historical data for {crypto_id} for {days} days.")
    if crypto_id not in crypto_service.get_supported_cryptos_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency '{crypto_id}' not supported or found."
        )
    
    data = await crypto_service.get_historical_prices(crypto_id, days)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve historical data from external service."
        )
    return data

@router.get("/crypto/top/{top_n}", response_model=TopCryptosResponse)
async def get_top_n_cryptos(
    top_n: int = Query(10, ge=1, le=250, description="Number of top cryptocurrencies to retrieve.")
):
    """
    Retrieves a list of the top N cryptocurrencies by market capitalization.
    """
    logger.info(f"Fetching top {top_n} cryptocurrencies.")
    data = await crypto_service.get_top_n_cryptos_by_market_cap(top_n)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve top cryptocurrencies from external service."
        )
    return TopCryptosResponse(data=data)

@router.get("/crypto/{crypto_id}", response_model=CryptoData)
async def get_single_crypto_market_data(crypto_id: str):
    """
    Retrieves detailed current market data for a single cryptocurrency.
    """
    logger.info(f"Fetching detailed market data for {crypto_id}.")
    if crypto_id not in crypto_service.get_supported_cryptos_list():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency '{crypto_id}' not supported or found."
        )
    
    data = await crypto_service.get_market_data(crypto_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve market data from external service."
        )
    return data
