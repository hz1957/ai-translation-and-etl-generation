from typing import Any, Awaitable, Callable, Optional
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat, Swarm
from autogen_agentchat.messages import TextMessage, HandoffMessage, ToolCallRequestEvent, ToolCallExecutionEvent, UserInputRequestedEvent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_core import CancellationToken
import os
from ..tools.read_file_tool import read_file
from ..tools.upload_json_tool import run_playwright_test


from autogen_ext.models.openai import OpenAIChatCompletionClient
# import pandas as pd
from ..config.settings import settings

qwen3 = OpenAIChatCompletionClient(
            model="Qwen",
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_url_agent,
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "structured_output": False,
                "family": "deepseek"
            },
            seed = 101,
            temperature=0.2,
            max_tokens=8000
        )


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
# use read_file tool to read the ETL JSON node documentation
etl_json_instruction = read_file(os.path.join(FILES_DIR, "etl_ui_json_nodes.md"))

def store_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File saved to {path}"

class JSONGeneratorAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="JSON_Generator",
            model_client=qwen3,
            system_message=(
                f"""
                You are an expert JSON transformation generator. Reply in Chinese.
                # GUIDELINES:
                {etl_json_instruction}
                # WORKFLOW:
                1. According to the descriptions on input data, output data and transformation, select appropriate table(s) from the source data for generating the target table.
                2. Generate a JSON file ONLY under {FILES_DIR} named "genai_etl_config" that represents the transformation.
                3. If QA_Agent finds logic issues, revise based on specific feedback.
                4. If JSON_Validator finds upload/validation issues, revise accordingly.
                5. If you revised the file, store your revised JSON file under {FILES_DIR} named "genai_etl_config.json".
                """
            ),
            description="Generates and revises JSON transformation interfaces",
            tools=[store_file],
            handoffs=["QA_Agent"],
            # model_client_stream=True,
        )

class JSONValidatorAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="JSON_Validator",
            model_client=qwen3,
            system_message=f"""You are the JSON validation agent responsible for testing JSON file uploads. Reply in Chinese.

            Your process:
            1. Receive JSON file name (e.g., genai_etl_config.json) from QA_Agent
            2. Use run_playwright_test tool with the file name to upload the JSON file
            3. Analyze the returned result string from the upload test
            4. Determine success/failure based on result content

            Validation criteria:
            - SUCCESS: If result string does NOT contain "错误"
            - FAILURE: If result string contains "错误"

            Response actions:
            - If successful: Report "JSON validation PASSED - file uploaded successfully" and use transfer_to_user_proxy for final approval.
            - If failed: Report "JSON validation FAILED" with specific error details and use transfer_to_json_generator for corrections.

            """,
            description="Validates JSON using Playwright automation and web system upload simulation",
            tools=[run_playwright_test],
            handoffs=["JSON_Generator", "User_Proxy"]
        )

class QAAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="QA_Agent",
            model_client=qwen3,
            system_message=f"""You are the QA agent responsible for logic verification. Reply in Chinese.
            Review JSON file named "genai_etl_config" under {FILES_DIR}.
            Your responsibilities:
            1. Check if input/output mappings match user specifications
            2. Verify transformation logic is consistent with user demands
            3. Decision:
            - If logic is correct: provide JSON file name (e.g., genai_etl_config.json) to JSON_Validator to verify the JSON file.
            - If NOT correct: specify mismatches and return to JSON_Generator for revision.

            Do not approve unless the JSON perfectly matches user needs.""",
            description="Performs QA check to ensure JSON logic matches user requirements",
            handoffs=["JSON_Validator", "JSON_Generator"]
        )


async def get_team(user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],) -> Swarm:
    """Initialize the team with the provided user input function."""
    user_proxy = UserProxyAgent(
    name="User_Proxy",
    input_func=user_input_func,
    description="Manage user approval and feedback",
)
    text_termination_en = TextMentionTermination("TERMINATE")
    text_termination_cn = TextMentionTermination("终止对话")
    text_termination_user = TextMentionTermination("APPROVE")
    termination = text_termination_en | text_termination_cn | text_termination_user | MaxMessageTermination(40)

    json_generator = JSONGeneratorAgent()
    qa_agent = QAAgent()
    json_validator = JSONValidatorAgent()
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        input_func=input,
        description="Manage user approval and feedback",
    )
    
    team = Swarm(
        participants=[json_generator, qa_agent, json_validator, user_proxy],
        termination_condition=termination
    )
    
    return team

