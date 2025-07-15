from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import uuid

app = FastAPI(title="Simple MCP Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data store - replace with your actual data source
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_1",
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It involves algorithms that can identify patterns, make predictions, and improve performance over time.",
        "url": "https://example.com/ml-intro",
        "metadata": {"category": "technology", "author": "AI Expert"}
    },
    {
        "id": "doc_2", 
        "title": "Climate Change Overview",
        "content": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, human activities since the 1800s have been the main driver of climate change, primarily due to burning fossil fuels.",
        "url": "https://example.com/climate",
        "metadata": {"category": "environment", "author": "Climate Scientist"}
    },
    {
        "id": "doc_3",
        "title": "Remote Work Best Practices",
        "content": "Remote work has become increasingly common. Key practices include setting up a dedicated workspace, maintaining regular communication with team members, establishing clear boundaries between work and personal time, and using collaborative tools effectively.",
        "url": "https://example.com/remote-work",
        "metadata": {"category": "business", "author": "HR Specialist"}
    },
    {
        "id": "doc_4",
        "title": "Healthy Cooking Tips",
        "content": "Healthy cooking involves using fresh ingredients, reducing processed foods, controlling portion sizes, and using cooking methods that preserve nutrients. Steaming, grilling, and baking are healthier alternatives to frying.",
        "url": "https://example.com/healthy-cooking",
        "metadata": {"category": "health", "author": "Nutritionist"}
    }
]

# MCP Protocol Models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    id: str
    title: str
    text: str
    url: str

class FetchResult(BaseModel):
    id: str
    title: str
    text: str
    url: str
    metadata: Optional[Dict[str, Any]] = None

def search_documents(query: str, limit: int = 10) -> List[SearchResult]:
    """Search through documents based on query"""
    query_lower = query.lower()
    results = []
    
    for doc in SAMPLE_DOCUMENTS:
        # Simple text matching - you can implement more sophisticated search
        if (query_lower in doc["title"].lower() or 
            query_lower in doc["content"].lower() or
            query_lower in doc["metadata"].get("category", "").lower()):
            
            # Create a snippet from the content
            content = doc["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            
            results.append(SearchResult(
                id=doc["id"],
                title=doc["title"],
                text=content,
                url=doc["url"]
            ))
    
    return results[:limit]

def fetch_document(doc_id: str) -> Optional[FetchResult]:
    """Fetch full document by ID"""
    for doc in SAMPLE_DOCUMENTS:
        if doc["id"] == doc_id:
            return FetchResult(
                id=doc["id"],
                title=doc["title"],
                text=doc["content"],
                url=doc["url"],
                metadata=doc["metadata"]
            )
    return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MCP Server"}

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP endpoint"""
    try:
        if request.method == "tools/list":
            # Return available tools
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search through documents",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "fetch",
                            "description": "Fetch full document by ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Document ID to fetch"
                                    }
                                },
                                "required": ["id"]
                            }
                        }
                    ]
                }
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            if tool_name == "search":
                query = arguments.get("query", "")
                if not query:
                    raise HTTPException(status_code=400, detail="Query parameter required")
                
                results = search_documents(query)
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps([result.dict() for result in results], indent=2)
                            }
                        ]
                    }
                )
            
            elif tool_name == "fetch":
                doc_id = arguments.get("id", "")
                if not doc_id:
                    raise HTTPException(status_code=400, detail="ID parameter required")
                
                result = fetch_document(doc_id)
                if not result:
                    return MCPResponse(
                        id=request.id,
                        result={
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Document with ID '{doc_id}' not found"
                                }
                            ]
                        }
                    )
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result.dict(), indent=2)
                            }
                        ]
                    }
                )
            
            else:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                )
        
        elif request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "simple-mcp-server",
                        "version": "1.0.0"
                    }
                }
            )
        
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Unknown method: {request.method}"
                }
            )
    
    except Exception as e:
        return MCPResponse(
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )

# For testing the search functionality directly
@app.get("/test/search")
async def test_search(q: str = "machine learning"):
    """Test endpoint for search functionality"""
    results = search_documents(q)
    return {"query": q, "results": [r.dict() for r in results]}

@app.get("/test/fetch")
async def test_fetch(id: str = "doc_1"):
    """Test endpoint for fetch functionality"""
    result = fetch_document(id)
    return {"document_id": id, "result": result.dict() if result else None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
