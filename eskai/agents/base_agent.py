from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import logging

try:
    import litellm
except ImportError:
    litellm = None  # Handle gracefully if not installed

class BaseAgent(ABC):
    """
    Robust abstract base class for agents in the ESKAI framework.
    Provides logging, config, result management, tool access, and LLM calls via LiteLLM.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.log: List[str] = []
        self.results: List[Any] = []
        
        # Configure logging to output to terminal
        self.logger = logging.getLogger(self.name)
        
        # Clear existing handlers to avoid duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        handler = logging.StreamHandler()
        formatter = logging.Formatter(f'%(asctime)s - {self.name} - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Set level based on config
        log_level = self.get_config('log_level', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Propagate to root logger can be turned off if needed
        self.logger.propagate = False

    def log_action(self, message: str):
        self.log.append(message)
        self.logger.info(message)

    def add_result(self, result: Any):
        self.results.append(result)

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def setup(self):
        """Optional setup before run."""
        self.log_action("Setup complete.")

    def teardown(self):
        """Optional cleanup after run."""
        self.log_action("Teardown complete.")

    async def call_llm(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Call an LLM using LiteLLM API asynchronously.
        """
        if litellm is None:
            self.log_action("LiteLLM not installed. Cannot call LLM.")
            return "LLM call unavailable."
        
        model_name = model if model is not None else self.get_config("llm_model", "gpt-4o-mini")
        if not isinstance(model_name, str):
            model_name = "gpt-4o-mini"

        llm_provider = self.get_config("llm_provider")
        if llm_provider and not model_name.startswith(f"{llm_provider}/"):
            model_name = f"{llm_provider}/{model_name}"

        try:
            messages=[
                {"role": "system", "content": """
                    You are a highly capable autonomous agent operating within the ESKAI framework. 
                    Your responsibilities include understanding user objectives, generating actionable 
                    insights, and executing tasks with precision. Always respond clearly, concisely, and 
                    professionally. If a task requires reasoning, provide step-by-step logic. 
                    If you need to use tools or external resources, describe your approach. 
                    Ensure all outputs are safe, ethical, and relevant to the user's intent. 
                    If you encounter ambiguous instructions, ask clarifying questions."""
                },
                {"role": "user", "content": prompt}
            ]
            
            # Allow overriding the system prompt
            if 'system_prompt' in kwargs:
                messages[0]['content'] = kwargs.pop('system_prompt')

            response = await litellm.acompletion(
                model=model_name,
                messages=messages,
                **kwargs
            )
            content = response.choices[0].message.content # type: ignore
            self.log_action(f"LLM response: {content}")
            return content # type: ignore
        except Exception as e:
            self.log_action(f"LLM call failed: {e}")
            return f"LLM call failed: {e}"

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the agent's main logic asynchronously.
        Accepts positional and keyword arguments for flexibility.
        """
        ...

class ExampleAgent(BaseAgent):
    async def run(self, *args, **kwargs):
        self.log_action("Running ExampleAgent.")
        response = await self.call_llm("What is the capital of France?")
        self.add_result(response)
        return "Example run complete."

if __name__ == "__main__":
    import asyncio

    async def main():
        agent = ExampleAgent(name="ExampleAgent", config={"llm_model": "gpt-5-mini"})
        agent.setup()
        await agent.run()
        print(f"Result: {agent.results[-1]}")
        agent.teardown()

    asyncio.run(main())