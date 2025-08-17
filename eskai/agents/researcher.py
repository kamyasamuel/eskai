from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Agent for conducting research tasks.
    """

    def run(self, prompt: str, **kwargs) -> dict:
        # Research logic (e.g., literature search, data gathering)
        return {"agent": self.name, "output": f"Research results for: {prompt}"}
