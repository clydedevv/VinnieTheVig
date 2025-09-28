# %% [code]
# --- Install dependencies (Jupyter cell magic, if running in a notebook) ---
# %%capture --no-stderr
# %pip install -U langgraph langchain_community langchain_anthropic langchain_experimental

# --- Set up API keys if not already defined ---
import getpass
import os

def _set_if_undefined(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}: ")

_set_if_undefined("OPENAI_API_KEY")
_set_if_undefined("TAVILY_API_KEY")

# --- Create Tools for the Research Team ---
from typing import Annotated, List

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

# Create a search tool that returns up to 5 results.
tavily_tool = TavilySearchResults(max_results=5)

@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )

# --- Create File-Access Tools for the Document Writing Team ---
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional

from langchain_experimental.utilities import PythonREPL
from typing_extensions import TypedDict

_TEMP_DIRECTORY = TemporaryDirectory()
WORKING_DIRECTORY = Path(_TEMP_DIRECTORY.name)

@tool
def create_outline(
    points: Annotated[List[str], "List of main points or sections."],
    file_name: Annotated[str, "File path to save the outline."],
) -> Annotated[str, "Path of the saved outline file."]:
    """Create and save an outline."""
    with (WORKING_DIRECTORY / file_name).open("w") as file:
        for i, point in enumerate(points):
            file.write(f"{i + 1}. {point}\n")
    return f"Outline saved to {file_name}"

@tool
def read_document(
    file_name: Annotated[str, "File path to read the document from."],
    start: Annotated[Optional[int], "The start line. Default is 0"] = None,
    end: Annotated[Optional[int], "The end line. Default is None"] = None,
) -> str:
    """Read the specified document."""
    with (WORKING_DIRECTORY / file_name).open("r") as file:
        lines = file.readlines()
    # If 'start' is provided (here defaulting to 0) we slice accordingly.
    if start is None:
        start = 0
    return "\n".join(lines[start:end])

@tool
def write_document(
    content: Annotated[str, "Text content to be written into the document."],
    file_name: Annotated[str, "File path to save the document."],
) -> Annotated[str, "Path of the saved document file."]:
    """Create and save a text document."""
    with (WORKING_DIRECTORY / file_name).open("w") as file:
        file.write(content)
    return f"Document saved to {file_name}"

@tool
def edit_document(
    file_name: Annotated[str, "Path of the document to be edited."],
    inserts: Annotated[
        Dict[int, str],
        "Dictionary where key is the line number (1-indexed) and value is the text to be inserted at that line.",
    ],
) -> Annotated[str, "Path of the edited document file."]:
    """Edit a document by inserting text at specific line numbers."""
    with (WORKING_DIRECTORY / file_name).open("r") as file:
        lines = file.readlines()
    sorted_inserts = sorted(inserts.items())
    for line_number, text in sorted_inserts:
        if 1 <= line_number <= len(lines) + 1:
            lines.insert(line_number - 1, text + "\n")
        else:
            return f"Error: Line number {line_number} is out of range."
    with (WORKING_DIRECTORY / file_name).open("w") as file:
        file.writelines(lines)
    return f"Document edited and saved to {file_name}"

# Warning: Executing arbitrary code can be unsafe.
repl = PythonREPL()

@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Execute Python code and return stdout. Use print() for visible output."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"

# --- Helper Utilities to Create Supervisor Nodes ---
from typing import List, Optional, Literal
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage

class State(MessagesState):
    next: str

def make_supervisor_node(llm: BaseChatModel, members: list[str]) -> str:
    options = ["FINISH"] + members
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: Literal[*options]

    def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END
        return Command(goto=goto, update={"next": goto})
    return supervisor_node

# --- Define the Research Team Agents and Graph ---
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o")

# Create a search agent using the Tavily search tool.
search_agent = create_react_agent(llm, tools=[tavily_tool])

def search_node(state: State) -> Command[Literal["supervisor"]]:
    result = search_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="search")]},
        goto="supervisor",
    )

# Create a web scraper agent using the scrape_webpages tool.
web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])

def web_scraper_node(state: State) -> Command[Literal["supervisor"]]:
    result = web_scraper_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="web_scraper")]},
        goto="supervisor",
    )

# Create a supervisor node that will decide which of the two workers (search or web scraper) to use.
research_supervisor_node = make_supervisor_node(llm, ["search", "web_scraper"])

# Build the research team graph.
research_builder = StateGraph(State)
research_builder.add_node("supervisor", research_supervisor_node)
research_builder.add_node("search", search_node)
research_builder.add_node("web_scraper", web_scraper_node)
research_builder.add_edge(START, "supervisor")
research_graph = research_builder.compile()

# (For debugging/inspection, display the graph image.)
from IPython.display import Image, display
display(Image(research_graph.get_graph().draw_mermaid_png()))
# --> [Comment: The above displays an image of the research team graph.]

# Test the research team by streaming a sample query.
for s in research_graph.stream(
    {"messages": [("user", "when is Taylor Swift's next tour?")]},
    {"recursion_limit": 100},
):
    print(s)
    print("---")
