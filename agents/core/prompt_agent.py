from agno.agent import Agent
from agno.run import RunContext


class PromptAgent(Agent):
    name = "prompt_agent"

    def run(self, ctx: RunContext):
        raw_text = ctx.state.get("raw_text")
        if not raw_text:
            raise ValueError("raw_text missing")

        prompt = f"""Extract profile information and return ONLY valid JSON.

Format:
{{
  "name": "Full Name",
  "role": "Job Title",
  "skills": ["skill1", "skill2"],
  "experience_years": 5,
  "projects": [{{"title": "Name", "description": "Desc"}}]
}}

Resume:
{raw_text}

Return ONLY the JSON object."""

        ctx.state["prompt"] = prompt.strip()