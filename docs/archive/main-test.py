from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from langsearch.assistant.graph import graph
from langsearch.assistant.configuration import Configuration
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

# Now you can access the API key
api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Enable Cors for frontend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request and response models

class AnalysisRequest(BaseModel):
    """request model for initiating market analysis"""
    insights_topic: str
    max_loops: int = 1
    # search_api: str = "perplexity"
    # openai_model: str = "gpt-4o-mini"
    
class AnalysisResponse(BaseModel):
    """Response model containing final market analysis"""
    analysis: str
    sources: list[str]
    
    
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_market(request: AnalysisRequest):
    """Endpoint to trigger market analysis
    
    Args:
        request: AnalysisRequest containing topic and analysis parameters
         - topic: str, the topic to analyze
         - max_loops: int, the maximum number of loops to run
         - search_api: str, the search API to use (perplexity, tavily), this is optional and defaults to perplexity
         - openai_model: str, the OpenAI model to use, this is optional and defaults to gpt-4o-mini
    Returns:
        Structred analysis with sources and references
    """
    try:
        # Initialize configuration
        config = {"configurable": {"max_loops": request.max_loops}}
        
        # Execute the langgraph workflow
        result = await graph.ainvoke(
            {"insights_topic": request.insights_topic},
            config=config,
        )
        
        return {
            "analysis": result["running_analysis"],
            "sources": result.get("sources_collected", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)