import os
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
from dotenv import load_dotenv
import litellm
litellm.callbacks = []
litellm.success_callback = []
litellm._async_success_callback = []
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)
search_tool = SerperDevTool(n_results=3)

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, current information on {topic} from the internet",
    backstory="You search the web efficiently to pull out facts, data points, context, and source URLs on any topic requested.",
    tools=[search_tool],
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer & Synthesizer",
    goal="Turn research into a clear, natural, engaging, and well-structured answer about {topic}.",
    backstory="You shape raw research findings into readable text with dynamic subheadings matching the topic, followed by a '### Sources & References' section if sources were used.",
    llm=llm,
    verbose=True
)

def chat():
    print("Ask me anything. Type 'exit' to quit.")
    while True:
        query = input("\nYou: ")
        if query.strip().lower() == "exit":
            break
        
        cleaned = query.strip().lower().rstrip(".!?")
        if cleaned in {"hello", "hi", "hey", "greetings", "who are you"} or (len(cleaned.split()) <= 2 and any(g in cleaned for g in ["hello", "hi", "hey"])):
            print("\nAnswer:\nHello! I am your AI Research Assistant. Ask me about any topic (technology, science, world news, etc.) and I will find key information for you!")
            continue

        research_task = Task(
            description="Research {topic} thoroughly using the internet. Extract key facts, relevant insights, and source URLs.",
            expected_output="A concise list of factual findings and source URLs on {topic}.",
            agent=researcher
        )

        writing_task = Task(
            description="Using research findings, answer: {topic}. Format naturally with dynamic topic headings (e.g. Overview, Key Findings, Details) and append a '### Sources & References' section at the end.",
            expected_output="A well structured, final answer covering {topic} with sources at the end.",
            agent=writer,
            context=[research_task]
        )

        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs={"topic": query})
        print("\nAnswer:\n", result)

if __name__ == "__main__":
    chat()