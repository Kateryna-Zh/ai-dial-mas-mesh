from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class ContentManagementAgentTool(BaseAgentTool):

    #TODO:
    # Provide implementations of deployment_name (in core config), name, description and parameters.
    # Don't forget to mark them as @property
    # Parameters:
    #   - prompt: string. Required.
    #   - propagate_history: boolean
    @property
    def deployment_name(self) -> str:
        return "content-management-agent"
    
    @property
    def name(self) -> str:
        return "content_management_agent"
    
    @property
    def description(self) -> str:
        return "Content Management Agent. Primary goal is to help users manage and organize their digital content effectively. Equipped with: File System Access, Metadata Extraction, Content Categorization, and Search and Retrieval tools."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt for the content management agent.",
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate conversation history.",
                }
            },
            "required": ["prompt"]
        }
