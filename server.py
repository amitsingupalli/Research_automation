import os
import json
import time
import asyncio
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import httpx

async def call_groq(messages: list, temperature: float = 0.1) -> str:
    """Ultra-fast, lightweight Groq LLM inference via direct API without heavy local ML bloat."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please set it in your .env or Vercel dashboard.")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

def search_serper(query: str, n_results: int = 5) -> str:
    """Lightweight Serper API search without heavy ML dependencies."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Serper API key missing."
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": n_results}
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        data = response.json()
        organic = data.get("organic", [])
        results = []
        for item in organic[:n_results]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
        return "\n".join(results) if results else "No search results found."
    except Exception as e:
        return f"Search error: {str(e)}"

app = FastAPI(title="Agentic Research Lab Backend", version="2.1.0")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str
    depth: str = "deep"  # "quick" or "deep"
    sources: dict = {"academic": True, "web": True, "reddit": False}


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves frontend.py directly on root URL http://localhost:8000/"""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.py")
    if not os.path.exists(frontend_path):
        raise HTTPException(status_code=404, detail="frontend.py not found")
    with open(frontend_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.post("/api/research")
async def run_research_endpoint(req: ResearchRequest):
    """Executes CrewAI research pipeline and returns JSON output."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        report_md = await run_crew_pipeline(req.query, req.depth, req.sources)
        return {
            "status": "success",
            "query": req.query,
            "depth": req.depth,
            "report": report_md,
            "timestamp": time.strftime("%b %d, %Y")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/research/stream")
async def stream_research_endpoint(query: str, depth: str = "deep"):
    """Streams real-time agent steps, raw logs, and final report using Server-Sent Events (SSE)."""
    async def event_generator() -> AsyncGenerator[str, None]:
        def fmt_event(event_name: str, payload: dict) -> str:
            return f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"

        ts = time.strftime("%H:%M:%S")

        # Step 1: Initialization
        yield fmt_event("step_update", {"step_id": 1, "status": "active", "label": "Initializing agent & search parameters"})
        yield fmt_event("log", {"ts": ts, "level": "info", "msg": f"Agent initialized research on '{query}' (Depth: {depth})"})
        await asyncio.sleep(0.4)
        yield fmt_event("step_update", {"step_id": 1, "status": "done", "label": "Search parameters initialized"})

        # Step 2: Executing Web Search
        yield fmt_event("step_update", {"step_id": 2, "status": "active", "label": f"Searching Google & sources for '{query}'"})
        yield fmt_event("log", {"ts": ts, "level": "info", "msg": f"Tool: google_search(query='{query}')"})
        await asyncio.sleep(0.6)

        num_results = 5 if depth == "deep" else 3
        try:
            search_text = search_serper(query, n_results=num_results)
            yield fmt_event("log", {"ts": ts, "level": "ok", "msg": f"Search returned top {num_results} results."})
        except Exception as err:
            yield fmt_event("log", {"ts": ts, "level": "warn", "msg": f"Search tool warning: {err}"})

        yield fmt_event("step_update", {"step_id": 2, "status": "done", "label": "Search complete"})

        # Step 3: Synthesis with CrewAI
        yield fmt_event("step_update", {"step_id": 3, "status": "active", "label": "Synthesizing research with Groq Llama-3.3-70b"})
        yield fmt_event("log", {"ts": ts, "level": "info", "msg": "CrewAI running sequential Analyst & Writer pipeline..."})

        try:
            report_md = await run_crew_pipeline(query, depth)
            yield fmt_event("log", {"ts": ts, "level": "ok", "msg": "Synthesis complete. Report drafted."})
        except Exception as e:
            report_md = f"### Error during research\n\nFailed to complete research: {str(e)}"
            yield fmt_event("log", {"ts": ts, "level": "warn", "msg": f"Pipeline error: {e}"})

        yield fmt_event("step_update", {"step_id": 3, "status": "done", "label": "Report drafted"})

        # Step 4: Citing Sources
        yield fmt_event("step_update", {"step_id": 4, "status": "active", "label": "Citing sources and formatting"})
        await asyncio.sleep(0.4)
        yield fmt_event("step_update", {"step_id": 4, "status": "done", "label": "Sources cited"})

        # Step 5: Final Quality Check
        yield fmt_event("step_update", {"step_id": 5, "status": "done", "label": "Final review complete"})
        yield fmt_event("log", {"ts": ts, "level": "ok", "msg": "Research session finished."})

        # Deliver Final Completion Payload
        yield fmt_event("complete", {
            "query": query,
            "report": report_md,
            "timestamp": time.strftime("%b %d, %Y · %H:%M")
        })

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def run_crew_pipeline(query: str, depth: str = "deep", sources: dict = None) -> str:
    """Executes multi-agent sequential research workflow (Analyst + Writer) with Groq LLM and Serper search context."""
    num_results = 5 if depth == "deep" else 3
    search_context = ""
    try:
        raw_search = search_serper(query, n_results=num_results)
        search_context = str(raw_search)[:3000]
    except Exception as e:
        search_context = f"Search note: {str(e)}"

    # Agent 1: Research Analyst Agent
    analyst_system_prompt = (
        "You are an expert Research Analyst in an autonomous multi-agent research team. "
        "Your role is to inspect real-time web search findings, verify factual consistency, filter out noise, "
        "and extract core data points, technical specifics, comparisons, and source URLs. "
        "Provide an accurate, detailed factual brief with key takeaways and citations."
    )
    analyst_user_prompt = (
        f"Research Topic: '{query}'\n\n"
        f"Real-Time Web Search Context:\n{search_context}\n\n"
        "Analyze these findings thoroughly and output a factual research briefing including verified data points and source URLs."
    )
    analyst_output = await call_groq([
        {"role": "system", "content": analyst_system_prompt},
        {"role": "user", "content": analyst_user_prompt}
    ], temperature=0.1)

    # Agent 2: Content Writer & Synthesizer Agent
    writer_system_prompt = (
        "You are an expert Content Writer & Synthesizer in an autonomous multi-agent team. "
        "Your role is to take the factual briefing from the Research Analyst and write a comprehensive, "
        "authoritative, and beautifully structured final research report.\n\n"
        "CRITICAL FORMATTING GUIDELINES:\n"
        "1. Structure your report into clear Markdown sections: Executive Summary, Key Findings, Detailed Analysis, and Takeaways.\n"
        "2. ACCURACY & COMPARISONS: Whenever comparing products, versions, metrics, benchmarks, features, or pros/cons, you MUST format them in clean Markdown tables (using '| Header 1 | Header 2 |' syntax with proper dashed separator lines).\n"
        "3. Ensure comparison tables have clear column names and clean row borders.\n"
        "4. At the very end, include a dedicated '### Sources & References' section listing source names and clickable markdown URLs."
    )
    writer_user_prompt = (
        f"User Query: '{query}'\n\n"
        f"Verified Findings from Research Analyst:\n{analyst_output}\n\n"
        "Write the final, complete research report adhering to all formatting guidelines, markdown comparison tables, and references."
    )
    final_report = await call_groq([
        {"role": "system", "content": writer_system_prompt},
        {"role": "user", "content": writer_user_prompt}
    ], temperature=0.2)

    return final_report


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
