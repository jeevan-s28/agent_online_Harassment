from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
import os
from agent_state import AgentState
from database import save_log

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0, max_retries=5)

# --- Nodes ---

def start_node(state: AgentState):
    # Initialize empty state fields if needed
    return {
        "reasoning_history": [],
        "policy_violations": []
    }

def linguistic_analyst_node(state: AgentState):
    input_text = state["input_text"]
    prompt = f"""
    You are a Linguistic Analyst. Analyze the following text for tone, intent, and subtle nuances (sarcasm, slang, passive-aggression).
    
    **SDG 5 Focus**: Pay special attention to gender-based bias, misogynistic undertones, objectification, or gender stereotypes.
    
    Text: "{input_text}"
    
    Output a brief analysis of how it was said and the contextual intent.
    Start your response with "Thought: [Your internal reasoning]" followed by "Analysis: [Your final analysis]".
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    
    # Parse thought and analysis (simple parsing for demo)
    thought = content.split("Analysis:")[0].replace("Thought:", "").strip() if "Thought:" in content else "Analyzing tone..."
    analysis = content.split("Analysis:")[1].strip() if "Analysis:" in content else content

    return {
        "linguistic_analysis": analysis,
        "reasoning_history": state["reasoning_history"] + [{"agent": "Linguistic Analyst", "thought": thought, "output": analysis}]
    }

def policy_auditor_node(state: AgentState):
    analysis = state["linguistic_analysis"]
    input_text = state["input_text"]
    
    prompt = f"""
    You are a Policy Auditor. Evaluate the text and the linguistic analysis against these community guidelines, with a strict focus on **SDG 5 (Gender Equality)**:
    - **Gender-based Harassment**: Unwanted sexual advances, misogyny, or gender-based insults.
    - **Hate Speech**: Attacks based on gender or sexual orientation.
    - **Cyberbullying**: Targeted harassment.
    - **Incitement of Violence**: Threats against women or girls.
    
    Text: "{input_text}"
    Linguistic Analysis: "{analysis}"
    
    List any policy violations. If none, say "None". Do NOT include "(SDG X)" in the violation name.
    Start with "Thought: [Reasoning]" followed by "Violations: [List]".
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    
    thought = content.split("Violations:")[0].replace("Thought:", "").strip() if "Thought:" in content else "Checking policies..."
    violations_text = content.split("Violations:")[1].strip() if "Violations:" in content else content
    
    violations = [v.strip() for v in violations_text.split(",")] if violations_text != "None" else []

    return {
        "policy_violations": violations,
        "reasoning_history": state["reasoning_history"] + [{"agent": "Policy Auditor", "thought": thought, "output": violations_text}]
    }

def resolution_agent_node(state: AgentState):
    violations = state["policy_violations"]
    
    prompt = f"""
    You are a Resolution Agent. Based on the policy violations, assign a severity score (Low, Medium, High, Critical) and suggest a mitigation action (Ignore, Warn, Shadowban, Immediate Report).
    
    Guidelines for Action:
    - Low Severity -> Ignore or Monitor
    - Medium Severity -> Warn
    - High Severity -> Shadowban
    - Critical Severity -> Immediate Report
    
    Violations: {violations}
    
    Format:
    Thought: [Reasoning]
    Severity: [Score]
    Action: [Action]
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    
    thought = content.split("Severity:")[0].replace("Thought:", "").strip() if "Thought:" in content else "Deciding verdict..."
    severity = content.split("Severity:")[1].split("Action:")[0].strip() if "Severity:" in content else "Low"
    action = content.split("Action:")[1].strip() if "Action:" in content else "Ignore"

    return {
        "severity_score": severity,
        "final_decision": action,
        "reasoning_history": state["reasoning_history"] + [{"agent": "Resolution Agent", "thought": thought, "output": f"Severity: {severity}, Action: {action}"}]
    }

def db_manager_node(state: AgentState):
    # Save to Supabase
    category = state["policy_violations"][0] if state["policy_violations"] else "Safe"
    source = "Manual"
    save_log(
        content=state["input_text"],
        category=category,
        severity=state["severity_score"],
        reasoning_chain=state["reasoning_history"],
        suggested_action=state["final_decision"],
        source=source
    )
    return {
        "reasoning_history": state["reasoning_history"] + [{"agent": "Database Manager", "thought": "Logging to Supabase", "output": "Saved"}]
    }

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("start", start_node)
workflow.add_node("linguistic_analyst", linguistic_analyst_node)
workflow.add_node("policy_auditor", policy_auditor_node)
workflow.add_node("resolution_agent", resolution_agent_node)
workflow.add_node("db_manager", db_manager_node)

workflow.set_entry_point("start")
workflow.add_edge("start", "linguistic_analyst")
workflow.add_edge("linguistic_analyst", "policy_auditor")
workflow.add_edge("policy_auditor", "resolution_agent")
workflow.add_edge("resolution_agent", "db_manager")
workflow.add_edge("db_manager", END)

app_graph = workflow.compile()
