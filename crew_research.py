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
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)
search_tool = SerperDevTool()

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate, current information on {topic} from the internet",
    backstory="You dig through the web and pull out only what matters, ignoring noise and fluff.",
    tools=[search_tool],
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Turn research into a clear, well structured answer for the user",
    backstory="You take raw research and shape it into something a person can actually read and use.",
    llm=llm,
    verbose=True
)

def chat():
    print("Ask me anything. Type 'exit' to quit.")
    while True:
        query = input("\nYou: ")
        if query.strip().lower() == "exit":
            break
        
        research_task = Task(
            description="Research {topic} thoroughly using the internet. Extract the most relevant facts and context.",
            expected_output="A concise set of well organized findings on {topic}.",
            agent=researcher
        )

        writing_task = Task(
            description="Using the research findings, write a clear, structured answer to: {topic}",
            expected_output="A well structured, final answer covering {topic}.",
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