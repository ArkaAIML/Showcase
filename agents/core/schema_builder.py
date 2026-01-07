"""
SCHEMA_BUILDER.PY - Portfolio Schema Construction Agent

Transforms parsed resume data into structured portfolio schema.
Converted to Agno Agent pattern.
"""

from agno.agent import Agent
from agno.run import RunContext
import logging

logger = logging.getLogger(__name__)


class SchemaBuilderAgent(Agent):
    """
    Agno Agent that builds portfolio schema from LLM-extracted profile data.

    INPUT (ctx.state):
        - profile: dict with name, role, skills, experience_years, projects

    OUTPUT:
        - returns schema
        - also stores schema in ctx.state["schema"]
    """

    name = "schema_builder_agent"

    async def run(self, ctx: RunContext):
        profile = ctx.state.get("profile")

        if not profile or not isinstance(profile, dict):
            raise ValueError("SchemaBuilderAgent: `profile` missing or invalid in ctx.state")

        logger.info(
            "Building schema for profile: %s",
            profile.get("name", "Unknown")
        )

        schema = {
            "profile_summary": self._build_profile_summary(profile),
            "hero": self._build_hero_schema(profile),
            "bio": self._build_bio_schema(profile),
            "projects": self._build_projects_schema(profile),
            "skills": self._build_skills_schema(profile),
            "layout_hints": self._build_layout_hints(profile),
            "generation_flags": {
                "hero": True,
                "bio": True,
                "projects": True,
            },
        }

        ctx.state["schema"] = schema
        logger.info("Schema built successfully")

        # IMPORTANT: explicit return for agent chaining
        return schema

    def _build_profile_summary(self, profile: dict) -> dict:
        skills = profile.get("skills") or []

        return {
            "name": profile.get("name"),
            "role": profile.get("role"),
            "experience_years": profile.get("experience_years", 0),
            "has_projects": bool(profile.get("projects")),
            "skill_count": len(skills) if isinstance(skills, list) else 0,
        }

    def _build_hero_schema(self, profile: dict) -> dict:
        role = profile.get("role", "Professional")
        exp = profile.get("experience_years", 0)

        tagline = role
        if isinstance(exp, int) and exp > 0:
            tagline += f" with {exp}+ years experience"

        return {
            "name": profile.get("name", "Portfolio"),
            "tagline": tagline,
            "contact": profile.get("contact", {}),
        }

    def _build_bio_schema(self, profile: dict) -> dict:
        bio_points = []

        if profile.get("role"):
            bio_points.append(f"Role: {profile['role']}")

        exp = profile.get("experience_years")
        if isinstance(exp, int) and exp > 0:
            bio_points.append(f"Experience: {exp} years")

        skills = profile.get("skills")
        if isinstance(skills, list) and skills:
            bio_points.append(f"Key skills: {', '.join(skills[:5])}")

        projects = profile.get("projects")
        if isinstance(projects, list) and projects:
            bio_points.append(f"Notable projects: {len(projects)}")

        return {
            "sections": ["introduction", "background", "highlights", "closing"],
            "reference_points": bio_points,
            "length_hint": "medium",
        }

    def _build_projects_schema(self, profile: dict) -> list:
        projects = profile.get("projects")

        if not isinstance(projects, list):
            return []

        result = []
        for idx, project in enumerate(projects):
            priority = "high" if idx < 3 else "normal"

            if isinstance(project, dict):
                result.append({
                    "id": f"project_{idx}",
                    "title": project.get("title", f"Project {idx + 1}"),
                    "description": project.get("description", ""),
                    "technologies": project.get("technologies", []),
                    "priority": priority,
                })
            elif isinstance(project, str):
                result.append({
                    "id": f"project_{idx}",
                    "title": project,
                    "description": "",
                    "technologies": [],
                    "priority": priority,
                })

        return result

    def _build_skills_schema(self, profile: dict) -> dict:
        skills = profile.get("skills")

        if not isinstance(skills, list):
            return {"raw": [], "count": 0, "categories": {}}

        categories = {
            "languages": [],
            "frameworks": [],
            "tools": [],
            "other": [],
        }

        for skill in skills:
            s = skill.lower()
            if any(x in s for x in ["python", "javascript", "java", "c++", "go", "rust"]):
                categories["languages"].append(skill)
            elif any(x in s for x in ["react", "vue", "angular", "django", "flask", "spring"]):
                categories["frameworks"].append(skill)
            elif any(x in s for x in ["docker", "git", "aws", "kubernetes", "jenkins"]):
                categories["tools"].append(skill)
            else:
                categories["other"].append(skill)

        return {
            "raw": skills,
            "count": len(skills),
            "categories": {k: v for k, v in categories.items() if v},
        }

    def _build_layout_hints(self, profile: dict) -> dict:
        sections = ["hero", "bio", "skills"]

        if isinstance(profile.get("projects"), list) and profile["projects"]:
            sections.insert(2, "projects")

        exp = profile.get("experience_years", 0)
        density = "detailed" if isinstance(exp, int) and exp >= 5 else "balanced"

        return {
            "sections": sections,
            "density": density,
            "emphasis": "projects" if profile.get("projects") else "skills",
        }
