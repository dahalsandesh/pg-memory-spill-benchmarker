from typing import Dict, Any, TypedDict

class SpillReport(TypedDict):
    spilled: bool
    spill_type: str
    sort_space_used_kb: int
    hash_batches: int
    temp_read_blocks: int
    temp_written_blocks: int

def detect_spills(plan_node: Dict[str, Any]) -> SpillReport:
    """
    Recursively walks a PostgreSQL EXPLAIN FORMAT JSON plan tree.
    Returns a detailed SpillReport with memory and disk metrics.
    """
    report: SpillReport = {
        "spilled": False,
        "spill_type": "none",
        "sort_space_used_kb": 0,
        "hash_batches": 1,
        "temp_read_blocks": 0,
        "temp_written_blocks": 0
    }

    def _walk(node: Dict[str, Any]):
        nonlocal report
        
        # Check for Temp blocks at this node
        read_blocks = node.get("Temp Read Blocks", 0)
        written_blocks = node.get("Temp Written Blocks", 0)
        
        if read_blocks > 0 or written_blocks > 0:
            report["spilled"] = True
            if report["spill_type"] == "none":
                report["spill_type"] = "temp_blocks"
            report["temp_read_blocks"] += read_blocks
            report["temp_written_blocks"] += written_blocks

        # Check for Sort Spill
        if node.get("Node Type") == "Sort":
            sort_space_type = node.get("Sort Space Type", "")
            if sort_space_type == "Disk":
                report["spilled"] = True
                report["spill_type"] = "sort_external_merge"
                report["sort_space_used_kb"] = max(report["sort_space_used_kb"], node.get("Sort Space Used", 0))

        # Check for Hash Spill
        if node.get("Node Type") == "Hash":
            batches = node.get("Hash Batches", 1)
            if batches > 1:
                report["spilled"] = True
                report["spill_type"] = "hash_multi_batch"
                report["hash_batches"] = max(report["hash_batches"], batches)

        # Recursively check child plans
        if "Plans" in node:
            for child in node["Plans"]:
                _walk(child)

    _walk(plan_node)
    return report
