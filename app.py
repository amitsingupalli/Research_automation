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

def create_crew():
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        max_retries=3
    )
    search_tool = SerperDevTool(n_results=2)

    researcher = Agent(
        role="Research Analyst",
        goal="Find accurate, current information on {topic} from the internet.",
        backstory="You dig through the web using search tools to pull out key facts and sources.",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        max_iter=5
    )

    writer = Agent(
        role="Content Writer",
        goal="Turn research into a clear, well-structured answer, placing all source website references at the very end.",
        backstory="You synthesize raw research into readable text without inline URL references. All citations and source links must appear strictly in a dedicated 'Sources & References' section at the end.",
        llm=llm,
        verbose=True
    )

    research_task = Task(
        description="Search for the latest news on {topic}. Extract key facts and famous titles grouped by genre.",
        expected_output="A concise list of key findings and famous anime per genre on {topic}.",
        agent=researcher
    )

    writing_task = Task(
        description="Using the research findings, answer: {topic}. Format the answer in a clean, point-wise structure organized under different genre subheadings (e.g. Action, Romance, Sci-Fi, Fantasy, Shonen, etc.). At the very end, add a separate '### Sources & References' section listing source names and URLs.",
        expected_output="A point-wise structured answer by genre followed by a '### Sources & References' section at the end.",
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
        with st.spinner("Crew is working on your request..."):
            crew = create_crew()

            inputs = {
                "topic": user_input,
                "feedback": "None"
            }

            result = crew.kickoff(inputs=inputs)
            response_text = str(result)
            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})