"""
LLM API client
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from ..context import PluginContext
from ..exceptions import LLMInvocationError
from .client import BaseAPIClient


class LLMResponse(BaseModel):
    """Response from LLM invocation"""

    content: str
    model_uuid: str
    model_name: str
    model_id: str
    provider: str
    usage: Dict[str, int]  # {prompt_tokens, completion_tokens, total_tokens}
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


class LLMClient(BaseAPIClient):
    """
    LLM API client

    Allows plugins to invoke AI models configured in the workspace.
    """

    def __init__(self, base_url: str, token: str, context: PluginContext):
        super().__init__(base_url, token, context)

    def invoke(
        self,
        messages: List[Dict[str, str]],
        model_uuid: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop: Optional[List[str]] = None,
    ) -> LLMResponse:
        """
        Invoke an LLM model

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_uuid: Model UUID (None = use application's default model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            stop: Stop sequences

        Returns:
            LLMResponse with content, usage, and metadata

        Raises:
            PluginPermissionError: If 'llm_access' permission not granted
            LLMInvocationError: If invocation fails

        Example:
            response = self.api.llm.invoke(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hello!"}
                ],
                temperature=0.7
            )
            print(response.content)
            print(f"Used {response.usage['total_tokens']} tokens")
        """
        # Check permission
        self.context.require_permission("llm_access")

        # Log API call
        self.context.debug(f"LLM invoke: {len(messages)} messages, temp={temperature}")

        # Prepare request
        payload = {
            "messages": messages,
            "temperature": temperature,
        }

        if model_uuid:
            payload["model_uuid"] = model_uuid
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if top_p:
            payload["top_p"] = top_p
        if stop:
            payload["stop"] = stop

        try:
            # Make API call (with automatic tracking via api_type parameter)
            response_data = self._request("POST", "/internal-api/plugin/invoke/llm", json=payload, api_type="llm")

            # Parse response
            response = LLMResponse(**response_data)

            # Log result
            self.context.info(
                f"LLM invoked: {response.model_name}, {response.usage['total_tokens']} tokens"
            )

            return response

        except Exception as e:
            self.context.error(f"LLM invocation failed: {str(e)}")
            raise LLMInvocationError(f"Failed to invoke LLM: {str(e)}") from e
