
# Ciyexa AI LLM Crypto Agent Backend

  

Welcome to the heart of Ciyexa, your intelligent AI LLM Crypto Agent! This robust Python backend, powered by FastAPI, is designed to provide real-time and historical cryptocurrency insights, empowering your AI to deliver accurate and timely information.

  

## 🌐 Connect with Ciyexa

  

Stay updated with the latest from Ciyexa AI!

  

*  **Twitter:** [Follow us on X (formerly Twitter)](https://x.com/Ciyexa_AI)

*  **Website:** [Visit our Official Website](https://www.ciyexa.dev/)

  

## ✨ Features

  

*  **Intelligent AI Chat**: Engage with an AI agent capable of understanding and responding to your crypto queries.

*  **Real-time Crypto Data**: Get instant access to current prices, market caps, and 24-hour changes for over 15 popular cryptocurrencies.

*  **Historical Price Insights**: Dive into the past with historical price data for any supported crypto, allowing the AI to answer questions about past performance.

*  **Top Cryptocurrencies**: Quickly fetch a list of the top N cryptocurrencies by market capitalization.

*  **Modular & Scalable**: Built with a clean, layered architecture for easy expansion and maintenance.

*  **LLM Integration**: Seamlessly integrates with external Large Language Models (LLMs) via a dedicated API, leveraging the power of the Vercel AI SDK.

  

## 🧠 Architecture

  

The Ciyexa backend operates on a sophisticated, yet clear, architecture:

  

1.  **User Query**: A user sends a natural language query to the FastAPI backend.

2.  **Intelligent Routing & Data Enrichment**: The Python backend intelligently analyzes the query. If it detects a crypto-related question (e.g., "What's the price of Bitcoin?", "What was Ethereum's price last week?"), it springs into action:

* It queries the `CryptoDataService` to fetch real-time or historical data from CoinGecko for the relevant cryptocurrency.

* It then crafts an "enriched prompt" for the LLM, embedding the fresh crypto data directly into the prompt.

3. **LLM Interaction**: This enriched prompt is sent to a dedicated Next.js API route. This route, powered by the Vercel AI SDK, handles the secure and efficient communication with the chosen Large Language Model (e.g., OpenAI's GPT-4o).

4. **AI Response**: The LLM processes the prompt (now armed with real-time or historical data!) and generates a comprehensive answer.

5. **Seamless Delivery**: The LLM's response flows back through the Next.js API to the Python backend, which then delivers it to the user.

  

This separation ensures that your Python backend remains lean and focused on business logic and data orchestration, while the LLM interactions are handled by a service optimized for the AI SDK.

  

## 🛠️ Getting Started: Ignite Your Agent!

  

Follow these steps to get Ciyexa up and running on your local machine.

  

### Prerequisites

  

* Python 3.9+

* Node.js 18+ & npm/yarn (for the Next.js LLM API)

  

### 1. Clone the Repository

  

    > git clone <your-repo-url>
    > cd ciyexa_backend

  

### 2. Set Up Python Backend

  

It's highly recommended to use a virtual environment:

  

   bash:

    > python -m venv venv

    > source venv/bin/activate # On Windows: `venv\Scripts\activate

  

Install the required Python dependencies:

  

bash:

    > pip install -r requirements.txt


  

Configure your environment variables. Create a `.env` file in the `ciyexa_backend` directory based on `.env.example`:

  

    dotenv

LLM_API_BASE_URL="http://localhost:3000/api/chat"

**COINGECKO_API_KEY="YOUR_COINGECKO_API_KEY" # Uncomment and add if you have a CoinGecko Pro API key**


  

### 3. Set Up Next.js LLM API (Example)

  

If you don't have a Next.js project, create one. Then, add an API route (e.g., `app/api/chat/route.ts`) that uses the AI SDK.

  

> typescript
> 
> // app/api/chat/route.ts (Example - ensure this matches your actual
> implementation)

    import { generateText } from 'ai';
    import { openai } from '@ai-sdk/openai';
    export async function POST(req: Request) {
    try {
    const { prompt } = await req.json();
    const { text } = await generateText({
    
    model: openai('gpt-4o'), // Or your preferred LLM
    prompt: prompt,
    });
    return new Response(JSON.stringify({ response: text }), {
    headers: { 'Content-Type': 'application/json' },
    });
    } catch (error) {
    console.error('Error in LLM API route:', error);
    return new Response(JSON.stringify({ error: 'Failed to generate text from LLM.' }), {
    status: 500,
    headers: { 'Content-Type': 'application/json' },
    });
    }
    }


  

Install AI SDK dependencies in your Next.js project:

  

bash:

    > npm install ai @ai-sdk/openai

  

Set your LLM provider's API key as an environment variable in your Next.js project (e.g., in a `.env.local` file):

  

dotenv:

    > OPENAI_API_KEY="your_openai_api_key_here"


  

### 4. Run Both Applications

  

First, start your Next.js LLM API:

  

bash:

    npm run dev # or yarn dev

  

Then, start the Python FastAPI backend:

  
bash:

    > uvicorn ciyexa_backend.main:app --reload --host 0.0.0.0 --port 8000

  

Your FastAPI backend will be accessible at `http://localhost:8000`. The interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## 🧪 Testing

  

To ensure the reliability and correctness of the Ciyexa backend, we use `pytest` for our test suite.

  

### Running Tests

  

1. **Install Test Dependencies**: Make sure you have the testing dependencies installed. If you followed the setup steps, they should already be in your `requirements.txt`.

bash:

    pip install pytest pytest-asyncio pytest-mock

2. **Navigate to the Project Root**: Ensure your terminal is in the `ciyexa_backend` directory (where `main.py` and the `tests` folder are located).

3. **Execute Tests**: Run `pytest` from your terminal:

bash:

    pytest

  

This will discover and run all tests in the `tests/` directory. The tests are designed to mock external API calls (to the LLM and CoinGecko) to ensure fast, isolated, and reliable results without requiring network access or external services to be running.
  

## 🚀 How to Use: Interact with Ciyexa!

  

Once both the Python backend and the Next.js LLM API are running, you can interact with your Ciyexa agent by sending HTTP POST requests to the `/api/v1/agent/chat` endpoint, or by directly querying the new crypto data endpoints.

  

You can use tools like `curl`, Postman, Insomnia, or even a simple JavaScript `fetch` call from a frontend application.

  

### 1. Chat with the AI Agent (`POST /api/v1/agent/chat`)

  

Send your natural language queries to the AI agent. The agent will intelligently use real-time or historical data when relevant.

  

* **Example: Ask about a cryptocurrency's current price:**

bash:

    curl -X POST http://localhost:8000/api/v1/agent/chat \
    
    -H "Content-Type: application/json" \
    
    -d '{ "query": "What is the current price of Ethereum and its 24-hour change?" }'

  

* **Example: Ask about historical price data:**

bash:

    curl -X POST http://localhost:8000/api/v1/agent/chat \
    
    -H "Content-Type: application/json" \
    
    -d '{ "query": "What was the price of Bitcoin 7 days ago?" }'

*(Note: The AI's response will be based on the historical data provided in the prompt.)*

  

* **Example: Ask a general crypto-related question:**

bash:

    curl -X POST http://localhost:8000/api/v1/agent/chat \
    
    -H "Content-Type: application/json" \
    
    -d '{ "query": "Explain what decentralized finance (DeFi) is." }'

  

### 2. Get Historical Crypto Data (`GET /api/v1/crypto/historical/{crypto_id}?days={days}`)

  

Retrieve raw historical price, market cap, and volume data.

  

* **Example: Get Bitcoin's price data for the last 30 days:**

bash:

    curl http://localhost:8000/api/v1/crypto/historical/bitcoin?days=30

  

### 3. Get Top Cryptocurrencies (`GET /api/v1/crypto/top/{top_n}`)

  

Fetch a list of the top N cryptocurrencies by market capitalization.

  

* **Example: Get the top 5 cryptocurrencies:**

bash:

    curl http://localhost:8000/api/v1/crypto/top/5

  

### 4. Get Single Crypto Market Data (`GET /api/v1/crypto/{crypto_id}`)

  

Retrieve detailed current market data for a specific cryptocurrency.

  

* **Example: Get detailed data for Cardano:**

bash:

    curl http://localhost:8000/api/v1/crypto/cardano

  

### 5. Explore the API Documentation

  

Open your web browser and navigate to `http://localhost:8000/docs` to explore the interactive API documentation (Swagger UI). Here, you can test all the endpoints directly from your browser!

  

## 📈 Future Enhancements: The Road Ahead

  

Ciyexa is designed for continuous evolution! Consider these exciting next steps:

  

* **Advanced NLP for Date/Time Parsing**: Implement more sophisticated natural language processing to accurately extract specific dates and timeframes from user queries for historical data.

* **LLM Tool Calling**: Leverage advanced LLM features like tool calling (e.g., OpenAI Functions) to allow the LLM to dynamically decide when and how to fetch specific crypto data or execute other actions, rather than relying on keyword detection.

* **Trading Strategies Module**: Integrate a dedicated service for defining, backtesting, and executing automated crypto trading strategies.

* **User & Portfolio Management**: Add database integration (e.g., PostgreSQL with SQLAlchemy) to store user profiles, chat history, and track crypto portfolios.

* **Authentication & Authorization**: Secure your API with robust user authentication and authorization mechanisms.

* **Real-time Data Streams**: Explore WebSocket integration for real-time price updates and push notifications to connected clients.

* **Alerts & Notifications**: Allow users to set up price alerts or news notifications for specific cryptocurrencies.

  

## 🙏 Contributing

  

We welcome contributions! Feel free to fork the repository, open issues, or submit pull requests. Let's build the future of crypto AI together!