# agents/agno_app.py
from agno.workflow import Workflow

from core.data_agent import DataAgent
from core.prompt_agent import PromptAgent
from core.gemini_agent import GeminiAgent
from core.schema_builder import SchemaBuilderAgent
from core.template_selector_agent import TemplateSelectorAgent


def create_app():
    return Workflow(
        name="Portfolio-Builder",
        agents=[
            DataAgent(),
            PromptAgent(),
            GeminiAgent(),
            SchemaBuilderAgent(),
            TemplateSelectorAgent(),
        ],
    )


app = create_app()


if __name__ == "__main__":
    sample_input = {
        "name": "Arjun Sharma",
        "role": "Full Stack Developer",
        "skills": "Python, React, Docker, AWS",
        "experience": "5 years",
        "projects": "E-commerce platform, Chat app"
    }

    print("🚀 Starting workflow...\n")
    result = app.run(input=sample_input)

    print("\n✅ Workflow Complete!")
    print(f"Profile: {result.state.get('profile', {}).get('name')}")
    print(f"Schema: {result.state.get('schema', {}).get('profile_summary')}")
    print(f"Template: {result.state.get('template', {}).get('name')}")