import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.content_management.content_management_agent import ContentManagementAgent
from task.agents.content_management.tools.files.file_content_extraction_tool import FileContentExtractionTool
from task.agents.content_management.tools.rag.document_cache import DocumentCache
from task.agents.content_management.tools.rag.rag_tool import RagTool
from task.tools.base_tool import BaseTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

#TODO:
# 1. Create ContentManagementApplication class and extend ChatCompletion
# 2. As a tools for ContentManagementAgent you need to provide:
#   - FileContentExtractionTool
#   - RagTool
#   - CalculationsAgentTool (MAS Mesh)
#   - WebSearchAgentTool (MAS Mesh)
# 3. Override the chat_completion method of ChatCompletion, create Choice and call ContentManagementAgent
# ---
class ContentManagementApplication(ChatCompletion):
    def __init__(self):
        self.tools: list[BaseTool] = []

    async def chat_completion(
        self, request: Request, response: Response
    ) -> None:
        if not self.tools:
            self.tools = [
                FileContentExtractionTool(endpoint=DIAL_ENDPOINT),
                RagTool(endpoint=DIAL_ENDPOINT, 
                        document_cache=DocumentCache.create(),
                        deployment_name=DEPLOYMENT_NAME),
                CalculationsAgentTool(endpoint=DIAL_ENDPOINT),
                WebSearchAgentTool(endpoint=DIAL_ENDPOINT)
            ]

        with response.create_single_choice() as choice:
            agent = ContentManagementAgent(endpoint=DIAL_ENDPOINT, tools=self.tools)
            await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response
            )

# 4. Create DIALApp with deployment_name `content-management-agent` (the same as in the core config) and impl is instance
#    of the ContentManagementApplication
app = DIALApp()
agent_app = ContentManagementApplication()
app.add_chat_completion(
    deployment_name="content-management-agent",
    impl=agent_app
)
# 5. Add starter with DIALApp, port is 5002 (see core config)
if __name__ == "__main__":
    import sys

    if 'pydevd' in sys.modules:
        config = uvicorn.Config(app, port=5002, host="0.0.0.0", log_level="info")
        server = uvicorn.Server(config)
        import asyncio
        asyncio.run(server.serve())
    else:
        uvicorn.run(app, port=5002, host="0.0.0.0", log_level="info")
