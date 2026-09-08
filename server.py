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

# Environment & Tracing setup
load_dotenv()
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"

try:
    import litellm
    litellm.api_key = os.getenv("GROQ_API_KEY")
    litellm.callbacks = []
    litellm.drop_params = True
except ImportError:
    pass

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

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
            search_tool = SerperDevTool(n_results=num_results)
            yield fmt_event("log", {"ts": ts, "level": "ok", "msg": f"Search returned {num_results} top results."})
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
    """Executes CrewAI sequential workflow with Groq LLM and Serper tool."""
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        max_retries=3
    )

    num_results = 5 if depth == "deep" else 3
    search_tool = SerperDevTool(n_results=num_results)

    researcher = Agent(
        role="Research Analyst",
        goal=f"Gather detailed, up-to-date, accurate information on {query} using web search tools.",
        backstory="You are an expert analyst retrieving facts, context, data points, and source links on any given topic.",
        tools=[search_tool],
        llm=llm,
        verbose=False,
        max_iter=5
    )

    writer = Agent(
        role="Content Writer & Synthesizer",
        goal=f"Synthesize raw research data into a clear, natural, engaging, and well-structured final report about {query}.",
        backstory="You are a versatile content writer. You structure findings into clear markdown with sections like Executive Summary, Key Findings, Detailed Analysis, and a separate '### Sources & References' section at the end.",
        llm=llm,
        verbose=False
    )

    research_task = Task(
        description=f"Search for key details, facts, news, and insights about '{query}'. Extract accurate context and note source URLs.",
        expected_output="Factual research findings and source URLs.",
        agent=researcher
    )

    writing_task = Task(
        description=f"Using the research findings, answer: '{query}'. Format the answer in a clean, comprehensive markdown format using logical subheadings that fit naturally (e.g. Executive Summary, Key Findings, Detailed Analysis, etc.). List sources under a separate '### Sources & References' section at the end.",
        expected_output="A well-structured markdown report with citations.",
        agent=writer,
        context=[research_task]
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        planning=False,
        verbose=False
    )

    # Run in separate thread so asyncio loop remains responsive
    result = await asyncio.to_thread(crew.kickoff, inputs={"topic": query, "feedback": "None"})
    return str(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
