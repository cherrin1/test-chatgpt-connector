from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import uvicorn
import json
import uuid
import random
from datetime import datetime

app = FastAPI(title="MCP ConnexPay & FinTech Knowledge Server - ChatGPT Compatible", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Updated knowledge base with pre-loaded API data
KNOWLEDGE_BASE = [
    # ConnexPay Core Knowledge
    {
        "id": "connexpay_overview",
        "title": "ConnexPay: Unified B2B Payments Platform",
        "content": "ConnexPay is a pioneering B2B payments platform founded in 2017 that uniquely combines payment acceptance and virtual card issuing into a single integrated solution. The company holds a patent for 'Intelligent Payment Routing and Payment Generation' that enables real-time connection of incoming customer payments with outgoing supplier payments. ConnexPay serves travel agencies, e-commerce providers, online marketplaces, and other payment intermediaries with guaranteed lower merchant processing fees and automated reconciliation.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "B2B Payments", "type": "company"}
    },
    
    # Company Research Resources & Websites
    {
        "id": "company_research_websites",
        "title": "Company Research Websites and Databases",
        "content": "Key websites for company research and corporate information: 1) SEC.gov - US public company filings, 10-K reports, proxy statements, and insider trading data. 2) Companies House (UK) - UK company registration details, directors, and financial filings. 3) Crunchbase.com - startup funding, investor information, and company profiles. 4) PitchBook.com - private market data, M&A deals, and venture capital information. 5) Bloomberg Terminal/Markets - comprehensive financial data and company analytics. 6) Yahoo Finance - stock data, financial statements, and company news. 7) Google Finance - basic financial information and stock performance. 8) Morningstar.com - investment research and company analysis. 9) Hoovers (D&B) - company profiles and industry analysis. 10) LinkedIn Company Pages - employee count, company updates, and leadership information.",
        "url": "https://www.sec.gov/",
        "metadata": {"category": "Research Tools", "topic": "Company Research", "type": "websites"}
    },
    {
        "id": "government_business_databases",
        "title": "Government and Official Business Databases",
        "content": "Official government databases for company information: 1) SEC EDGAR Database - searchable database of US public company filings and reports. 2) Companies House Beta - UK company search with free basic company information. 3) DUNS Number Database - global business identifier system by Dun & Bradstreet. 4) USPTO Patent Database - patent filings and intellectual property information. 5) IRS Tax Exempt Organization Search - nonprofit organization details and tax documents. 6) System for Award Management (SAM.gov) - US government contractor database. 7) Better Business Bureau - business ratings and consumer complaints. 8) State Secretary of State Databases - corporation search by state (varies by state). 9) European Business Register - EU company information network. 10) World Bank Open Data - global economic and business statistics.",
        "url": "https://www.sec.gov/edgar/searchedgar/companysearch.html",
        "metadata": {"category": "Research Tools", "topic": "Government Databases", "type": "official_sources"}
    },
    {
        "id": "financial_data_platforms",
        "title": "Financial Data and Investment Platforms",
        "content": "Comprehensive financial data sources: 1) FactSet - institutional-grade financial data and analytics platform. 2) Refinitiv (formerly Thomson Reuters) - market data, news, and analytics. 3) S&P Capital IQ - financial intelligence and market data. 4) Moody's Analytics - credit ratings and financial analysis. 5) Fitch Ratings - credit ratings and financial research. 6) Zacks Investment Research - earnings estimates and stock analysis. 7) GuruFocus - value investing data and insider trading information. 8) Simply Wall St - visual company analysis and financial health scores. 9) Seeking Alpha - investment research and earnings analysis. 10) Alpha Architect - quantitative investment research and factor analysis.",
        "url": "https://www.factset.com/",
        "metadata": {"category": "Research Tools", "topic": "Financial Data", "type": "platforms"}
    },
    {
        "id": "business_intelligence_tools",
        "title": "Business Intelligence and Market Research Tools",
        "content": "Business intelligence and market research platforms: 1) IBISWorld - industry reports and market research. 2) Statista - market data, consumer insights, and industry statistics. 3) MarketResearch.com - comprehensive market research reports. 4) Frost & Sullivan - growth consulting and market intelligence. 5) Gartner - technology research and consulting. 6) Forrester Research - technology and business strategy research. 7) McKinsey Global Institute - economic research and business insights. 8) Deloitte Insights - business trend analysis and industry reports. 9) PwC Research - global business and economic analysis. 10) Boston Consulting Group Insights - strategic business research.",
        "url": "https://www.ibisworld.com/",
        "metadata": {"category": "Research Tools", "topic": "Market Research", "type": "intelligence"}
    },
    {
        "id": "startup_venture_databases",
        "title": "Startup and Venture Capital Databases",
        "content": "Startup and venture capital information sources: 1) AngelList (Wellfound) - startup jobs, funding, and investor information. 2) Crunchbase - startup funding rounds, acquisitions, and company profiles. 3) PitchBook - private market data and venture capital analytics. 4) CB Insights - startup intelligence and market research. 5) Mattermark (now part of Full Circle Insights) - startup growth metrics. 6) VentureSource - venture capital and private equity database. 7) Preqin - alternative investment data including VC and PE. 8) VC4A - African startup and venture capital database. 9) Dealroom.co - European startup and tech company database. 10) Tracxn - emerging company and startup intelligence platform.",
        "url": "https://wellfound.com/",
        "metadata": {"category": "Research Tools", "topic": "Startups & VC", "type": "venture_data"}
    },
    {
        "id": "industry_specific_databases",
        "title": "Industry-Specific Company Databases",
        "content": "Specialized industry databases: 1) Mergent Online - company financials and industry analysis. 2) Vault.com - company reviews and industry insights. 3) Glassdoor - employee reviews and company culture insights. 4) Indeed Company Reviews - employer ratings and salary information. 5) G2 - business software reviews and company information. 6) Capterra - software company profiles and user reviews. 7) TrustRadius - B2B technology company reviews. 8) BuiltIn - tech company profiles and startup information. 9) The Muse - company culture and career information. 10) Comparably - company culture and compensation data.",
        "url": "https://www.mergent.com/",
        "metadata": {"category": "Research Tools", "topic": "Industry Databases", "type": "specialized"}
    },
    {
        "id": "news_media_sources",
        "title": "Business News and Media Sources for Company Information",
        "content": "Key business news sources for company research: 1) Bloomberg - financial news and market data. 2) Reuters - global business news and company updates. 3) Wall Street Journal - financial journalism and company analysis. 4) Financial Times - international business news. 5) CNBC - business news and market coverage. 6) MarketWatch - stock market news and company earnings. 7) Barron's - investment news and stock analysis. 8) Forbes - business news and company rankings. 9) Fortune - business magazine and company profiles. 10) Business Insider - technology and business news. 11) TechCrunch - startup and technology company news. 12) VentureBeat - technology and startup coverage.",
        "url": "https://www.bloomberg.com/",
        "metadata": {"category": "Research Tools", "topic": "Business News", "type": "media_sources"}
    },
    {
        "id": "international_databases",
        "title": "International and Global Company Databases",
        "content": "Global company information sources: 1) Bureau van Dijk (Moody's Analytics) - global business information. 2) Orbis Database - comprehensive global company data. 3) Amadeus Database - European company information. 4) EMIS (Euromoney) - emerging markets company data. 5) OneSource (Infogroup) - global business database. 6) LexisNexis Corporate Affiliations - global corporate relationships. 7) Kompass - international business directory. 8) Uniworld Business Directory - global business contacts. 9) Export.gov - international trade and company information. 10) Trade.gov - US trade data and international business intelligence.",
        "url": "https://www.bvdinfo.com/",
        "metadata": {"category": "Research Tools", "topic": "International Data", "type": "global_databases"}
    },
    {
        "id": "free_company_search_tools",
        "title": "Free Company Search and Research Tools",
        "content": "Free resources for company research: 1) Google - basic company information and news search. 2) Wikipedia - company background and history. 3) LinkedIn - company profiles, employee information, and updates. 4) Facebook Business Pages - company information and customer reviews. 5) Yelp - local business information and customer reviews. 6) Yellow Pages - business directory and contact information. 7) Manta - small business directory and profiles. 8) ZoomInfo (limited free) - business contact information. 9) Apollo.io (limited free) - sales intelligence and company data. 10) Hunter.io (limited free) - email finder and company information. 11) Clearbit Connect - company and contact information. 12) Company websites and investor relations pages - primary source information.",
        "url": "https://www.google.com/",
        "metadata": {"category": "Research Tools", "topic": "Free Tools", "type": "free_resources"}
    },
    {
        "id": "specialized_fintech_databases",
        "title": "FinTech and Financial Services Databases",
        "content": "Specialized databases for FinTech and financial services companies: 1) Fintech Global - fintech company directory and analysis. 2) CB Insights FinTech - fintech market intelligence and company tracking. 3) Fintech Futures - fintech news and company profiles. 4) The Fintech Times - fintech industry news and company coverage. 5) FinTech Magazine - fintech company features and industry analysis. 6) PaymentsSource - payments industry news and company information. 7) American Banker - banking and fintech company coverage. 8) Bank Innovation - financial technology and innovation news. 9) Finovate - fintech demo and company showcase platform. 10) LendIt Fintech - marketplace lending and fintech company information. 11) InsurTech Global - insurance technology company database. 12) WealthTech Global - wealth management technology companies.",
        "url": "https://fintech.global/",
        "metadata": {"category": "Research Tools", "topic": "FinTech Databases", "type": "industry_specific"}
    },
    {
        "id": "connexpay_technology",
        "title": "ConnexPay's Patented Payment Technology",
        "content": "ConnexPay's core innovation is its patented Intelligent PayOuts technology (U.S. Patent No. 12,118,519) that automatically routes payments through optimal channels to maximize rebates and supplier acceptance. The platform accepts payments via credit cards, ACH, mobile wallets, and bank transfers, then instantly issues virtual cards to pay suppliers. This eliminates the traditional cash flow gap, transforming payment cycles from weeks to minutes while providing AI-powered fraud protection through integration with Kount (an Equifax company).",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Payment Technology", "type": "innovation"}
    },
    {
        "id": "connexpay_business_model",
        "title": "ConnexPay's Revenue and Business Model",
        "content": "ConnexPay operates on a unique business model that turns payment costs into revenue opportunities. The company generates revenue through competitive merchant processing fees, virtual card rebates (up to 20% uplift for clients), and intelligent payment routing. Founded by Bob Kaufman (former CFO at a top-5 US bank's Payment Services division), ConnexPay has raised $145 million across Series A, B, and C funding rounds. The company serves businesses with $5 million+ in annual payment volume and earned spot #704 on the Inc 5000 fastest-growing companies list in 2023.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Business Model", "type": "revenue"}
    },
    {
        "id": "connexpay_industries",
        "title": "ConnexPay's Target Industries and Solutions",
        "content": "ConnexPay primarily serves payment intermediaries including travel agencies, TMCs, MICE agencies, e-commerce providers, online marketplaces, ticket brokers, insurance companies, and warranty providers. The platform offers specialized solutions for leisure travel, business travel, and embedded payments for white-label resellers. ConnexPay's travel-focused innovations include the Global Travel card (eliminating cross-border and FX fees) and UATP partnerships. The company also launched ConnexPay Flex, a variable-rate virtual card with over 30 dynamic rates for enhanced supplier acceptance.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Industry Solutions", "type": "verticals"}
    },
    {
        "id": "connexpay_competitive_advantage",
        "title": "ConnexPay's Market Position and Competitive Advantage",
        "content": "ConnexPay is the first and only company to unify payment acceptance and virtual card issuing on a single platform with one contract and one reconciliation. This eliminates the need for separate banking relationships and reduces operational complexity. The company's competitive advantages include guaranteed lower merchant processing fees, real-time fund availability, automated reconciliation, industry-leading card rebates, and proprietary fraud protection. ConnexPay processes tens of millions in payments daily and was named Travel Innovator of the Year at Phocuswright 2023, distinguishing it from competitors like traditional payment processors and card issuers.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Competitive Analysis", "type": "advantage"}
    },
    
    # ConnexPay Full Service Payments from Presentation
    {
        "id": "connexpay_full_service_payments",
        "title": "ConnexPay Full Service Payments Platform",
        "content": "ConnexPay's Full Service Payments platform addresses the complexity of 'offline payments' where goods/services are separate from payment processing. Unlike online synchronous payments, offline payments require complex AP/AR processes, different payment options, critical data management, and exception handling. The platform provides a foundation of card, check, ACH, and RTP payments with custom data delivery, lifecycle payment management, payee support, and comprehensive risk management including ACH enrollment.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Full Service Payments", "type": "platform"}
    },
    {
        "id": "connexpay_insurance_market",
        "title": "ConnexPay's Insurance Market Opportunity",
        "content": "ConnexPay targets the massive insurance market with specific focus on non-medical insurance sectors. Key opportunities include Workers Compensation ($53.8B market, $16.6B B2B claims), Auto Personal ($316B market, $110.5B B2B claims), Auto Commercial ($61.6B market, $49.4B B2B claims), and Property insurance sectors. The platform addresses both B2B and B2C claim payments, with different complexity levels and payer ecosystems across various insurance verticals including travel, pet, and renters insurance.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Insurance Payments", "type": "market"}
    },
    {
        "id": "connexpay_ap_automation",
        "title": "ConnexPay's Approach to AP Automation",
        "content": "ConnexPay addresses the complex traditional AP process spanning spend management, procure-to-pay, and AP automation. The platform covers the entire workflow from spend category strategy and vendor selection through invoice management, payments, and remittance. Key differentiators include simplified integration compared to multiple ERP systems, managed funding reconciliation, enhanced branding/whitelabel capabilities, and comprehensive payment reporting. ConnexPay serves both direct enterprise clients and platform partners with different value propositions.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "AP Automation", "type": "solution"}
    },
    {
        "id": "connexpay_vertical_saas",
        "title": "ConnexPay's Vertical SaaS Strategy",
        "content": "ConnexPay targets vertical SaaS companies across multiple industries including legal practice management, auto shop management, salon management, construction management, community management, fitness management, property management, and landscape company management. The ideal customer profile includes vertical SaaS software companies with $100M+ annual spend, control over B2B USD-based spend, decision makers like Head of Payments/CFO/CPO/CTO, prior payment solution experience, and willingness to support payers with Tier 1 support.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Vertical SaaS", "type": "strategy"}
    },
    {
        "id": "connexpay_competitive_differentiation",
        "title": "ConnexPay's Five-Point Competitive Strategy",
        "content": "ConnexPay differentiates through five key pillars: 1) Strict SLAs ensuring reliability, speed, and minimizing disruptions with guaranteed timely transactions; 2) Branding capabilities empowering clients to offer branded services reducing payee confusion; 3) Flexible Funding enhancing cash flow management by aligning payment funding with client cash cycles; 4) Self Boarding allowing clients and payees to onboard at their own pace for efficient scaling; 5) Menu of Options providing diverse payment methods to meet varied customer needs and boost conversion rates.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Competitive Strategy", "type": "differentiation"}
    },
    {
        "id": "connexpay_roadmap_2025",
        "title": "ConnexPay's 2025 Product Roadmap",
        "content": "ConnexPay's 2025 roadmap includes Q2 deliverables: email/fax delivery, funding management, single card page; Q3: payment status tracking, sandbox readiness, ACH & check support, base supplier enablement, white label payee touch; Q4: decision engine, payee portal, self-service ACH enrollment (B2B), full payee management, content management, payer portal; Q2 2026: legacy integrations, ACH+, self-service ACH enrollment (B2C), multi-party B2C workflows. Vertical-specific features include OPT OUT networks, 835 EDI support, and clearing house integration.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Product Roadmap", "type": "development"}
    },
    {
        "id": "connexpay_organizational_structure",
        "title": "ConnexPay's Organizational Structure and Teams",
        "content": "ConnexPay's organizational structure includes: FSP Platform team (Chase) developing new payment automation platform, customer-facing API, content management tools, and managed delivery with printing; CxP Core team (Judson, Sandy, Julie) handling checks through MVB, minor funding tweaks; Operations team (Crystal) managing new functions like Supplier Enablement, Payee Support, Payment Operations, Agent Pay, and CRM tools; Sales/GTM team (Michael) defining the brand, website updates, one-pagers, and sales/CSM resources.",
        "url": "https://www.connexpay.com/",
        "metadata": {"category": "ConnexPay", "topic": "Organization", "type": "structure"}
    },
    
    # General FinTech Knowledge
    {
        "id": "fintech_payments_evolution",
        "title": "Evolution of FinTech Payment Systems",
        "content": "The fintech payments landscape has evolved from traditional banking systems to innovative digital solutions. Key developments include real-time payments, embedded finance, API-driven integrations, and AI-powered fraud detection. Modern payment systems emphasize user experience, security, and seamless integration. Technologies like blockchain, mobile wallets, and contactless payments have transformed how businesses and consumers transact. The industry continues to innovate with solutions like buy-now-pay-later (BNPL), cross-border payments, and cryptocurrency integration.",
        "url": "https://www.bis.org/topics/fintech/",
        "metadata": {"category": "FinTech", "topic": "Payment Evolution", "type": "industry_trends"}
    },
    {
        "id": "b2b_payments_market",
        "title": "B2B Payments Market and Trends",
        "content": "The B2B payments market represents a multi-trillion dollar opportunity with significant inefficiencies in traditional systems. Key trends include digitization of paper-based processes, adoption of virtual cards, real-time settlement, and embedded payment solutions. Challenges include complex reconciliation, multiple payment methods, regulatory compliance, and cross-border transactions. Solutions focus on automation, transparency, and integration with existing business systems. The market is driven by demand for better cash flow management, cost reduction, and improved supplier relationships.",
        "url": "https://www.mckinsey.com/industries/financial-services/our-insights/accelerating-winds-of-change-in-global-payments",
        "metadata": {"category": "FinTech", "topic": "B2B Payments", "type": "market_analysis"}
    },
    {
        "id": "virtual_cards_technology",
        "title": "Virtual Cards and Digital Payment Innovation",
        "content": "Virtual cards represent a significant innovation in digital payments, offering enhanced security, control, and tracking capabilities. These digital payment instruments provide unique card numbers for each transaction or vendor, reducing fraud risk and improving expense management. Virtual cards enable instant issuance, spending controls, and detailed transaction data. They're particularly valuable for B2B payments, online purchases, and expense management. The technology supports various use cases including supplier payments, employee expenses, and programmatic advertising spend.",
        "url": "https://www.visa.com/solutions/virtual-cards.html",
        "metadata": {"category": "FinTech", "topic": "Virtual Cards", "type": "technology"}
    },
    {
        "id": "payment_orchestration",
        "title": "Payment Orchestration and Intelligent Routing",
        "content": "Payment orchestration platforms manage multiple payment service providers, optimizing transaction routing based on factors like cost, success rates, and regional preferences. These systems provide unified APIs, reduce dependencies on single providers, and enable sophisticated payment strategies. Key features include automatic failover, currency optimization, and compliance management. Payment orchestration is crucial for global businesses needing to support multiple payment methods and currencies while maintaining high approval rates and minimizing costs.",
        "url": "https://stripe.com/payments/payment-orchestration",
        "metadata": {"category": "FinTech", "topic": "Payment Orchestration", "type": "infrastructure"}
    },
    {
        "id": "embedded_finance",
        "title": "Embedded Finance and Banking-as-a-Service",
        "content": "Embedded finance integrates financial services directly into non-financial platforms and applications. This includes embedded payments, lending, insurance, and banking services within software platforms. Banking-as-a-Service (BaaS) enables companies to offer financial products without becoming banks themselves. Key benefits include improved user experience, new revenue streams, and better customer retention. The trend is driven by API-first architectures, regulatory changes, and customer demand for seamless financial experiences.",
        "url": "https://www.mckinsey.com/industries/financial-services/our-insights/embedded-finance-what-every-ceo-needs-to-know",
        "metadata": {"category": "FinTech", "topic": "Embedded Finance", "type": "business_model"}
    },
    {
        "id": "fintech_compliance_regulation",
        "title": "FinTech Compliance and Regulatory Landscape",
        "content": "The fintech industry operates under complex regulatory frameworks covering payments, lending, data protection, and anti-money laundering. Key regulations include PCI DSS for payment security, PSD2 for open banking, GDPR for data protection, and various national banking regulations. Compliance requirements include customer verification, transaction monitoring, reporting, and audit trails. RegTech solutions help automate compliance processes, reduce costs, and ensure adherence to evolving regulations. The regulatory landscape continues to evolve with new digital asset regulations and cross-border payment rules.",
        "url": "https://www.bis.org/bcbs/publ/d518.htm",
        "metadata": {"category": "FinTech", "topic": "Compliance & Regulation", "type": "regulatory"}
    },
    {
        "id": "ai_fraud_detection",
        "title": "AI and Machine Learning in FinTech Fraud Detection",
        "content": "Artificial intelligence and machine learning have revolutionized fraud detection in financial services. These technologies analyze transaction patterns, user behavior, and risk factors in real-time to identify potentially fraudulent activities. AI-powered systems can adapt to new fraud patterns, reduce false positives, and improve detection accuracy. Key techniques include anomaly detection, neural networks, and ensemble methods. The technology enables automated decision-making, continuous learning, and scalable fraud prevention across various financial services.",
        "url": "https://www.mckinsey.com/industries/financial-services/our-insights/fighting-fraud-with-artificial-intelligence",
        "metadata": {"category": "FinTech", "topic": "AI Fraud Detection", "type": "technology"}
    },
    {
        "id": "open_banking_apis",
        "title": "Open Banking and API Economy in Financial Services",
        "content": "Open banking initiatives worldwide have created opportunities for fintech innovation through standardized APIs. These APIs enable third-party providers to access customer financial data and payment services with proper authorization. The open banking ecosystem facilitates account aggregation, payment initiation, and financial data analysis. Key benefits include increased competition, innovation, and consumer choice. The API economy has enabled new business models, partnerships, and financial services that weren't possible with traditional banking infrastructure.",
        "url": "https://www.openbanking.org.uk/",
        "metadata": {"category": "FinTech", "topic": "Open Banking", "type": "ecosystem"}
    },
    {
        "id": "cryptocurrency_digital_assets",
        "title": "Cryptocurrency and Digital Assets in FinTech",
        "content": "Cryptocurrencies and digital assets have introduced new paradigms in financial services, offering decentralized alternatives to traditional banking. Key innovations include blockchain-based payments, stablecoins for stable value transfer, and decentralized finance (DeFi) protocols. Central Bank Digital Currencies (CBDCs) represent government-issued digital currencies. The technology enables programmable money, smart contracts, and new financial primitives. However, adoption faces challenges including regulatory uncertainty, volatility, and scalability issues.",
        "url": "https://www.bis.org/publ/arpdf/ar2021e3.htm",
        "metadata": {"category": "FinTech", "topic": "Cryptocurrency", "type": "innovation"}
    },
    {
        "id": "fintech_funding_investment",
        "title": "FinTech Funding and Investment Trends",
        "content": "The fintech industry has attracted significant venture capital and institutional investment, with funding reaching record levels in recent years. Key investment areas include payments, lending, insurtech, wealthtech, and regulatory technology. Funding trends show increased focus on embedded finance, B2B solutions, and emerging markets. Investors value scalable business models, strong unit economics, and regulatory compliance. The funding environment has become more selective, emphasizing profitability and sustainable growth over pure user acquisition.",
        "url": "https://www.cbinsights.com/research/fintech-funding-trends/",
        "metadata": {"category": "FinTech", "topic": "Investment & Funding", "type": "market_data"}
    }
]

