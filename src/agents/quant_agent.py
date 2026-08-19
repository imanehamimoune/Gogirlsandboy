from pathlib import Path

from src.llm.lm_studio_client import ask_llm


PROMPT_PATH = Path("src/prompts/quant_agent_prompt.txt")


def run_quant_agent(publisher_data):

    system_prompt = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    user_prompt = f"""
    Analyze the following quantitative publisher evidence:

    {publisher_data}
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

    return ask_llm(
        messages,
        model="your-model"
    )
