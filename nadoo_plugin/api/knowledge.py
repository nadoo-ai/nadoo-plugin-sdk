"""
Knowledge Base API client
"""

from typing import Any, Dict, List
from pydantic import BaseModel

from ..context import PluginContext
from ..exceptions import KnowledgeSearchError
from .client import BaseAPIClient


class KnowledgeSearchResult(BaseModel):
    """Knowledge base search result"""

    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, Any]


class KnowledgeClient(BaseAPIClient):
    """
    Knowledge Base API client

    Allows plugins to search knowledge bases.
    """

    def __init__(self, base_url: str, token: str, context: PluginContext):
        super().__init__(base_url, token, context)

    def search(
        self,
        knowledge_base_uuid: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[KnowledgeSearchResult]:
        """
        Search a knowledge base

        Args:
            knowledge_base_uuid: Knowledge base UUID
            query: Search query
            top_k: Number of results to return (1-20)
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of search results

        Raises:
            PluginPermissionError: If 'knowledge_access' permission not granted
            KnowledgeSearchError: If search fails

        Example:
            results = self.api.knowledge.search(
                knowledge_base_uuid="kb-uuid-123",
                query="How to use plugins?",
                top_k=5
            )

            for result in results:
                print(f"{result.score:.2f}: {result.content}")
        """
        # Check permission
        self.context.require_permission("knowledge_access")

        # Check if knowledge base is allowed
        if knowledge_base_uuid not in self.context.allowed_kb_ids:
            from ..exceptions import PluginPermissionError

            raise PluginPermissionError(
                f"Knowledge base {knowledge_base_uuid} is not accessible. "
                f"Add it to application's allowed knowledge bases."
            )

        # Validate parameters
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")
        if not 0 <= score_threshold <= 1:
            raise ValueError("score_threshold must be between 0 and 1")

        # Log API call
        self.context.debug(f"Knowledge search: {query[:50]}... (top_k={top_k})")

        # Prepare request
        payload = {
            "knowledge_base_uuid": knowledge_base_uuid,
            "query": query,
            "top_k": top_k,
            "score_threshold": score_threshold,
        }

        try:
            # Make API call (with automatic tracking)
            response = self._request(
                "POST", "/internal-api/plugin/invoke/knowledge/search", json=payload, api_type="knowledge"
            )

            # Parse results
            results = [KnowledgeSearchResult(**item) for item in response]

            # Log result
            self.context.info(f"Knowledge search: {len(results)} results")

            return results

        except Exception as e:
            self.context.error(f"Knowledge search failed: {str(e)}")
            raise KnowledgeSearchError(f"Failed to search knowledge base: {str(e)}") from e