def get_company_research_resources():
    """Get company research resources"""
    research_resources = [doc for doc in KNOWLEDGE_BASE if doc["metadata"]["category"] == "Research Tools"]
    return research_resources

# MCP Protocol Models
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

def search_knowledge(query: str, limit: int = 10) -> List[SearchResult]:
    """Search through ConnexPay and FinTech knowledge base with intelligent matching"""
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
        
        # Enhanced fuzzy matching for ConnexPay, FinTech, and Research terms
        fuzzy_terms = {
            "connexpay": ["connexpay", "connex pay", "payment platform", "b2b payments", "virtual card"],
            "payment": ["payments", "pay", "transaction", "money", "finance"],
            "fintech": ["financial technology", "payments", "banking", "finance"],
            "b2b": ["business to business", "commercial", "enterprise", "corporate"],
            "research": ["company research", "business intelligence", "database", "information"],
            "company": ["corporation", "business", "firm", "enterprise", "organization"],
            "database": ["data", "information", "records", "directory", "search"],
            "api": ["integration", "software", "platform", "system"],
            "virtual": ["card", "digital", "electronic", "online"],
            "insurance": ["claims", "policy", "coverage", "risk"],
            "ap": ["accounts payable", "invoice", "supplier", "vendor"],
            "compliance": ["regulation", "kyc", "aml", "regulatory"],
            "fraud": ["security", "risk", "detection", "prevention"],
            "automation": ["automatic", "process", "workflow", "efficiency"],
            "sec": ["securities", "filing", "edgar", "10-k", "financial"],
            "startup": ["venture", "funding", "investment", "entrepreneur"],
            "news": ["media", "journalism", "reporting", "coverage"]
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
        "service": "MCP ConnexPay & FinTech Knowledge Server - ChatGPT Compatible",
        "knowledge_items": len(KNOWLEDGE_BASE),
        "categories": list(set(doc["metadata"]["category"] for doc in KNOWLEDGE_BASE)),
        "focus": "ConnexPay, Financial Technology, and Company Research Resources",
        "chatgpt_compatible": True
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint - ChatGPT compatible (resources only)"""
    try:
        json_data = await request.json()
        mcp_request = MCPRequest(**json_data)
        
        print(f"Processing method: {mcp_request.method}")
        
        if mcp_request.method == "initialize":
            return MCPResponse(
                id=mcp_request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "resources": {},
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "mcp-connexpay-fintech-server",
                        "version": "1.0.0"
                    }
                }
            ).dict()
        
        elif mcp_request.method == "resources/list":
            # Return all knowledge base items as resources
            resources = []
            
            # Add knowledge base items
            for doc in KNOWLEDGE_BASE:
                resources.append({
                    "uri": f"knowledge://{doc['id']}",
                    "name": doc["title"],
                    "description": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    "mimeType": "text/plain"
                })
            
            return MCPResponse(
                id=mcp_request.id,
                result={"resources": resources}
            ).dict()
        
        elif mcp_request.method == "resources/read":
            uri = mcp_request.params.get("uri", "")
            
            if uri.startswith("knowledge://"):
                doc_id = uri.replace("knowledge://", "")
                result = fetch_knowledge(doc_id)
                
                if result:
                    return MCPResponse(
                        id=mcp_request.id,
                        result={
                            "contents": [{
                                "uri": uri,
                                "mimeType": "text/plain",
                                "text": result.text
                            }]
                        }
                    ).dict()
            
            return MCPResponse(
                id=mcp_request.id,
                error={
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            ).dict()
        
        elif mcp_request.method == "tools/list":
            return MCPResponse(
                id=mcp_request.id,
                result={
                    "tools": [
                        {
                            "name": "search",
                            "description": "Search through ConnexPay and FinTech knowledge base covering B2B payments, virtual cards, AP automation, and financial technology",
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
                            "description": "Fetch complete ConnexPay or FinTech knowledge article by ID",
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

# Handle GET requests for notifications
@app.get("/mcp")
async def mcp_get_endpoint():
    """Handle GET requests for MCP notifications"""
    return {"error": "MCP server requires POST requests for JSON-RPC calls"}

@app.get("/browse")
async def browse_knowledge():
    """Browse all available knowledge"""
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
    
    return {
        "categories": categories, 
        "total_items": len(KNOWLEDGE_BASE),
        "focus": "ConnexPay, Financial Technology, and Company Research Resources",
        "chatgpt_compatible": True
    }

@app.get("/research_resources")
async def get_research_resources():
    """Get all company research resources"""
    resources = get_company_research_resources()
    return {
        "research_resources": [
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "topic": r["metadata"]["topic"]
            } for r in resources
        ],
        "total_resources": len(resources)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)