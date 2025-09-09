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

class DatasetSelectorAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Dataset_Selector",
            model_client=qwen3,
            system_message="""You are a dataset selection agent responsible for identifying appropriate input datasets from user requests.
            
            Your only job is to:
            1. Analyze the user's task description
            2. Identify which input datasets are needed for the transformation
            3. Create a minimal JSON structure with only the required datasets
            4. Hand off to JSON_Generator for actual JSON generation
            
            Output format: Return a JSON object with meta and inputs fields containing only the datasets that will be used.
            Example:
            {
              "meta": [
                {
                  "type": "INPUT_DATASET",
                  "name": "CDASH_AE",
                  "displayType": "CSV",
                  "preview": { "scope": "ALL", "config": {} },
                  "cascadeUpdateEnabled": false,
                  "inputDsId": "example_id",
                  "id": "id_123",
                  "position": { "x": 0, "y": 0 },
                  "sources": []
                }
              ],
              "inputs": [
                {
                  "dsId": "example_id",
                  "name": "CDASH_AE",
                  "fields": [
                    { "name": "字段1", "type": "STRING", "seqNo": 0 },
                    { "name": "字段2", "type": "DATE", "seqNo": 1 }
                  ]
                }
              ],
              "task_description": "User's original task description"
            }
            
            IMPORTANT: Only include datasets that are actually needed for the transformation.
            """,
            description="Selects appropriate input datasets for transformation",
            handoffs=["JSON_Generator"]
        )

class JSONGeneratorAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="JSON_Generator",
            model_client=qwen3,
            system_message=(
                f"""
                You are an expert JSON transformation generator.
                # GUIDELINES:
                {etl_json_instruction}
                # WORKFLOW:
                1. Only use fields that exist in the provided inputs. NEVER invent or hallucinate fields.
                2. If a required field is not present in inputs, find the closest semantically matching field.
                3. For example: if inputs have "年龄" but task asks for "AGE", use "年龄".
                4. If inputs have "受试者" and "SUBJID", either can be used.
                5. Output the complete JSON configuration directly in a ```json``` code block.
                7. If QA_Agent finds logic issues, revise based on feedback and output complete JSON.
                8. If JSON_Validator finds upload issues, revise and output complete JSON.
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
            system_message=f"""You are the JSON validation agent responsible for testing JSON data uploads.

            Your process:
            1. Extract JSON data string from the chat conversation (look for JSON formatted text between ```json and ``` markers)
            2. Use run_playwright_test tool with the extracted JSON data string to upload and test the JSON
            3. Analyze the returned result string from the upload test
            4. Determine success/failure based on result content

            Validation criteria:
            - SUCCESS: If result string does NOT contain "错误"
            - FAILURE: If result string contains "错误"

            Response actions:
            - If successful: Report "JSON validation PASSED - data uploaded successfully", output the original JSON data, and TERMINATE the workflow with "TERMINATE".
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
            system_message=f"""You are the QA agent responsible for checking if the transformation logic matches user requirements.
            
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


async def get_team() -> Swarm:
    """Initialize the team with the provided user input function."""

    text_termination_en = TextMentionTermination("TERMINATE")
    text_termination_cn = TextMentionTermination("终止对话")
    termination = text_termination_en | text_termination_cn | MaxMessageTermination(10)

    dataset_selector = DatasetSelectorAgent()
    json_generator = JSONGeneratorAgent()
    qa_agent = QAAgent()
    json_validator = JSONValidatorAgent()

    team = Swarm(
        participants=[dataset_selector, json_generator, qa_agent, json_validator],
        termination_condition=termination
    )
    
    return team

