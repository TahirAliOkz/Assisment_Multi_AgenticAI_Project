import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        self.knowledge_base = {
            "neural networks": "Main types: CNN, RNN, Transformer.",
            "ML optimization": "Techniques: Gradient Descent, Adam, SGD."
        }

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate retrieval: Search mock KB, return info with confidence."""
        task = message.get("task", "")
        logger.info(f"Researching: {task}")
        context = message.get("context", {})
        result = self.knowledge_base.get(task.lower(), "No info found.")
        confidence = 0.9 if result != "No info found." else 0.5
        return {"output": result, "confidence": confidence, "source": "mock_kb", "context_used": str(context)}