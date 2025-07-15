from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import uuid
import random

app = FastAPI(title="MCP Knowledge Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive knowledge base covering various domains
KNOWLEDGE_BASE = [
    {
        "id": "mcp_overview",
        "title": "Model Context Protocol (MCP) Overview",
        "content": "Model Context Protocol (MCP) is an open standard for connecting AI assistants to data sources and tools. It enables secure, controlled access to resources like databases, APIs, and local files through a standardized interface. MCP uses JSON-RPC 2.0 for communication and supports both local and remote server deployments. Key components include servers (expose resources), clients (AI applications), and transports (communication layer).",
        "url": "https://docs.anthropic.com/en/docs/mcp/overview",
        "metadata": {"category": "AI/ML", "topic": "MCP", "type": "protocol"}
    },
    {
        "id": "mcp_tools",
        "title": "MCP Tools and Capabilities",
        "content": "MCP servers can expose three types of capabilities: Tools (functions the AI can call), Resources (data the AI can access), and Prompts (templates for interactions). Tools are stateless functions with defined input schemas. Resources provide structured data access with URI-based addressing. The protocol supports authentication, session management, and real-time updates through server-sent events.",
        "url": "https://docs.anthropic.com/en/docs/mcp/concepts",
        "metadata": {"category": "AI/ML", "topic": "MCP", "type": "capabilities"}
    },
    {
        "id": "quantum_computing",
        "title": "Quantum Computing Fundamentals",
        "content": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information. Unlike classical bits, quantum bits (qubits) can exist in multiple states simultaneously. Key algorithms include Shor's algorithm for factoring and Grover's algorithm for search. Current limitations include decoherence, error rates, and the need for extremely low temperatures. Major players include IBM, Google, and Rigetti.",
        "url": "https://quantum-computing.ibm.com/",
        "metadata": {"category": "Technology", "topic": "Quantum", "type": "science"}
    },
    {
        "id": "blockchain_consensus",
        "title": "Blockchain Consensus Mechanisms",
        "content": "Consensus mechanisms ensure agreement in distributed blockchain networks. Proof of Work (PoW) requires computational effort, used by Bitcoin. Proof of Stake (PoS) selects validators based on stake, more energy-efficient. Other mechanisms include Delegated Proof of Stake (DPoS), Proof of Authority (PoA), and Byzantine Fault Tolerance variants. Each has trade-offs between security, scalability, and decentralization.",
        "url": "https://ethereum.org/en/developers/docs/consensus-mechanisms/",
        "metadata": {"category": "Technology", "topic": "Blockchain", "type": "consensus"}
    },
    {
        "id": "neural_architectures",
        "title": "Modern Neural Network Architectures",
        "content": "Transformer architecture revolutionized NLP with self-attention mechanisms, enabling models like GPT and BERT. Convolutional Neural Networks (CNNs) excel at image processing with feature detection layers. Recurrent Neural Networks (RNNs) and LSTMs handle sequential data. Recent innovations include Vision Transformers (ViTs), diffusion models for generation, and mixture of experts (MoE) for scaling.",
        "url": "https://arxiv.org/abs/1706.03762",
        "metadata": {"category": "AI/ML", "topic": "Neural Networks", "type": "architecture"}
    },
    {
        "id": "microservices_patterns",
        "title": "Microservices Design Patterns",
        "content": "Microservices architecture decomposes applications into independent services. Key patterns include API Gateway for routing, Circuit Breaker for fault tolerance, Service Discovery for location transparency, and Event Sourcing for state management. Challenges include distributed system complexity, data consistency, and network latency. Tools like Kubernetes, Docker, and service meshes help manage deployments.",
        "url": "https://microservices.io/patterns/",
        "metadata": {"category": "Software", "topic": "Architecture", "type": "patterns"}
    },
    {
        "id": "climate_science",
        "title": "Climate Change Science and Impacts",
        "content": "Climate change results from increased greenhouse gas concentrations, primarily CO2 from fossil fuel combustion. Global average temperatures have risen 1.1°C since pre-industrial times. Impacts include sea level rise, extreme weather events, ecosystem disruption, and agricultural changes. Mitigation strategies involve renewable energy transition, carbon capture, and policy interventions. Adaptation includes infrastructure resilience and ecosystem restoration.",
        "url": "https://www.ipcc.ch/reports/",
        "metadata": {"category": "Environment", "topic": "Climate", "type": "science"}
    },
    {
        "id": "space_exploration",
        "title": "Modern Space Exploration Technologies",
        "content": "Space exploration has advanced with reusable rockets (SpaceX Falcon 9), Mars rovers (Perseverance, Curiosity), and the James Webb Space Telescope. Private companies like SpaceX, Blue Origin, and Virgin Galactic are commercializing space access. Future missions target Moon bases, Mars colonization, and asteroid mining. Technologies include ion propulsion, nuclear rockets, and in-situ resource utilization.",
        "url": "https://www.nasa.gov/missions/",
        "metadata": {"category": "Science", "topic": "Space", "type": "exploration"}
    },
    {
        "id": "crispr_gene_editing",
        "title": "CRISPR Gene Editing Technology",
        "content": "CRISPR-Cas9 enables precise DNA editing by cutting specific sequences and allowing insertions or deletions. Applications include treating genetic diseases, improving crops, and developing disease models. Recent advances include base editing, prime editing, and epigenome editing. Ethical considerations involve germline editing, equity of access, and unintended consequences. Clinical trials are ongoing for sickle cell disease and cancer treatments.",
        "url": "https://www.broadinstitute.org/what-broad/areas-focus/project-spotlight/questions-and-answers-about-crispr",
        "metadata": {"category": "Biotechnology", "topic": "Gene Editing", "type": "technology"}
    },
    {
        "id": "renewable_energy",
        "title": "Renewable Energy Technologies and Trends",
        "content": "Renewable energy sources include solar photovoltaics, wind turbines, hydroelectric, geothermal, and biomass. Solar costs have dropped 90% since 2010. Wind power capacity grows annually. Energy storage solutions like lithium-ion batteries and pumped hydro enable grid stability. Smart grids integrate distributed generation. Challenges include intermittency, grid infrastructure, and material supply chains.",
        "url": "https://www.irena.org/",
        "metadata": {"category": "Energy", "topic": "Renewable", "type": "technology"}
    },
    {
        "id": "cybersecurity_threats",
        "title": "Modern Cybersecurity Threat Landscape",
        "content": "Cybersecurity threats include ransomware, phishing, supply chain attacks, and state-sponsored campaigns. AI enables both better defenses and more sophisticated attacks. Zero-trust architecture assumes no inherent trust. Key defenses include multi-factor authentication, encryption, endpoint detection, and security awareness training. Emerging concerns involve IoT security, cloud vulnerabilities, and quantum computing's impact on cryptography.",
        "url": "https://www.cisa.gov/cybersecurity",
        "metadata": {"category": "Security", "topic": "Cybersecurity", "type": "threats"}
    },
    {
        "id": "containerization",
        "title": "Container Technologies and Orchestration",
        "content": "Containerization packages applications with dependencies for consistent deployment. Docker popularized container adoption. Kubernetes orchestrates container clusters with features like auto-scaling, service discovery, and rolling updates. Container registries store images. Security considerations include image scanning, runtime protection, and network policies. Alternative orchestrators include Docker Swarm and cloud-native solutions.",
        "url": "https://kubernetes.io/docs/concepts/",
        "metadata": {"category": "DevOps", "topic": "Containers", "type": "technology"}
    },
    {
        "id": "edge_computing",
        "title": "Edge Computing Architecture and Applications",
        "content": "Edge computing processes data closer to sources, reducing latency and bandwidth usage. Applications include IoT sensors, autonomous vehicles, and real-time analytics. Edge devices range from gateways to micro data centers. Key challenges involve resource constraints, connectivity, and management complexity. 5G networks enable new edge use cases. Major providers include AWS Wavelength, Azure Edge, and Google Distributed Cloud.",
        "url": "https://www.ibm.com/cloud/what-is-edge-computing",
        "metadata": {"category": "Technology", "topic": "Edge Computing", "type": "architecture"}
    },
    {
        "id": "financial_technology",
        "title": "Financial Technology Innovation",
        "content": "FinTech innovations include digital payments, blockchain currencies, robo-advisors, and peer-to-peer lending. Central Bank Digital Currencies (CBDCs) are being explored globally. Open banking APIs enable third-party financial services. RegTech automates compliance. Challenges involve regulation, security, and financial inclusion. Key players include traditional banks, tech companies, and specialized startups.",
        "url": "https://www.bis.org/topics/fintech/",
        "metadata": {"category": "Finance", "topic": "FinTech", "type": "innovation"}
    },
    {
        "id": "materials_science",
        "title": "Advanced Materials and Nanotechnology",
        "content": "Advanced materials include graphene, carbon nanotubes, metamaterials, and smart materials. Nanotechnology enables precise control at atomic scales. Applications span electronics, medicine, energy, and manufacturing. Graphene offers exceptional electrical and mechanical properties. Shape-memory alloys change properties with temperature. Challenges include manufacturing scalability, safety assessment, and cost reduction.",
        "url": "https://www.nist.gov/topics/materials-science",
        "metadata": {"category": "Science", "topic": "Materials", "type": "nanotechnology"}
    },
    {
        "id": "data_privacy",
        "title": "Data Privacy and Protection Regulations",
        "content": "Data privacy regulations like GDPR, CCPA, and emerging laws worldwide establish user rights and organization obligations. Key principles include consent, purpose limitation, data minimization, and transparency. Technical measures include encryption, anonymization, and differential privacy. Privacy-by-design integrates protection into system development. Challenges involve cross-border data flows, AI model training, and balancing innovation with protection.",
        "url": "https://gdpr.eu/",
        "metadata": {"category": "Legal/Policy", "topic": "Privacy", "type": "regulation"}
    },
    {
        "id": "serverless_computing",
        "title": "Serverless Computing and Function-as-a-Service",
        "content": "Serverless computing abstracts infrastructure management, automatically scaling functions based on demand. Benefits include reduced operational overhead, cost efficiency, and faster development cycles. Limitations include cold starts, vendor lock-in, and debugging complexity. Popular platforms include AWS Lambda, Azure Functions, and Google Cloud Functions. Use cases span APIs, data processing, and event-driven architectures.",
        "url": "https://aws.amazon.com/serverless/",
        "metadata": {"category": "Cloud", "topic": "Serverless", "type": "computing"}
    },
    {
        "id": "augmented_reality",
        "title": "Augmented and Virtual Reality Technologies",
        "content": "AR overlays digital content on the real world, while VR creates immersive virtual environments. Key technologies include computer vision, spatial tracking, and display systems. Applications span gaming, education, healthcare, and industrial training. Challenges involve hardware limitations, user experience, and content creation costs. Emerging trends include mixed reality (MR) and extended reality (XR) ecosystems.",
        "url": "https://www.oculus.com/",
        "metadata": {"category": "Technology", "topic": "AR/VR", "type": "immersive"}
    },
    {
        "id": "sustainable_computing",
        "title": "Green Computing and Sustainable Technology",
        "content": "Green computing minimizes environmental impact through energy-efficient hardware, software optimization, and responsible disposal. Data centers consume 1% of global electricity. Strategies include renewable energy adoption, efficient cooling, and workload optimization. Carbon-aware computing schedules tasks based on grid carbon intensity. Circular economy principles promote device longevity and material recovery.",
        "url": "https://www.epa.gov/greenerproducts/recommendations-green-computing",
        "metadata": {"category": "Sustainability", "topic": "Green IT", "type": "environmental"}
    },
    {
        "id": "api_design",
        "title": "API Design Principles and Best Practices",
        "content": "RESTful API design follows principles like statelessness, uniform interface, and resource-based URLs. GraphQL enables flexible data fetching. gRPC provides efficient binary communication. Design considerations include versioning, authentication, rate limiting, and documentation. OpenAPI specifications standardize descriptions. Best practices emphasize consistency, error handling, and developer experience.",
        "url": "https://restfulapi.net/",
        "metadata": {"category": "Software", "topic": "APIs", "type": "design"}
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

def search_knowledge(query: str, limit: int = 10) -> List[SearchResult]:
    """Search through knowledge base with intelligent matching"""
    query_lower = query.lower()
    results = []
    
    # Score documents based on relevance
    scored_docs = []
    
    for doc in KNOWLEDGE_BASE:
        score = 0
        
        # Title match (highest weight)
        if query_lower in doc["title"].lower():
            score += 10
        
        # Content match
        if query_lower in doc["content"].lower():
            score += 5
        
        # Category match
        if query_lower in doc["metadata"].get("category", "").lower():
            score += 3
        
        # Topic match
        if query_lower in doc["metadata"].get("topic", "").lower():
            score += 3
        
        # Type match
        if query_lower in doc["metadata"].get("type", "").lower():
            score += 2
        
        # Fuzzy matching for common terms
        fuzzy_terms = {
            "ai": ["artificial intelligence", "machine learning", "neural", "model"],
            "ml": ["machine learning", "neural", "algorithm", "model"],
            "tech": ["technology", "computing", "software", "system"],
            "security": ["cybersecurity", "encryption", "privacy", "protection"],
            "cloud": ["serverless", "container", "kubernetes", "microservices"],
            "science": ["quantum", "climate", "space", "materials", "gene"],
            "web": ["api", "rest", "graphql", "microservices"],
            "energy": ["renewable", "solar", "wind", "sustainable", "green"],
            "data": ["privacy", "blockchain", "database", "analytics"]
        }
        
        for term, related in fuzzy_terms.items():
            if term in query_lower:
                for related_term in related:
                    if related_term in doc["content"].lower() or related_term in doc["title"].lower():
                        score += 1
        
        if score > 0:
            scored_docs.append((doc, score))
    
    # Sort by score and create results
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    for doc, score in scored_docs[:limit]:
        # Create intelligent snippet
        content = doc["content"]
        
        # Try to find the most relevant sentence containing the query
        sentences = content.split('. ')
        best_sentence = ""
        
        for sentence in sentences:
            if query_lower in sentence.lower():
                best_sentence = sentence + "."
                break
        
        # If no exact match, use first sentence + context
        if not best_sentence:
            best_sentence = sentences[0] + "."
        
        # Ensure snippet isn't too long
        if len(best_sentence) > 300:
            best_sentence = best_sentence[:300] + "..."
        
        results.append(SearchResult(
            id=doc["id"],
            title=doc["title"],
            text=best_sentence,
            url=doc["url"]
        ))
    
    # If no results, return some random relevant documents
    if not results:
        random_docs = random.sample(KNOWLEDGE_BASE, min(3, len(KNOWLEDGE_BASE)))
        for doc in random_docs:
            snippet = doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
            results.append(SearchResult(
                id=doc["id"],
                title=doc["title"],
                text=snippet,
                url=doc["url"]
            ))
    
    return results

def fetch_knowledge(doc_id: str) -> Optional[FetchResult]:
    """Fetch full knowledge document by ID"""
    for doc in KNOWLEDGE_BASE:
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
    return {
        "status": "healthy", 
        "service": "MCP Knowledge Server",
        "knowledge_items": len(KNOWLEDGE_BASE),
        "categories": list(set(doc["metadata"]["category"] for doc in KNOWLEDGE_BASE))
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint with better error handling"""
    try:
        # Get raw body for debugging
        body = await request.body()
        print(f"Received request body: {body}")
        
        # Try to parse JSON
        try:
            json_data = await request.json()
            print(f"Parsed JSON: {json_data}")
        except Exception as e:
            print(f"JSON parse error: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    },
                    "id": None
                }
            )
        
        # Convert to MCPRequest
        try:
            mcp_request = MCPRequest(**json_data)
        except Exception as e:
            print(f"MCP Request validation error: {e}")
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": f"Invalid params: {str(e)}"
                    },
                    "id": json_data.get("id")
                }
            )
        
        print(f"Processing method: {mcp_request.method}")
        
        if mcp_request.method == "initialize":
            return MCPResponse(
                id=mcp_request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "mcp-knowledge-server",
                        "version": "1.0.0"
                    }
                }
            ).dict()
        
        elif mcp_request.method == "tools/list":
            return MCPResponse(
                id=mcp_request.id,
                result={
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search through comprehensive knowledge base covering AI/ML, technology, science, and more",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query string"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "fetch",
                            "description": "Fetch complete knowledge article by ID",
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
            ).dict()
        
        elif mcp_request.method == "tools/call":
            params = mcp_request.params or {}
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            print(f"Tool call: {tool_name}, args: {arguments}")
            
            if tool_name == "search":
                query = arguments.get("query", "")
                if not query:
                    return MCPResponse(
                        id=mcp_request.id,
                        error={
                            "code": -32602,
                            "message": "Query parameter required"
                        }
                    ).dict()
                
                results = search_knowledge(query)
                search_results = [
                    {
                        "id": result.id,
                        "title": result.title,
                        "text": result.text,
                        "url": result.url
                    }
                    for result in results
                ]
                
                return MCPResponse(
                    id=mcp_request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(search_results, indent=2)
                            }
                        ]
                    }
                ).dict()
            
            elif tool_name == "fetch":
                doc_id = arguments.get("id", "")
                if not doc_id:
                    return MCPResponse(
                        id=mcp_request.id,
                        error={
                            "code": -32602,
                            "message": "ID parameter required"
                        }
                    ).dict()
                
                result = fetch_knowledge(doc_id)
                if not result:
                    return MCPResponse(
                        id=mcp_request.id,
                        result={
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({"error": f"Document with ID '{doc_id}' not found"})
                                }
                            ]
                        }
                    ).dict()
                
                fetch_result = {
                    "id": result.id,
                    "title": result.title,
                    "text": result.text,
                    "url": result.url,
                    "metadata": result.metadata
                }
                
                return MCPResponse(
                    id=mcp_request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(fetch_result, indent=2)
                            }
                        ]
                    }
                ).dict()
            
            else:
                return MCPResponse(
                    id=mcp_request.id,
                    error={
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                ).dict()
        
        else:
            return MCPResponse(
                id=mcp_request.id,
                error={
                    "code": -32601,
                    "message": f"Unknown method: {mcp_request.method}"
                }
            ).dict()
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": None
            }
        )

# Handle GET requests for notifications (required by MCP spec)
@app.get("/mcp")
async def mcp_get_endpoint():
    """Handle GET requests for MCP notifications"""
    return {"error": "MCP server requires POST requests for JSON-RPC calls"}

# Handle OPTIONS for CORS preflight
@app.options("/mcp")
async def mcp_options():
    """Handle CORS preflight requests"""
    return {"status": "ok"}

# Enhanced testing endpoints
@app.get("/test/search")
async def test_search(q: str = "artificial intelligence"):
    """Test endpoint for search functionality"""
    results = search_knowledge(q)
    return {"query": q, "results": [r.dict() for r in results]}

@app.get("/test/fetch")
async def test_fetch(id: str = "mcp_overview"):
    """Test endpoint for fetch functionality"""
    result = fetch_knowledge(id)
    return {"knowledge_id": id, "result": result.dict() if result else None}

@app.get("/browse")
async def browse_knowledge():
    """Browse all available knowledge categories and topics"""
    categories = {}
    for doc in KNOWLEDGE_BASE:
        category = doc["metadata"]["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": doc["id"],
            "title": doc["title"],
            "topic": doc["metadata"]["topic"]
        })
    return {"categories": categories, "total_items": len(KNOWLEDGE_BASE)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)