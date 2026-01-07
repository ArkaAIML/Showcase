"""
DATA_AGENT.PY - Input Normalization
Converts any input format into clean plain text for downstream agents
"""

from agno.agent import Agent
from agno.run import RunContext


class DataAgent(Agent):
    name = "data_agent"

    def run(self, ctx: RunContext):
        """Normalize workflow input into raw_text"""
        if "input" not in ctx.state:
            raise ValueError("Missing 'input' in workflow state")

        input_data = ctx.state["input"]

        # Dict → readable text
        if isinstance(input_data, dict):
            raw_text = "\n".join(
                f"{key}: {value}" for key, value in sorted(input_data.items())
            )
        else:
            raw_text = str(input_data)

        ctx.state["raw_text"] = raw_text.strip()
