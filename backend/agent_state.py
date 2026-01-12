from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    input_text: str
    linguistic_analysis: Optional[str]
    policy_violations: List[str]
    severity_score: Optional[str]
    final_decision: Optional[str]
    reasoning_history: List[dict]