# --> [Sample output:
# {'supervisor': {'next': 'search'}}
# ---
# {'search': {'messages': [HumanMessage(content="Taylor Swift's next tour is The Eras Tour, ...", ...)]}}
# ---
# {'supervisor': {'next': 'web_scraper'}}
# ---
# {'web_scraper': {'messages': [HumanMessage(content='Taylor Swift\'s next tour is "The Eras Tour." ...', ...)]}}
# ---
# {'supervisor': {'next': '__end__'}}
# ---]

# --- Define the Document Writing Team Agents and Graph ---
llm = ChatOpenAI(model="gpt-4o")  # Re-use or reinitialize LLM as needed

# Create a document writer agent with file-writing tools.
doc_writer_agent = create_react_agent(
    llm,
    tools=[write_document, edit_document, read_document],
    prompt=(
        "You can read, write and edit documents based on note-taker's outlines. "
        "Don't ask follow-up questions."
    ),
)

def doc_writing_node(state: State) -> Command[Literal["supervisor"]]:
    result = doc_writer_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="doc_writer")]},
        goto="supervisor",
    )

# Create a note-taker agent to produce outlines.
note_taking_agent = create_react_agent(
    llm,
    tools=[create_outline, read_document],
    prompt=(
        "You can read documents and create outlines for the document writer. "
        "Don't ask follow-up questions."
    ),
)

def note_taking_node(state: State) -> Command[Literal["supervisor"]]:
    result = note_taking_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="note_taker")]},
        goto="supervisor",
    )

# Create a chart-generating agent that can run Python code.
chart_generating_agent = create_react_agent(llm, tools=[read_document, python_repl_tool])

def chart_generating_node(state: State) -> Command[Literal["supervisor"]]:
    result = chart_generating_agent.invoke(state)
    return Command(
        update={"messages": [HumanMessage(content=result["messages"][-1].content, name="chart_generator")]},
        goto="supervisor",
    )

# Supervisor for the document writing team
doc_writing_supervisor_node = make_supervisor_node(llm, ["doc_writer", "note_taker", "chart_generator"])

# Build the document writing (paper writing) team graph.
paper_writing_builder = StateGraph(State)
paper_writing_builder.add_node("supervisor", doc_writing_supervisor_node)
paper_writing_builder.add_node("doc_writer", doc_writing_node)
paper_writing_builder.add_node("note_taker", note_taking_node)
paper_writing_builder.add_node("chart_generator", chart_generating_node)
paper_writing_builder.add_edge(START, "supervisor")
paper_writing_graph = paper_writing_builder.compile()

# (Display the document writing team graph for inspection.)
display(Image(paper_writing_graph.get_graph().draw_mermaid_png()))
# --> [An image of the document writing team graph is shown.]

# Test the document writing team with a sample query.
for s in paper_writing_graph.stream(
    {"messages": [("user", "Write an outline for poem about cats and then write the poem to disk.")]},
    {"recursion_limit": 100},
):
    print(s)
    print("---")
# --> [Sample output:
# {'supervisor': {'next': 'note_taker'}}
# ---
# {'note_taker': {'messages': [HumanMessage(content="The outline for the poem about cats has been created and saved as 'cats_poem_outline.txt'.", ...)]}}
# ---
# {'supervisor': {'next': 'doc_writer'}}
# ---
# {'doc_writer': {'messages': [HumanMessage(content="The poem about cats has been written and saved as 'cats_poem.txt'.", ...)]}}
# ---
# {'supervisor': {'next': '__end__'}}
# ---]

# --- Compose a Top-Level Hierarchical Graph to Orchestrate Both Teams ---
from langchain_core.messages import BaseMessage

llm = ChatOpenAI(model="gpt-4o")

# Create a top-level supervisor that decides between the research team and writing team.
teams_supervisor_node = make_supervisor_node(llm, ["research_team", "writing_team"])

# Helper functions to call each subgraph and "report back" to the top-level supervisor.
def call_research_team(state: State) -> Command[Literal["supervisor"]]:
    response = research_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={"messages": [HumanMessage(content=response["messages"][-1].content, name="research_team")]},
        goto="supervisor",
    )

def call_paper_writing_team(state: State) -> Command[Literal["supervisor"]]:
    response = paper_writing_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={"messages": [HumanMessage(content=response["messages"][-1].content, name="writing_team")]},
        goto="supervisor",
    )

# Build the top-level (super) graph.
super_builder = StateGraph(State)
super_builder.add_node("supervisor", teams_supervisor_node)
super_builder.add_node("research_team", call_research_team)
super_builder.add_node("writing_team", call_paper_writing_team)
super_builder.add_edge(START, "supervisor")
super_graph = super_builder.compile()

# Display the hierarchical super graph.
display(Image(super_graph.get_graph().draw_mermaid_png()))
# --> [An image of the top-level supervisor graph routing between research_team and writing_team is shown.]

# You can now use 'super_graph.stream(...)' to run the overall hierarchical workflow.
# For example:
# for s in super_graph.stream({"messages": [("user", "Give me a research report and a document about skincare.")]}, {"recursion_limit": 100}):
#     print(s)
#     print("---")

# End of combined code cell.