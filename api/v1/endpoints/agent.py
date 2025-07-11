from fastapi import APIRouter, HTTPException, status
from ciyexa_backend.api.v1.schemas.agent import AgentQuery, AgentResponse
from ciyexa_backend.services.llm_agent import LLMAgentService
from ciyexa_backend.services.crypto_data_service import CryptoDataService
from ciyexa_backend.utils.logger import get_logger
import re # For simple regex matching for historical queries

router = APIRouter()
llm_service = LLMAgentService()
crypto_service = CryptoDataService()
logger = get_logger(__name__)

@router.post("/agent/chat", response_model=AgentResponse)
async def chat_with_agent(query_data: AgentQuery):
    """
    Endpoint for chatting with the Ciyexa AI agent.
    The agent will process the query, potentially fetch crypto data (current or historical),
    and then generate a response using the LLM.
    """
    user_query = query_data.query
    logger.info(f"Received chat query: {user_query}")

    llm_prompt = user_query
    response_source = "LLM"

    # --- Crypto Data Integration Logic ---
    # Simple keyword detection for crypto price queries
    crypto_price_keywords = ["price of", "how much is", "value of", "current price", "what is the price"]
    is_current_price_query = any(keyword in user_query.lower() for keyword in crypto_price_keywords)

    # NEW: Simple keyword detection for historical price queries
    historical_price_keywords = ["historical price of", "price of .* on", "price of .* ago", "price of .* last", "what was the price of"]
    is_historical_price_query = any(re.search(keyword, user_query.lower()) for keyword in historical_price_keywords)

    detected_crypto_id = None
    for crypto_name in crypto_service.get_supported_cryptos_list():
        if crypto_name.lower() in user_query.lower() or crypto_name.replace('-', '').lower() in user_query.lower():
            detected_crypto_id = crypto_name
            break
    
    if detected_crypto_id:
        if is_historical_price_query:
            logger.info(f"Detected historical crypto query for: {detected_crypto_id}")
            # For simplicity, we'll fetch 7 days of data. More advanced parsing would extract 'days' from query.
            historical_data = await crypto_service.get_historical_prices(detected_crypto_id, days=7)
            
            if historical_data and historical_data.prices:
                # Format historical data for LLM prompt
                # Take the last price as the most recent historical point
                latest_historical_price = historical_data.prices[-1][1] if historical_data.prices else "N/A"
                
                # You could iterate through more points or summarize trends for the LLM
                llm_prompt = (
                    f"The user asked: '{user_query}'. "
                    f"Here is recent historical data for {detected_crypto_id} (last 7 days):\n"
                    f"Latest recorded price (approx): ${latest_historical_price:,.2f} USD.\n"
                    f"Please provide a concise and helpful answer based on this historical information, "
                    f"and then answer any other parts of the user's original query."
                )
                response_source = "Hybrid (LLM + Historical Crypto Data)"
                logger.info(f"Enriched LLM prompt with historical crypto data for {detected_crypto_id}.")
            else:
                logger.warning(f"Could not fetch historical data for {detected_crypto_id}. Proceeding with original query.")
        elif is_current_price_query:
            logger.info(f"Detected current price crypto query for: {detected_crypto_id}")
            crypto_data = await crypto_service.get_market_data(detected_crypto_id)
            
            if crypto_data and crypto_data.market_data:
                price_usd = crypto_data.market_data.current_price.get("usd")
                price_change_24h = crypto_data.market_data.price_change_percentage_24h
                
                if price_usd is not None:
                    llm_prompt = (
                        f"The user asked: '{user_query}'. "
                        f"Here is the current data for {crypto_data.name} ({crypto_data.symbol.upper()}):\n"
                        f"- Current Price (USD): ${price_usd:,.2f}\n"
                        f"- 24h Price Change: {price_change_24h:.2f}%\n"
                        f"Please provide a concise and helpful answer based on this information, "
                        f"and then answer any other parts of the user's original query."
                    )
                    response_source = "Hybrid (LLM + Current Crypto Data)"
                    logger.info(f"Enriched LLM prompt with current crypto data for {detected_crypto_id}.")
                else:
                    logger.warning(f"Could not get USD price for {detected_crypto_id}. Proceeding with original query.")
            else:
                logger.warning(f"Could not fetch detailed market data for {detected_crypto_id}. Proceeding with original query.")
        else:
            logger.info("Crypto ID detected but not a specific price query. Proceeding with original query.")
    else:
        logger.info("No specific crypto ID or price query detected. Proceeding with original query.")

    # --- LLM Interaction ---
    try:
        llm_response_text = await llm_service.get_llm_response(llm_prompt)
        if "Error" in llm_response_text: # Simple check for error messages from service
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=llm_response_text
            )
        return AgentResponse(response=llm_response_text, source=response_source)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to process chat query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing your request."
        )
