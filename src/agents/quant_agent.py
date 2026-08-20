import time
import json
from pathlib import Path

from src.llm.lm_studio_client import chat


PROMPT_PATH = Path("src/prompts/quant_agent_prompt.txt")
OUTPUT_PATH = Path("outputs/quant_agent/quant_results.json")


def run_quant_agent(publisher_data):

    system_prompt = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    user_prompt = f"""
Analyze the following quantitative publisher evidence:

{json.dumps(publisher_data, indent=2)}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = chat(messages)

    return response


if __name__ == "__main__":
    start_time = time.perf_counter()

    # Quantitative data will eventually come from quant_tools.py
    publisher_data = {
        "example": "Replace this with quant_tools output"
    }

    response = run_quant_agent(publisher_data)

    print(response)

    end_time = time.perf_counter()

    print(
        f"// Total runtime: "
        f"{end_time - start_time:.2f} seconds"
    )
