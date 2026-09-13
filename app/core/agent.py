import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

load_dotenv()


class TriageResult(BaseModel):
    confidence: str = Field(description="One of: HIGH, LOW — how confident you are this is a real, safely auto-fixable issue")
    severity: str = Field(description="One of: LOW, MEDIUM, HIGH, CRITICAL")
    explanation: str = Field(description="Why this finding matters, one to two sentences")
    patched_code: str = Field(description="Full corrected file content, only if confidence is HIGH")


class PipelineState(TypedDict):
    rule: str
    message: str
    file_path: str
    code: str
    confidence: str
    severity: str
    explanation: str
    patched_code: str
    decision: str
    verified: bool


llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b", temperature=0.0)
parser = JsonOutputParser(pydantic_object=TriageResult)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a security engineer triaging a static-analysis finding. "
               "Judge your CONFIDENCE that this is a real issue with a safe, unambiguous fix "
               "(HIGH), versus a case requiring human judgment about context, intent, or "
               "business logic before fixing (LOW). If confidence is LOW, still explain why, "
               "but patched_code can be an empty string.\n{format_instructions}"),
    ("user", "Rule: {rule}\nMessage: {message}\nFile: {file_path}\n\nCode:\n{code}"),
])

chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser


def triage_node(state: PipelineState) -> PipelineState:
    result = chain.invoke({
        "rule": state["rule"], "message": state["message"],
        "file_path": state["file_path"], "code": state["code"],
    })
    state["confidence"] = result["confidence"]
    state["severity"] = result["severity"]
    state["explanation"] = result["explanation"]
    state["patched_code"] = result["patched_code"]
    return state


def route_decision(state: PipelineState) -> str:
    return "auto_fix" if state["confidence"] == "HIGH" else "escalate"


def auto_fix_node(state: PipelineState) -> PipelineState:
    state["decision"] = "auto_fix"
    return state


def escalate_node(state: PipelineState) -> PipelineState:
    state["decision"] = "escalate"
    state["verified"] = False
    return state


def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("triage", triage_node)
    graph.add_node("auto_fix", auto_fix_node)
    graph.add_node("escalate", escalate_node)

    graph.set_entry_point("triage")
    graph.add_conditional_edges("triage", route_decision, {"auto_fix": "auto_fix", "escalate": "escalate"})
    graph.add_edge("auto_fix", END)
    graph.add_edge("escalate", END)

    return graph.compile()
