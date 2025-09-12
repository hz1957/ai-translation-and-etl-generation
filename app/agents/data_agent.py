from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
# import pandas as pd
from ..config.settings import settings
import json

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
            temperature=0.1,
            max_tokens=8000
        )


class DataAnnotationAgent:
    def __init__(self, model = qwen3):
        self.model = model

    async def map_table(self, target_table_desc: str, source_data_description: str):
        """Map a source table to a target table based on descriptions."""

        system_prompt = """You are an expert in mapping TABLES across different sources.
        Your task is to determine the best match for a target table from the source tables based on their descriptions.

        Your response must follow these rules:
        - Compare the **target table's description** with the **descriptions of the source tables**.
        - If a source table aligns well with the target table, return:
          {
            "source_table": "<best_match_table_name>",
            "confidence": <float between 0 and 1>
          }
        - If no source table is a good match, return:
          {
            "source_table": "Nothing Compatible",
            "confidence": 0.0
          }
        - Confidence must reflect the likelihood that the mapping is correct.
        - Only output valid JSON, nothing else.
        """

        user_prompt = f"""The target table and its description are as follows:
        {target_table_desc}

        Here are the source tables with their descriptions:
        {source_data_description}

        Your output must be JSON with "source_table" and "confidence" fields only."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                UserMessage(content=user_prompt, source="user")
            ]
            result = await self.model.create(messages)
            response = json.loads(str(result.content).strip())
            if response['confidence'] < 0.7:
                return {"source_table": "Nothing Compatible", "confidence": response['confidence']}
            return response
        except Exception as e:
            print(f"Error in map_table: {e}")
            return {"source_table": "Nothing Compatible", "confidence": 0.0}
        
    async def map_field(self, target_field_name: str, target_field_desc: str, source_data_description: str):
        """Map a source field to a target field based on descriptions."""

        system_prompt = """You are an expert in mapping FIELDS across different tables.
        Your task is to determine the best match for a target field from the source table based on their descriptions.

        Your response must follow these rules:
        - Compare the **target field's description** with the **descriptions of all source fields**.
        - If a source field aligns well with the target field, return:
          {
            "source_field": "<best_match_field_name>",
            "confidence": <float between 0 and 1>
          }
        - If no source field is a good match, return:
          {
            "source_field": "Nothing Compatible",
            "confidence": 0.0
          }
        - Confidence must reflect the likelihood that the mapping is correct.
        - Only output valid JSON, nothing else.
        """

        user_prompt = f"""The target field and its description are as follows:
        Target field: {target_field_name}
        Description: {target_field_desc}

        Here are the source fields with their descriptions:
        {source_data_description}

        Your output must be JSON with "source_field" and "confidence" fields only."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                UserMessage(content=user_prompt, source="user")
            ]
            result = await self.model.create(messages)
            response = json.loads(str(result.content).strip())
            if response['confidence'] < 0.7:
                return {"source_field": "Nothing Compatible", "confidence": response['confidence']}
            return response
        except Exception as e:
            print(f"Error in map_field: {e}")
            return {"source_field": "Nothing Compatible", "confidence": 0.0}
    
    # async def describe_table(self, df_head: pd.DataFrame):
    #     """Generate a JSON description of each field in a table."""
    #     system_prompt = """You are a data analysis expert. When given a pandas DataFrame's head output,
    #     carefully analyze each field and provide a comprehensive yet concise description. Your response
    #     must be a valid JSON object where:
    #     - Keys are field names
    #     - Values are detailed descriptions capturing the field's nature, potential meaning, and data characteristics
    #     - Descriptions should be precise, informative, and max 100 characters long"""

    #     user_prompt = f"""Analyze the following DataFrame head and provide a JSON description 
    #     of each field's characteristics and potential meaning:
    #     {df_head.to_string()}
    #     Format your response as a valid JSON object with descriptive insights for each field."""

    #     try:
    #         messages = [
    #             SystemMessage(content=system_prompt),
    #             UserMessage(content=user_prompt, source="user")
    #         ]
    #         result = await self.model.create(messages)
    #         return result.content
    #     except Exception as e:
    #         print(f"Error in describe_dataset: {e}")
    #         return {}



