from typing import Any, Awaitable, Callable, Optional
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat, Swarm
from autogen_agentchat.messages import TextMessage, HandoffMessage, ToolCallRequestEvent, ToolCallExecutionEvent, UserInputRequestedEvent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_core import CancellationToken
import os
from ..tools.file_tool import read_file
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
                2. Generate JSON configuration and output it directly in the chat as a formatted JSON string. 
                   IMPORTANT: Only include input tables in your JSON that you actually use for the transformation. 
                   If you don't use a source table, completely exclude it from the JSON configuration.
                3. If QA_Agent finds logic issues, revise based on specific feedback and output the revised JSON in chat.
                4. If JSON_Validator finds upload/validation issues, revise accordingly and output the revised JSON in chat.
                5. Always output the complete JSON configuration in your response.
                """
            ),
            description="Generates and revises JSON transformation interfaces",
            tools=[],
            handoffs=["QA_Agent"],
            # model_client_stream=True,
        )

class JSONValidatorAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="JSON_Validator",
            model_client=qwen3,
            system_message=f"""You are the JSON validation agent responsible for testing JSON data uploads. Reply in Chinese.

            Your process:
            1. Extract JSON data string from the chat conversation (look for JSON formatted text between ```json and ``` markers)
            2. Use run_playwright_test tool with the extracted JSON data string to upload and test the JSON
            3. Analyze the returned result string from the upload test
            4. Determine success/failure based on result content

            Validation criteria:
            - SUCCESS: If result string does NOT contain "错误"
            - FAILURE: If result string contains "错误"

            Response actions:
            - If successful: Report "JSON validation PASSED - data uploaded successfully", output the original JSON data, and TERMINATE the workflow with "终止对话".
            - If failed: Report "JSON validation FAILED" with specific error details and use transfer_to_json_generator for corrections.

            Important: Always extract the JSON data from the chat conversation before using run_playwright_test.
            """,
            description="Validates JSON using Playwright automation and web system upload simulation",
            tools=[run_playwright_test],
            handoffs=["JSON_Generator"]
        )

class QAAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="QA_Agent",
            model_client=qwen3,
            system_message=f"""You are the QA agent responsible for checking if the transformation logic matches user requirements. Reply in Chinese.
            
            Your ONLY job is to verify that the JSON transformation addresses what the user requested.
            
            Simple process:
            1. Look at the user's original request
            2. Check if the JSON transformation logic addresses that request
            3. If it matches the user's needs: forward to JSON_Validator for upload testing
            4. If it doesn't match: briefly explain what's missing and return to JSON_Generator
            
            What to check:
            - Are the right input datasets being used?
            - Is the transformation logic doing what the user asked for?
            - Are the output fields what the user requested?
            
            What NOT to check:
            - Don't validate JSON structure (that's for JSON_Validator)
            - Don't check technical implementation details
            - Don't worry about minor formatting issues
            
            Be generous in approval - if the basic logic matches the user request, send it to validation.""",
            description="Checks if transformation logic matches user requirements",
            handoffs=["JSON_Validator", "JSON_Generator"]
        )


async def get_team(user_input_func: Callable[[str, Optional[CancellationToken]], Awaitable[str]],) -> Swarm:
    """Initialize the team with the provided user input function."""

    text_termination_en = TextMentionTermination("TERMINATE")
    text_termination_cn = TextMentionTermination("终止对话")
    termination = text_termination_en | text_termination_cn | MaxMessageTermination(10)

    json_generator = JSONGeneratorAgent()
    qa_agent = QAAgent()
    json_validator = JSONValidatorAgent()

    team = Swarm(
        participants=[json_generator, qa_agent, json_validator],
        termination_condition=termination
    )
    
    return team

