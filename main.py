from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uvicorn
import logging
import json

# ──────────────── FastAPI App Setup ──────────────── #

app = FastAPI(
    title="MCP ConnexPay & FinTech Knowledge Server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ──────────────── Logging Setup ──────────────── #

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# ──────────────── Knowledge Base ──────────────── #

from knowledge_base import KNOWLEDGE_BASE

# ──────────────── Models ──────────────── #

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
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

# ──────────────── Search Logic ──────────────── #

def search_knowledge(query: str, limit: int = 10) -> List[SearchResult]:
    query_lower = query.lower()
    results = []

    for doc in KNOWLEDGE_BASE:
        score = 0
        title = doc["title"].lower()
        content = doc["content"].lower()

        if query_lower in title:
            score += 10
        if query_lower in content:
            score += 5
        if query_lower in doc["metadata"].get("topic", "").lower():
            score += 3
        if score == 0:
            continue

        snippet = next((s for s in content.split('. ') if query_lower in s), content.split('. ')[0])
        snippet = snippet.strip()[:300] + "..." if len(snippet) > 300 else snippet

        results.append(SearchResult(
            id=doc["id"],
            title=doc["title"],
            text=snippet,
            url=doc["url"]
        ))

    results.sort(key=lambda r: r.text.count(query_lower), reverse=True)
    return results[:limit]

def fetch_knowledge(doc_id: str) -> Optional[FetchResult]:
    for doc in KNOWLEDGE_BASE:
        if doc["id"] == doc_id:
            return FetchResult(
                id=doc["id"],
                title=doc["title"],
                text=doc["content"],
                url=doc["url"],
                metadata=doc.get("metadata", {})
            )
    return None

# ──────────────── Endpoints ──────────────── #

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "knowledge_items": len(KNOWLEDGE_BASE),
        "categories": list({doc["metadata"]["category"] for doc in KNOWLEDGE_BASE}),
        "chatgpt_compatible": True
    }

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        try:
            json_data = await request.json()
            mcp_req = MCPRequest(**json_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid MCP JSON-RPC request")

        logger.info(f"Received MCP method: {mcp_req.method}")

        if mcp_req.method == "initialize":
            return MCPResponse(id=mcp_req.id, result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"resources": {}, "tools": {}},
                "serverInfo": {"name": "mcp-connexpay-fintech-server", "version": "1.0.0"}
            }).dict()

        elif mcp_req.method == "notifications/initialized":
            return MCPResponse(id=mcp_req.id, result={
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat()
            }).dict()

        elif mcp_req.method == "resources/list":
            resources = [{
                "uri": f"knowledge://{doc['id']}",
                "name": doc["title"],
                "description": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                "type": "resource",
                "mimeType": "text/plain"
            } for doc in KNOWLEDGE_BASE]

            return MCPResponse(id=mcp_req.id, result={"resources": resources}).dict()

        elif mcp_req.method == "resources/read":
            uri = mcp_req.params.get("uri", "")
            if uri.startswith("knowledge://"):
                doc_id = uri.split("knowledge://")[1]
                result = fetch_knowledge(doc_id)
                if result:
                    return MCPResponse(id=mcp_req.id, result={
                        "contents": [{
                            "uri": uri,
                            "type": "text",
                            "mimeType": "text/plain",
                            "text": result.text
                        }]
                    }).dict()
            return MCPResponse(id=mcp_req.id, error={
                "code": -32602, "message": f"Resource not found: {uri}"
            }).dict()

        elif mcp_req.method == "tools/list":
            return MCPResponse(id=mcp_req.id, result={
                "tools": [
                    {
                        "name": "search",
                        "description": "Search through ConnexPay and FinTech knowledge base.",
                        "inputSchema": {"type": "object", "properties": {
                            "query": {"type": "string", "description": "Search query string"}
                        }, "required": ["query"]}
                    },
                    {
                        "name": "fetch",
                        "description": "Fetch full article by ID.",
                        "inputSchema": {"type": "object", "properties": {
                            "id": {"type": "string", "description": "Document ID to fetch"}
                        }, "required": ["id"]}
                    }
                ]
            }).dict()

        elif mcp_req.method == "tools/call":
            tool = mcp_req.params.get("name")
            args = mcp_req.params.get("arguments", {})
            if tool == "search":
                query = args.get("query", "").strip()
                if not query:
                    raise ValueError("Missing search query")
                results = search_knowledge(query)
                return MCPResponse(id=mcp_req.id, result={"content": [{
                    "type": "text",
                    "text": json.dumps([r.dict() for r in results], indent=2)
                }]}).dict()
            elif tool == "fetch":
                doc_id = args.get("id", "")
                result = fetch_knowledge(doc_id)
                if not result:
                    return MCPResponse(id=mcp_req.id, result={"content": [{
                        "type": "text",
                        "text": json.dumps({"error": "Document not found"})
                    }]}).dict()
                return MCPResponse(id=mcp_req.id, result={"content": [{
                    "type": "text",
                    "text": json.dumps(result.dict(), indent=2)
                }]}).dict()
            else:
                raise ValueError(f"Unknown tool: {tool}")

        raise ValueError(f"Unknown method: {mcp_req.method}")

    except Exception as e:
        logger.exception("Unhandled exception in /mcp")
        return JSONResponse(status_code=500, content={
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            "id": None
        })

@app.get("/mcp")
async def reject_get():
    return JSONResponse(status_code=405, content={
        "error": "MCP requires POST requests"
    })

@app.get("/browse")
async def browse_knowledge():
    by_category = {}
    for doc in KNOWLEDGE_BASE:
        category = doc["metadata"]["category"]
        by_category.setdefault(category, []).append({
            "id": doc["id"],
            "title": doc["title"],
            "topic": doc["metadata"]["topic"]
        })
    return {
        "categories": by_category,
        "total_items": len(KNOWLEDGE_BASE)
    }

@app.get("/research_resources")
async def get_research_docs():
    return {
        "research_resources": [
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "topic": r["metadata"]["topic"]
            } for r in KNOWLEDGE_BASE if r["metadata"]["category"] == "Research Tools"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
