import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.web_search.web_search_agent import WebSearchAgent
from task.tools.base_tool import BaseTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.mcp import mcp_tool
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

_DDG_MCP_URL = os.getenv('DDG_MCP_URL', "http://localhost:8051/mcp")

#TODO:
# 1. Create WebSearchApplication class and extend ChatCompletion
# 2. As a tools for WebSearchAgent you need to provide:
#   - MCP tools by _DDG_MCP_URL
#   - CalculationsAgentTool (MAS Mesh)
#   - ContentManagementAgentTool (MAS Mesh)
# 3. Override the chat_completion method of ChatCompletion, create Choice and call WebSearchAgent
class WebSearchApplication(ChatCompletion):
    def __init__(self):
        self.tools: list[BaseTool] = []

    async def chat_completion(
        self, request: Request, response: Response
    ) -> None:
        if not self.tools:
            mcp_tools: list[BaseTool] = []
            mcp_client = await MCPClient.create(mcp_server_url=_DDG_MCP_URL)
            for mcp_tool_model in await mcp_client.get_tools():
                mcp_tools.append(MCPTool(mcp_tool_model=mcp_tool_model, client=mcp_client))

            self.tools = [
                *mcp_tools,
                CalculationsAgentTool(endpoint=DIAL_ENDPOINT),
                ContentManagementAgentTool(endpoint=DIAL_ENDPOINT)
            ]

        with response.create_single_choice() as choice:
            agent = WebSearchAgent(endpoint=DIAL_ENDPOINT, tools=self.tools)
            await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response
            )
# ---
# 4. Create DIALApp with deployment_name `web-search-agent` (the same as in the core config) and impl is instance
#    of the WebSearchApplication
app: DIALApp = DIALApp()
agent_app = WebSearchApplication()
app.add_chat_completion(deployment_name="web-search-agent", impl=agent_app)

# 5. Add starter with DIALApp, port is 5003 (see core config)
if __name__ == "__main__":
    import sys

    if 'pydevd' in sys.modules:
        config = uvicorn.Config(app, port=5003, host="0.0.0.0", log_level="info")
        server = uvicorn.Server(config)
        import asyncio
        asyncio.run(server.serve())
    else:
        uvicorn.run(app, port=5003, host="0.0.0.0", log_level="info")