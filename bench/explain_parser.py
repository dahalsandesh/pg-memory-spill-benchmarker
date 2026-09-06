from typing import Dict, Any

def detect_spills(plan_node: Dict[str, Any]) -> bool:
    """
    Recursively walks a PostgreSQL EXPLAIN FORMAT JSON plan tree.
    Returns True if a sort or hash spill is detected.
    """
    spilled = False

    # Check for Sort Spill
    if plan_node.get("Node Type") == "Sort":
        sort_method = plan_node.get("Sort Method", "")
        if "external merge" in sort_method.lower():
            spilled = True

    # Check for Hash Spill
    if plan_node.get("Node Type") == "Hash":
        if plan_node.get("Hash Batches", 1) > 1:
            spilled = True

    # Check for memory vs disk in Aggregate or other nodes
    if plan_node.get("Temp Read Blocks", 0) > 0 or plan_node.get("Temp Written Blocks", 0) > 0:
        spilled = True

    # Recursively check child plans
    if "Plans" in plan_node:
        for child in plan_node["Plans"]:
            if detect_spills(child):
                spilled = True

    return spilled
