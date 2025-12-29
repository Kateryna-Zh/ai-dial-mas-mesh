import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.calculations.calculations_agent import CalculationsAgent
from task.agents.calculations.tools.simple_calculator_tool import SimpleCalculatorTool
from task.tools.base_tool import BaseTool
from task.agents.calculations.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME


#TODO:
# 1. Create CalculationsApplication class and extend ChatCompletion
class CalculationsApplication(ChatCompletion):
    def __init__(self):
        self.tools: list[BaseTool] = []
    
# 2. As a tools for CalculationsAgent you need to provide:
#   - SimpleCalculatorTool
#   - PythonCodeInterpreterTool
#   - ContentManagementAgentTool (MAS Mesh)
#   - WebSearchAgentTool (MAS Mesh)   
# 3. Override the chat_completion method of ChatCompletion, create Choice and call CalculationsAgent
    async def chat_completion(
        self, request: Request, response: Response
    ) -> None:
        if not self.tools:
            py_interpreter_mcp_url = os.getenv('PYINTERPRETER_MCP_URL', "http://localhost:8050/mcp")
            print(f"PYINTERPRETER_MCP_URL {py_interpreter_mcp_url}")
            
            self.tools = [
                SimpleCalculatorTool(),
                ContentManagementAgentTool(endpoint=DIAL_ENDPOINT),
                WebSearchAgentTool(endpoint=DIAL_ENDPOINT),
                await PythonCodeInterpreterTool.create(
                    mcp_url=py_interpreter_mcp_url,
                    dial_endpoint= DIAL_ENDPOINT,
                    tool_name="execute_code"
                )
            ]
        
        with response.create_single_choice() as choice:
            agent = CalculationsAgent(endpoint=DIAL_ENDPOINT, tools=self.tools)
            await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response
            )           

# ---
# 4. Create DIALApp with deployment_name `calculations-agent` (the same as in the core config) and impl is instance of
#    the CalculationsApplication
app = DIALApp()
agent_app = CalculationsApplication()
app.add_chat_completion(
    deployment_name="calculations-agent",
    impl=agent_app
)
# 5. Add starter with DIALApp, port is 5001 (see core config)
if __name__ == "__main__":
    import sys

    if 'pydevd' in sys.modules:
        config = uvicorn.Config(app, port=5001, host="0.0.0.0", log_level="info")
        server = uvicorn.Server(config)
        import asyncio
        asyncio.run(server.serve())
    else:
        uvicorn.run(app, port=5001, host="0.0.0.0", log_level="info")