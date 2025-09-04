from ..agents.data_agent import DataAnnotationAgent as DataAgent
import asyncio
import json
import os
from typing import Dict, Any

def format_source_table_desc(table):
    """Format a single source table description for LLM prompting."""
    table_desc = f"Table: {table['tableName']}\n"
    table_desc += "Structure and Data:\n"
    # Create a header row
    headers = "  ".join(field['fieldName'] for field in table['fields'])
    table_desc += f"  {headers}\n"
    # Add field descriptions
    for field in table['fields']:
        table_desc += f"  {field['fieldName']} ({field['fieldType']}): {field['fieldLabel']}\n"
    # Add example data
    table_desc += "Example Rows:\n"
    for row in table['detailData'][:2]:
        values = "  ".join(str(row.get(field['fieldName'], '')) for field in table['fields'])
        table_desc += f"  {values}\n"
    table_desc += "\n"
    return table_desc

async def map_data_schemas(source_data: Dict[str, Any]):
    """Map source data tables and fields to target schema using semantic analysis.
    
    Args:
        source_data: Dictionary containing source data in the format of source_data_case.json
        target_schema: Dictionary containing target schema in the format of target_schema.json
    
    Returns:
        Dictionary containing mapping results with success status, version info, table mappings, and statistics
    """
    data_agent = DataAgent()
    
    target_schema = source_data.get('labelVersion', {})
    # Use provided target_schema directly
    if not target_schema:
        raise ValueError("target_schema is required and cannot be empty")
    
    # Use provided source_data directly
    if not source_data:
        raise ValueError("source_data is required and cannot be empty")
    
    # Extract descriptions for all source tables
    source_tables_desc = ""
    for table in source_data['originalData']['tables']:
        source_tables_desc += format_source_table_desc(table)
    
    # Result structure
    result = {
        "success": True,
        "errorMessage": None,
        "standardVersion": {
            "versionId": source_data.get('labelVersion', {}).get('versionId', 'unknown'),
            "versionName": source_data.get('labelVersion', {}).get('versionName', 'Unknown Standard'),
            "description": source_data.get('labelVersion', {}).get('description', 'No description available')
        },
        "tableMappings": [],
        "statistics": {
            "totalTables": 0,
            "totalFields": 0,
            "mappedTables": 0,
            "mappedFields": 0,
            "unmappedFields": 0,
            "mappingSuccessRate": 0.0
        }
    }
    
    total_tables = 0
    mapped_tables = 0
    total_fields = 0
    mapped_fields = 0
    
    async def process_table(target_table):
        nonlocal total_tables, mapped_tables, total_fields, mapped_fields
        total_tables += 1
        target_table_info = f"Table: {target_table['name']}\n"
        target_table_info += "Fields:\n"
        for field in target_table['fields']:
            target_table_info += f"  - {field['name']} ({field.get('type', 'unknown')}): {field.get('description', 'No description provided')}\n"
        
        # Map table
        table_result = await data_agent.map_table(
            target_table_desc=target_table_info,
            source_data_description=source_tables_desc
        )
        
        # Check table compatibility with >= 0.86 confidence threshold
        if table_result['source_table'] == "Nothing Compatible" or table_result['confidence'] < 0.86:
            print(f"Target table '{target_table['name']}' has no compatible source table (confidence: {table_result['confidence']:.3f})")
            return {
                "targetTable": target_table['name'],
                "sourceTable": None,
                "mappings": {},
                "confidence": table_result['confidence'],
                "description": f"No compatible source table (confidence < 0.86): {table_result['confidence']:.3f}"
            }
        
        # Found compatible table
        mapped_tables += 1
        source_table_name = table_result['source_table']
        
        # Find the source table
        source_table = next((t for t in source_data['originalData']['tables']
                          if t['tableName'] == source_table_name), None)
        if not source_table:
            print(f"Source table '{source_table_name}' not found in source data.")
            return {
                "targetTable": target_table['name'],
                "sourceTable": None,
                "mappings": {},
                "confidence": table_result['confidence'],
                "description": "Source table not found"
            }
        
        # Format description for just this source table
        single_source_desc = format_source_table_desc(source_table)
        
        # Initialize mappings for this table
        field_mappings = {}
        
        print(f"Mapping target table '{target_table['name']}' to source table '{source_table_name}' (confidence: {table_result['confidence']:.3f})")
        # Create async function for field mapping within this table
        async def map_single_field(target_field):
            nonlocal total_fields
            total_fields += 1
            field_result = await data_agent.map_field(
                target_field_name=target_field['name'],
                target_field_desc=target_field.get('description', 'No description provided'),
                source_data_description=single_source_desc
            )
            
            # Check field compatibility with >= 0.8 confidence threshold
            if field_result['source_field'] == "Nothing Compatible" or field_result['confidence'] < 0.8:
                print(f"  Target field '{target_field['name']}' has no compatible source field (confidence: {field_result['confidence']:.3f})")
                return None
            else:
                nonlocal mapped_fields
                mapped_fields += 1
                print(f"  Target field '{target_field['name']}' matched to source: {field_result['source_field']} (confidence: {field_result['confidence']:.3f})")
                return (target_field['name'], field_result['source_field'])
        
        # Create tasks for all fields in this table and run them concurrently
        field_tasks = [map_single_field(target_field) for target_field in target_table['fields']]
        field_results = await asyncio.gather(*field_tasks)
        
        # Process the results and build the field mappings dictionary
        for result in field_results:
            if result is not None:
                field_mappings[result[0]] = result[1]
        
        # Return table mapping to be added to results
        return {
            "targetTable": target_table['name'],
            "sourceTable": source_table_name,
            "mappings": field_mappings,
            "confidence": table_result['confidence'],
            "description": f"Mapped table with confidence: {table_result['confidence']:.3f}"
        }
    
    # Create tasks for all target tables and run them concurrently
    table_tasks = [process_table(target_table) for target_table in target_schema['tables']]
    table_mappings = await asyncio.gather(*table_tasks)
    
    # Add all table mappings to results
    for table_mapping in table_mappings:
        result["tableMappings"].append(table_mapping)
    
    # Update statistics
    result["statistics"]["totalTables"] = total_tables
    result["statistics"]["totalFields"] = total_fields
    result["statistics"]["mappedTables"] = mapped_tables
    result["statistics"]["mappedFields"] = mapped_fields
    result["statistics"]["unmappedFields"] = total_fields - mapped_fields
    result["statistics"]["mappingSuccessRate"] = mapped_fields / total_fields if total_fields > 0 else 0.0
    
    return result