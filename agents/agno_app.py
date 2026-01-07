import json
import asyncio
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
            DataAgent(),                 # ingests raw resume text
            PromptAgent(),               # builds LLM prompt
            GeminiAgent(),               # calls Gemini
            SchemaBuilderAgent(),        # builds structured schema
            TemplateSelectorAgent(),     # selects template
        ],
    )


app = create_app()


async def main():
    sample_input = {
        "name": "Arjun Sharma",
        "role": "Full Stack Developer",
        "skills": "Python, React, Docker, AWS",
        "experience_years": 5,
        "projects": "E-commerce platform, Chat app"
    }

    print("🚀 Starting workflow...\n")

    # Agno expects a STRING input at workflow entry
    input_text = (
        "Build a professional portfolio from this resume:\n"
        + json.dumps(sample_input, indent=2)
    )

    # ✅ Async execution (CRITICAL FIX)
    result = await app.run(input_text)

    print("\n✅ Workflow Complete!\n")

    # Safe debug output
    print(json.dumps(result.state, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
