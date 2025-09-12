from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

# 初始化 MCP Playwright 连接
mcp_playwright = McpWorkbench(StdioServerParams(
    command="npx",
    args=[
        "@playwright/mcp@latest",
    ],
))
