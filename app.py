import os
from dotenv import load_dotenv
load_dotenv()
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
import streamlit as st

try:
    import litellm
    litellm.api_key = os.getenv("GROQ_API_KEY")
    litellm.callbacks = []
    litellm.success_callback = []
    litellm._async_success_callback = []
    litellm.drop_params = True
    litellm.set_verbose = False
    litellm.num_retries = 3
except ImportError:
    pass

import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

load_dotenv()

st.set_page_config(page_title="Research Assistant Crew", page_icon="🤖", layout="wide")
st.title("🤖 Research Assistant Crew")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

GREETINGS = {
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening", 
    "who are you", "what can you do", "what are the things you can do", "help", "how do you work",
    "tell me about yourself", "tell me something about yourself", "introduce yourself", "about yourself"
}

def is_greeting(text: str) -> bool:
    cleaned = text.strip().lower().rstrip(".!? ")
    if cleaned in GREETINGS:
        return True
    if any(p in cleaned for p in ["what can you do", "things you can do", "who are you", "how do you work", "what are your features", "what do you do", "about yourself", "introduce yourself"]):
        return True
    return len(cleaned.split()) <= 2 and any(g in cleaned for g in ["hello", "hi", "hey"])

def handle_greeting() -> str:
    return (
        "👋 **Hello! I am your AI Research Assistant.**\n\n"
        "I am an intelligent multi-agent research assistant powered by CrewAI and Groq (Llama 3.3 70B).\n\n"
        "**What I do:**\n"
        "- 🔍 **Web Research**: Perform real-time web searches to gather accurate facts, news, and insights on any subject.\n"
        "- 📝 **Topic Synthesis**: Synthesize raw research into clean, readable answers with dynamic, subject-specific subheadings.\n"
        "- 📚 **Source References**: Include direct URLs and citations for all research sources at the end of the response.\n\n"
        "Ask me about any topic (e.g. *Artificial Intelligence*, *Global Economics*, *Space Exploration*, or *Latest Tech Trends*) to get started!"
    )

def classify_intent(query: str) -> str:
    """Classifies user query into 'DIRECT' (conversational/general knowledge) or 'RESEARCH' (needs live web search)."""
    q_clean = query.strip().lower().rstrip(".!? ")
    if is_greeting(query):
        return "DIRECT"

    # Explicit research keywords
    if any(w in q_clean for w in ["latest news", "search", "recent news", "current news", "today news", "latest updates"]):
        return "RESEARCH"

    try:
        classifier_llm = LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0
        )
        prompt = (
            "Classify the following user request into exactly one of two categories:\n"
            "- DIRECT: The request is a greeting, casual chat, general knowledge question, coding explanation, math problem, or concept explanation that does NOT require searching real-time live internet news.\n"
            "- RESEARCH: The request explicitly or implicitly asks for real-time information, latest news, recent updates, current events, recent releases, market prices, or web research.\n\n"
            f"User Request: \"{query}\"\n\n"
            "Respond with ONLY ONE WORD: DIRECT or RESEARCH."
        )
        res = classifier_llm.call([{"role": "user", "content": prompt}]).strip().upper()
        if "RESEARCH" in res:
            return "RESEARCH"
        return "DIRECT"
    except Exception:
        keywords = ["latest", "news", "current", "2026", "2025", "recent", "today", "update", "stock", "price", "who is the current"]
        if any(kw in q_clean for kw in keywords):
            return "RESEARCH"
        return "DIRECT"

def get_direct_llm_response(query: str) -> str:
    """Generates a direct response using LLM without running web search crew."""
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7
    )
    prompt = (
        "You are an intelligent, helpful AI assistant. Answer the user's message clearly, naturally, and concisely.\n\n"
        f"User Message: {query}"
    )
    return llm.call([{"role": "user", "content": prompt}])

def create_crew():
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        max_retries=3
    )
    search_tool = SerperDevTool(n_results=3)

    researcher = Agent(
        role="Research Analyst",
        goal="Gather accurate, relevant, and up-to-date information on {topic} from web search tools.",
        backstory="You are an expert web researcher. You search the internet efficiently to pull out key facts, context, data points, and source links on any given topic.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        max_iter=5
    )

    writer = Agent(
        role="Content Writer & Synthesizer",
        goal="Synthesize raw research data into a clear, natural, engaging, and well-structured final answer about {topic}.",
        backstory="You are a versatile content writer. You take research findings and structure them logically into markdown sections with natural headings tailored specifically to {topic}. You adapt your headings dynamically based on the subject (e.g., Overview, Key Features, Recent Developments, Analysis, etc.). At the very end, add a separate '### Sources & References' section if sources were used.",
        llm=llm,
        verbose=True
    )

    research_task = Task(
        description="Search for key details, facts, news, and relevant insights about {topic}. Extract accurate context and note source URLs.",
        expected_output="A concise list of factual research findings and web source URLs related to {topic}.",
        agent=researcher
    )

    writing_task = Task(
        description="Using the research findings, answer: {topic}. Format the answer in a clean, comprehensive markdown format using logical subheadings that fit {topic} naturally (e.g. Overview, Key Highlights, Details, Impact, etc.). Do not force irrelevant categories or templates. If web sources were referenced in research, list them clearly under a separate '### Sources & References' section at the end.",
        expected_output="A well-structured, natural answer formatted with topic-relevant headings, followed by a '### Sources & References' section if sources were used.",
        agent=writer,
        context=[research_task]
    )

    return Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        planning=False,
        verbose=True
    )

user_input = st.chat_input("Ask a topic...")

if user_input:
    # Render user prompt immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        intent = classify_intent(user_input)
        if intent == "DIRECT":
            if is_greeting(user_input):
                response_text = handle_greeting()
            else:
                with st.spinner("Thinking..."):
                    response_text = get_direct_llm_response(user_input)
            st.markdown(response_text)
        else:
            with st.spinner("Searching the web and compiling research..."):
                crew = create_crew()

                inputs = {
                    "topic": user_input,
                    "feedback": "None"
                }

                result = crew.kickoff(inputs=inputs)
                response_text = str(result)
                st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})