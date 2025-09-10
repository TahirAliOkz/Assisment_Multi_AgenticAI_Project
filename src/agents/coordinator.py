import logging
from typing import Dict, Any, List
from .research_agent import ResearchAgent
from .analysis_agent import AnalysisAgent
from .memory_agent import MemoryAgent
import datetime  # Import datetime module

# Set up logging for traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.memory_agent = MemoryAgent()
        self.conversation_history: List[Dict[str, Any]] = []  # Global context
        self.global_state: Dict[str, Any] = {"priority_tasks": []}  # System state

    def receive_query(self, user_query: str) -> str:
        """Receive user query, analyze complexity, route tasks, and return response."""
        logger.info(f"Received query: {user_query}")
        try:
            # Analyze complexity and plan tasks
            task_plan = self._plan_tasks(user_query)
            results = self._execute_plan(task_plan)
            final_response = self._synthesize_results(results)
            self._update_context(final_response)
            return final_response
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error: Could not process query. Fallback response: {self._fallback_response(user_query)}"

    def _plan_tasks(self, query: str) -> List[Dict[str, str]]:
        """Simple planner: Decompose query into sub-tasks based on complexity."""
        logger.info("Planning tasks...")
        plan = [{"agent": "research", "subtask": query}]  # Default: Research first
        if "analyze" in query.lower() or "compare" in query.lower():
            plan.append({"agent": "analysis", "subtask": query, "depends_on": "research"})
        if "earlier" in query.lower() or "previous" in query.lower():
            plan.append({"agent": "memory", "subtask": query, "depends_on": "research" if "research" in [t["agent"] for t in plan] else ""})
        self.global_state["priority_tasks"] = [t["agent"] for t in plan]  # Track priorities
        return plan

    def _execute_plan(self, plan: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Route to agents, handle dependencies, and merge results."""
        results = []
        executed_agents = set()
        for task in plan:
            agent_name = task["agent"]
            if agent_name in executed_agents and not task.get("depends_on"):  # Avoid redundant calls
                logger.info(f"Skipping redundant call to {agent_name}")
                continue
            if task.get("depends_on") and task["depends_on"] not in executed_agents:
                logger.warning(f"Dependency {task['depends_on']} not met for {agent_name}")
                continue

            message = {"task": task["subtask"], "context": self.global_state.copy()}
            try:
                if agent_name == "research":
                    result = self.research_agent.process_message(message)
                elif agent_name == "analysis":
                    result = self.analysis_agent.process_message(message)
                elif agent_name == "memory":
                    result = self.memory_agent.process_message({"action": "retrieve", "keywords": task["subtask"].split()})
                else:
                    raise ValueError(f"Unknown agent: {agent_name}")
                results.append(result)
                executed_agents.add(agent_name)
                logger.info(f"Executed {agent_name}: {result}")
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results.append({"error": f"{agent_name} failed", "fallback": "No data"})
        return results

    def _synthesize_results(self, results: List[Dict[str, Any]]) -> str:
        """Merge and synthesize final answer with confidence scoring."""
        logger.info("Synthesizing results...")
        if not results or all("error" in r for r in results):
            return "No valid results to synthesize."

        # Aggregate confidence (average of non-error results)
        confidences = [r.get("confidence", 0.0) for r in results if "error" not in r]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # Synthesize output
        output = "Synthesized response (confidence: {:.2f}). ".format(overall_confidence)
        for i, result in enumerate(results):
            if "error" not in result:
                output += f"Result {i+1}: {result.get('output', 'No output')}. "
            else:
                output += f"Result {i+1} failed: {result['error']}. "
        return output

    def _update_context(self, response: str):
        """Update conversation history and global state."""
        self.conversation_history.append({"query": response, "timestamp": datetime.datetime.now().isoformat()})
        logger.info("Updated context.")

    def _fallback_response(self, query: str) -> str:
        """Provide a rule-based fallback response."""
        return f"Fallback: Limited information available for '{query}'. Please try a simpler query."