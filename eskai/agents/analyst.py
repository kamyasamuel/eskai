import json
import pandas as pd
from .base_agent import BaseAgent
from eskai.tools.data_analysis_tool import (
    StatisticsTool,
    MLTool,
    DataCleaningTool,
    ReportingTool,
    VisualizationTool,
)
import logging

class AnalystAgent(BaseAgent):
    """
    Agent for data analysis tasks.
    Mind-like algorithm: uses LLM to plan, select tools, and solve analysis problems.
    """

    def __init__(self, 
        data_path: str, 
        analysis_objective: str, 
        llm_provider: str = "openai", 
        llm_model: str = "gpt-5-mini", 
        verbose: bool = False, 
        name: str = "AnalystAgent"):
        
        config = {
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "verbose": verbose,
        }
        super().__init__(name, config)
        self.data_path = data_path
        self.objective = analysis_objective
        self.tools = {
            "statistics": StatisticsTool(),
            "visualization": VisualizationTool(),
            "ml": MLTool(),
            "cleaning": DataCleaningTool(),
            "reporting": ReportingTool(name=f"{name}_reporting_tool")
        }
        if verbose:
            self.logger.setLevel(logging.INFO)

    async def _generate_plan(self, analysis_prompt: str) -> list:
        """Generates an analysis plan using an LLM."""
        system_prompt = f"""
            You are a master data analyst. Your task is to create a step-by-step JSON plan to analyze data based on the user's request.
            The available tools are: {list(self.tools.keys())}.
            Each step in the plan should be a JSON object with "tool", "action", and "params" keys.
            Example: [{{"tool": "cleaning", "action": "handle_missing_values", "params": {{"strategy": "mean"}}}}]
        """
        plan_str = await self.call_llm(
            f"User request: {analysis_prompt}\n\nGenerate the JSON analysis plan.",
            system_prompt=system_prompt
        )
        self.log_action(f"LLM-generated plan: {plan_str}")
        try:
            # The plan might be in a markdown block
            plan_str = plan_str.strip()
            if plan_str.startswith("```json"):
                plan_str = plan_str[7:]
            if plan_str.endswith("```"):
                plan_str = plan_str[:-3]
            return json.loads(plan_str)
        except json.JSONDecodeError:
            self.log_action("Failed to decode LLM plan. Using a default plan.")
            return [{"tool": "statistics", "action": "describe", "params": {}}]

    def _execute_plan(self, plan: list, data: pd.DataFrame) -> list:
        """Executes the analysis plan step by step, using DataFrames."""
        results = []
        current_data = data.copy()
        for step in plan:
            tool_name = step.get("tool")
            action_name = step.get("action")
            params = step.get("params", {})
            
            if tool_name in self.tools and hasattr(self.tools[tool_name], action_name):
                tool = self.tools[tool_name]
                action = getattr(tool, action_name)
                
                # Pass data to the action
                params['data'] = current_data

                try:
                    result = action(**params)
                    if isinstance(result, pd.DataFrame):
                        current_data = result
                    
                    results.append({"title": f"Step: {action_name}", "tool": tool_name, "content": result})
                    self.log_action(f"Executed {{tool_name}}.{{action_name}} successfully.")
                except Exception as e:
                    self.log_action(f"Error executing {tool_name}.{action_name}: {e}")
                    results.append({"title": f"Error in {action_name}", "tool": tool_name, "content": str(e)})
            else:
                self.log_action(f"Tool or action not found: {tool_name}.{action_name}")

        return results

    async def run(self, **kwargs) -> dict:
        self.log_action(f"Starting analysis for objective: {self.objective}")
        
        # Load data
        try:
            data_df = pd.read_csv(self.data_path)
            self.log_action(f"Successfully loaded data from {self.data_path}")
        except Exception as e:
            self.log_action(f"Failed to load data: {e}")
            return {"error": f"Failed to load data: {e}"}

        # 1. Generate a plan
        plan = await self._generate_plan(self.objective)
        
        # 2. Execute the plan
        analysis_results = self._execute_plan(plan, data_df)
        
        # 3. Summarize and generate a report
        serializable_results = []
        for res in analysis_results:
            content = res['content']
            if isinstance(content, pd.DataFrame):
                content = content.to_string()
            elif isinstance(content, dict):
                try:
                    # Attempt to serialize, fallback to string conversion
                    json.dumps(content)
                except (TypeError, OverflowError):
                    content = {str(k): str(v) for k, v in content.items()}
            else:
                content = str(content)
            serializable_results.append({"title": res["title"], "tool": res["tool"], "content": content})

        summary_prompt = f"Based on the following results, provide a brief executive summary:\n{{json.dumps(serializable_results, indent=2, default=str)}}"
        summary = await self.call_llm(summary_prompt)
        
        report_path = self.tools["reporting"].generate_markdown_report(summary, analysis_results)
        
        self.add_result(report_path)
        self.log_action(f"Analysis complete. Report generated at {report_path}")
        return {"agent": self.name, "plan": plan, "report": report_path}

