import os
from dotenv import load_dotenv
load_dotenv()

try:
    from agent_graph import app_graph
    print("Graph imported successfully.")
    
    initial_state = {"input_text": "You are stupid"}
    print("Invoking graph...")
    result = app_graph.invoke(initial_state)
    print("Graph result:", result)

except Exception as e:
    import traceback
    traceback.print_exc()
