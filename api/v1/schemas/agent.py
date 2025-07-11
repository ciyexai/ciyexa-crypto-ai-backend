from pydantic import BaseModel, Field

class AgentQuery(BaseModel):
    query: str = Field(..., min_length=1, description="The user's query for the AI agent.")

class AgentResponse(BaseModel):
    response: str = Field(..., description="The AI agent's response.")
    source: str = Field("LLM", description="The source of the response (e.g., LLM, Crypto Data).")
