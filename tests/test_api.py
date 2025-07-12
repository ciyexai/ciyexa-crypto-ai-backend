import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from ciyexa_backend.main import app
from ciyexa_backend.api.v1.schemas.crypto import CryptoData, MarketData, HistoricalPriceData, TopCrypto
from ciyexa_backend.core.config import settings

client = TestClient(app)

# Mock data for services
MOCK_LLM_RESPONSE = "This is a mock LLM response."
MOCK_CRYPTO_MARKET_DATA = CryptoData(
    id="bitcoin",
    symbol="btc",
    name="Bitcoin",
    market_data=MarketData(
        current_price={"usd": 70000.0},
        market_cap={"usd": 1300000000000.0},
        total_volume={"usd": 30000000000.0},
        price_change_percentage_24h=2.5
    )
)
MOCK_HISTORICAL_DATA = HistoricalPriceData(
    prices=[[1678886400000, 20000.0], [1678972800000, 20500.0]],
    market_caps=[[1678886400000, 380000000000.0], [1678972800000, 390000000000.0]],
    total_volumes=[[1678886400000, 10000000000.0], [1678972800000, 11000000000.0]]
)
MOCK_TOP_CRYPTOS = [
    TopCrypto(
        id="bitcoin", symbol="btc", name="Bitcoin", image="url",
        current_price=70000.0, market_cap=1.3e12, market_cap_rank=1, total_volume=3e10
    ),
    TopCrypto(
        id="ethereum", symbol="eth", name="Ethereum", image="url",
        current_price=3500.0, market_cap=4.2e11, market_cap_rank=2, total_volume=1.5e10
    )
]

@pytest.fixture(autouse=True)
def mock_services(mocker):
    """
    Fixture to mock external service dependencies for all tests.
    """
    # Mock LLMAgentService
    mocker.patch('ciyexa_backend.services.llm_agent.LLMAgentService.get_llm_response',
                 new_callable=AsyncMock, return_value=MOCK_LLM_RESPONSE)
    
    # Mock CryptoDataService
    mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_market_data',
                 new_callable=AsyncMock, return_value=MOCK_CRYPTO_MARKET_DATA)
    mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_historical_prices',
                 new_callable=AsyncMock, return_value=MOCK_HISTORICAL_DATA)
    mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_top_n_cryptos_by_market_cap',
                 new_callable=AsyncMock, return_value=MOCK_TOP_CRYPTOS)
    
    # Ensure supported cryptos list is consistent for tests
    mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_supported_cryptos_list',
                 return_value=["bitcoin", "ethereum", "cardano"])


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Ciyexa AI LLM Crypto Agent Backend!"}

@pytest.mark.asyncio
async def test_chat_general_query(mocker):
    """Test chat endpoint with a general query."""
    mock_llm_response = mocker.patch('ciyexa_backend.services.llm_agent.LLMAgentService.get_llm_response',
                                     new_callable=AsyncMock, return_value="AI response to general query.")
    
    response = client.post("/api/v1/agent/chat", json={"query": "What is AI?"})
    assert response.status_code == 200
    assert response.json()["response"] == "AI response to general query."
    assert response.json()["source"] == "LLM"
    mock_llm_response.assert_called_once_with("What is AI?")

@pytest.mark.asyncio
async def test_chat_current_crypto_query(mocker):
    """Test chat endpoint with a current crypto price query."""
    mock_get_market_data = mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_market_data',
                                        new_callable=AsyncMock, return_value=MOCK_CRYPTO_MARKET_DATA)
    mock_llm_response = mocker.patch('ciyexa_backend.services.llm_agent.LLMAgentService.get_llm_response',
                                     new_callable=AsyncMock, return_value="AI response with Bitcoin price.")

    response = client.post("/api/v1/agent/chat", json={"query": "What is the price of Bitcoin?"})
    assert response.status_code == 200
    assert response.json()["response"] == "AI response with Bitcoin price."
    assert response.json()["source"] == "Hybrid (LLM + Current Crypto Data)"
    mock_get_market_data.assert_called_once_with("bitcoin")
    # Check if LLM was called with enriched prompt
    assert "Current Price (USD): $70,000.00" in mock_llm_response.call_args[0][0]

@pytest.mark.asyncio
async def test_chat_historical_crypto_query(mocker):
    """Test chat endpoint with a historical crypto price query."""
    mock_get_historical_prices = mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_historical_prices',
                                              new_callable=AsyncMock, return_value=MOCK_HISTORICAL_DATA)
    mock_llm_response = mocker.patch('ciyexa_backend.services.llm_agent.LLMAgentService.get_llm_response',
                                     new_callable=AsyncMock, return_value="AI response with historical Bitcoin price.")

    response = client.post("/api/v1/agent/chat", json={"query": "What was the price of Bitcoin 7 days ago?"})
    assert response.status_code == 200
    assert response.json()["response"] == "AI response with historical Bitcoin price."
    assert response.json()["source"] == "Hybrid (LLM + Historical Crypto Data)"
    mock_get_historical_prices.assert_called_once_with("bitcoin", days=7)
    # Check if LLM was called with enriched prompt
    assert "Latest recorded price (approx): $20,500.00 USD." in mock_llm_response.call_args[0][0]

@pytest.mark.asyncio
async def test_get_historical_crypto_data_success(mocker):
    """Test fetching historical crypto data directly."""
    mock_get_historical_prices = mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_historical_prices',
                                              new_callable=AsyncMock, return_value=MOCK_HISTORICAL_DATA)
    
    response = client.get("/api/v1/crypto/historical/bitcoin?days=7")
    assert response.status_code == 200
    assert response.json() == MOCK_HISTORICAL_DATA.model_dump(mode='json')
    mock_get_historical_prices.assert_called_once_with("bitcoin", 7)

@pytest.mark.asyncio
async def test_get_historical_crypto_data_not_found():
    """Test fetching historical data for unsupported crypto."""
    response = client.get("/api/v1/crypto/historical/unsupported-coin?days=7")
    assert response.status_code == 404
    assert "not supported or found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_top_n_cryptos_success(mocker):
    """Test fetching top N cryptocurrencies."""
    mock_get_top_n_cryptos = mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_top_n_cryptos_by_market_cap',
                                          new_callable=AsyncMock, return_value=MOCK_TOP_CRYPTOS)
    
    response = client.get("/api/v1/crypto/top/2")
    assert response.status_code == 200
    assert response.json()["data"] == [c.model_dump(mode='json') for c in MOCK_TOP_CRYPTOS]
    mock_get_top_n_cryptos.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_get_single_crypto_market_data_success(mocker):
    """Test fetching single crypto market data directly."""
    mock_get_market_data = mocker.patch('ciyexa_backend.services.crypto_data_service.CryptoDataService.get_market_data',
                                        new_callable=AsyncMock, return_value=MOCK_CRYPTO_MARKET_DATA)
    
    response = client.get("/api/v1/crypto/bitcoin")
    assert response.status_code == 200
    assert response.json() == MOCK_CRYPTO_MARKET_DATA.model_dump(mode='json')
    mock_get_market_data.assert_called_once_with("bitcoin")

@pytest.mark.asyncio
async def test_get_single_crypto_market_data_not_found():
    """Test fetching single crypto market data for unsupported crypto."""
    response = client.get("/api/v1/crypto/unsupported-coin")
    assert response.status_code == 404
    assert "not supported or found" in response.json()["detail"]
