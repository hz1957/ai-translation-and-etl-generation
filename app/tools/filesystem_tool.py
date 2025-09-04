from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 初始化 MCP filesystem 连接
mcp_filesystem = McpWorkbench(StdioServerParams(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        os.path.join(PROJECT_ROOT, "files"), 
        #"/path/to/other/allowed/dir"
    ],
))
