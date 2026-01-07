from agno.agent import Agent
from agno.run import RunContext
from pathlib import Path
import json


class TemplateSelectorAgent(Agent):
    name = "template_selector_agent"

    def __init__(self, registry_path: str | Path | None = None):
        super().__init__()

        # Resolve registry path safely
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "templates" / "registry.json"

        registry_path = Path(registry_path).resolve()

        if not registry_path.exists():
            raise FileNotFoundError(f"Template registry not found at: {registry_path}")

        try:
            self.registry = json.loads(
                registry_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in registry file: {registry_path}"
            ) from e

    async def run(self, ctx: RunContext):
        profile = ctx.state.get("profile")

        if not profile or not isinstance(profile, dict):
            raise ValueError(
                "TemplateSelectorAgent: `profile` missing or invalid in ctx.state"
            )

        template = self._select_template(profile)

        ctx.state["template"] = template

        # IMPORTANT: return for agent chaining
        return template

    def _select_template(self, profile: dict) -> dict:
        skills = profile.get("skills", [])
