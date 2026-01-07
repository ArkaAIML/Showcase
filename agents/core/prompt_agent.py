from agno.agent import Agent
from agno.run import RunContext


class PromptAgent(Agent):
    name = "prompt_agent"
    model = "gpt-4o-mini"  # or whatever model your project uses

    async def run(self, ctx: RunContext):
        raw_text = ctx.state.get("raw_text")

        if not raw_text or not isinstance(raw_text, str):
            raise ValueError("`raw_text` is missing or invalid in ctx.state")

        prompt = f"""
Extract profile information and return ONLY valid JSON.

Format:
{{
  "name": "Full Name",
  "role": "Job Title",
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "projects": []
}}

IMPORTANT:
- name, role, and skills are REQUIRED
- experience_years is OPTIONAL (use 0 if not found)
- projects is OPTIONAL (use empty array [] if not found)

Resume:
{raw_text}

Return ONLY the JSON object.
""".strip()

        # store for downstream agents or LLM call
        ctx.state["prompt"] = prompt

        # return explicitly (important)
        return {
            "prompt": prompt
        }
