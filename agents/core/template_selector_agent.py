from agno.agent import Agent
from agno.run import RunContext
from pathlib import Path
import json


class TemplateSelectorAgent(Agent):
    name = "template_selector_agent"

    def __init__(self, registry_path=None):
        super().__init__()
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "templates" / "registry.json"

        with open(registry_path, 'r') as f:
            self.registry = json.load(f)

    def run(self, ctx: RunContext):
        profile = ctx.state.get("profile")
        if not profile:
            raise ValueError("Profile missing")

        template = self._select_template(profile)
        ctx.state["template"] = template

    def _select_template(self, profile):
        skills = profile.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',')]

        exp = profile.get("experience_years", 0)

        if exp >= 5 and len(skills) > 5:
            template_id = "tech-developer"
        elif exp >= 10:
            template_id = "business-executive"
        else:
            template_id = "modern-minimal"

        for t in self.registry.get("templates", []):
            if t["id"] == template_id:
                return t

        return self.registry["templates"][0]