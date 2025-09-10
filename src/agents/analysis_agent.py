import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        pass

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data: Compare, reason, calculate."""
        task = message.get("task", "")
        context = message.get("context", {})
        research_data = context.get("research_result", {}).get("output", "No data")
        logger.info(f"Analyzing: {task} with research data: {research_data}")
        result = f"Analysis of {task}: {research_data} is effective." if research_data != "No data" else "No analysis possible."
        confidence = 0.7 if research_data != "No data" else 0.3
        return {"output": result, "confidence": confidence, "reasoning": "basic", "input_data": research_data}