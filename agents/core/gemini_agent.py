from agno.agent import Agent
from agno.run import RunContext
from agno.models.gemini import Gemini
import json
import re


class GeminiAgent(Agent):
    name = "gemini_agent"

    def __init__(self):
        super().__init__()
        self.llm = Gemini(model="gemini-1.5-pro")

    def run(self, ctx: RunContext):
        prompt = ctx.state.get("prompt")
        if not prompt:
            raise ValueError("Prompt missing")

        response = self.llm.generate(prompt)

        # Extract JSON from response
        try:
            profile = json.loads(response.text)
        except:
            match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
            if match:
                profile = json.loads(match.group(1))
            else:
                raise ValueError("Could not extract JSON")

        ctx.state["profile"] = profile