"""
LLM Summarizer Plugin - Demonstrates LLM integration in Nadoo plugins

This plugin shows how to use the Internal API to invoke LLMs and other Nadoo services.
"""

from typing import Optional
from nadoo_plugin import NadooPlugin, tool, parameter, validator, permission_required


class LLMSummarizerPlugin(NadooPlugin):
    """
    Text summarization plugin using LLM integration

    Features:
    - Text summarization with customizable length
    - Keyword extraction
    - Question answering based on context
    - Knowledge base integration
    - Persistent caching with storage
    """

    def __init__(self):
        super().__init__()

    @tool(name="summarize", description="Summarize a long text into a shorter version")
    @parameter("text", type="string", required=True, description="Text to summarize")
    @parameter("length", type="string", required=False, default="medium", description="Summary length (short, medium, long)")
    @parameter("style", type="string", required=False, default="informative", description="Summary style (informative, technical, casual)")
    @validator("length", allowed_values=["short", "medium", "long"])
    @validator("style", allowed_values=["informative", "technical", "casual"])
    @validator("text", min_length=10, max_length=50000)
    @permission_required("llm_access", "storage")
    def summarize(self, text: str, length: str = "medium", style: str = "informative") -> dict:
        """
        Summarize text using LLM

        Args:
            text: Text to summarize
            length: Desired summary length
            style: Summary style

        Returns:
            dict with summary and metadata
        """
        self.context.start_step("summarization")
        self.context.info(f"Summarizing text (length={length}, style={style})")
        self.context.watch_variable("text_length", len(text))

        # Check cache
        cache_key = f"summary:{hash(text)}:{length}:{style}"
        try:
            cached = self.api.storage.get(cache_key)
            if cached and isinstance(cached, dict) and "summary" in cached:
                self.context.info("Using cached summary")
                self.context.end_step()
                return {
                    "success": True,
                    "summary": cached["summary"],
                    "from_cache": True,
                    "length": length,
                    "style": style,
                }
        except Exception as e:
            self.context.warn(f"Cache retrieval failed: {str(e)}")

        # Define length constraints
        length_constraints = {
            "short": "in 2-3 sentences",
            "medium": "in 1 paragraph (4-6 sentences)",
            "long": "in 2-3 paragraphs",
        }

        # Define style instructions
        style_instructions = {
            "informative": "Use clear, neutral language suitable for general audiences.",
            "technical": "Use precise technical terminology and maintain academic tone.",
            "casual": "Use conversational language and simple explanations.",
        }

        # Prepare LLM prompt
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that summarizes text. {style_instructions[style]}",
            },
            {
                "role": "user",
                "content": f"Please summarize the following text {length_constraints[length]}:\n\n{text}",
            },
        ]

        self.context.trace("llm_invocation_prepared", {"message_count": len(messages)})

        # Invoke LLM with error handling
        try:
            response = self.api.llm.invoke(messages=messages, temperature=0.7, max_tokens=500)

            if not response or not hasattr(response, 'content') or not response.content:
                self.context.end_step()
                return {
                    "success": False,
                    "error": "LLM returned empty or invalid response"
                }

            summary = response.content.strip()
            if not summary:
                self.context.end_step()
                return {
                    "success": False,
                    "error": "LLM returned empty summary"
                }

            self.context.watch_variable("summary_length", len(summary))

            # Cache the result (TTL: 1 hour)
            try:
                self.api.storage.set(cache_key, {"summary": summary}, ttl=3600)
                self.context.trace("summary_cached", {"cache_key": cache_key})
            except Exception as e:
                self.context.warn(f"Failed to cache summary: {str(e)}")

            self.context.end_step()

            return {
                "success": True,
                "summary": summary,
                "from_cache": False,
                "length": length,
                "style": style,
                "model": response.model_name,
                "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0,
            }
        except Exception as e:
            self.context.end_step()
            return {
                "success": False,
                "error": f"LLM invocation failed: {str(e)}"
            }

    @tool(name="extract_keywords", description="Extract key terms and concepts from text")
    @parameter("text", type="string", required=True, description="Text to analyze")
    @parameter("max_keywords", type="number", required=False, default=10, description="Maximum number of keywords to extract")
    @validator("text", min_length=10, max_length=50000)
    @validator("max_keywords", min_value=1, max_value=50)
    @permission_required("llm_access")
    def extract_keywords(self, text: str, max_keywords: int = 10) -> dict:
        """
        Extract keywords from text using LLM

        Args:
            text: Text to analyze
            max_keywords: Maximum keywords to extract

        Returns:
            dict with keywords and relevance scores
        """
        self.context.start_step("keyword_extraction")
        self.context.info(f"Extracting up to {max_keywords} keywords")

        messages = [
            {
                "role": "system",
                "content": "You are a text analysis assistant. Extract the most important keywords and concepts from the given text.",
            },
            {
                "role": "user",
                "content": f"Extract the {max_keywords} most important keywords or key phrases from this text. "
                f"Return ONLY a comma-separated list of keywords, nothing else:\n\n{text}",
            },
        ]

        try:
            response = self.api.llm.invoke(messages=messages, temperature=0.3, max_tokens=200)

            if not response or not hasattr(response, 'content') or not response.content:
                self.context.end_step()
                return {
                    "success": False,
                    "error": "LLM returned empty or invalid response"
                }

            # Parse keywords
            keywords_text = response.content.strip()
            keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()][:max_keywords]

            if not keywords:
                self.context.end_step()
                return {
                    "success": False,
                    "error": "No keywords could be extracted from text"
                }

            self.context.watch_variable("keywords_found", len(keywords))
            self.context.trace("keywords_extracted", {"count": len(keywords)})
            self.context.end_step()

            return {
                "success": True,
                "keywords": keywords,
                "count": len(keywords),
                "model": response.model_name,
                "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0,
            }
        except Exception as e:
            self.context.end_step()
            return {
                "success": False,
                "error": f"Keyword extraction failed: {str(e)}"
            }

    @tool(name="answer_question", description="Answer a question based on provided context")
    @parameter("context", type="string", required=True, description="Context text containing information")
    @parameter("question", type="string", required=True, description="Question to answer")
    @parameter("use_knowledge_base", type="boolean", required=False, default=False, description="Search knowledge base for additional context")
    @parameter("knowledge_base_uuid", type="string", required=False, description="Knowledge base UUID (required if use_knowledge_base=true)")
    @validator("context", min_length=10, max_length=50000)
    @validator("question", min_length=3, max_length=500)
    @permission_required("llm_access")
    def answer_question(
        self,
        context: str,
        question: str,
        use_knowledge_base: bool = False,
        knowledge_base_uuid: Optional[str] = None,
    ) -> dict:
        """
        Answer question based on context using LLM

        Args:
            context: Context text
            question: Question to answer
            use_knowledge_base: Whether to search knowledge base
            knowledge_base_uuid: Knowledge base to search (if enabled)

        Returns:
            dict with answer and sources
        """
        self.context.start_step("question_answering")
        self.context.info(f"Answering question: {question[:100]}")
        self.context.watch_variable("use_kb", use_knowledge_base)

        full_context = context
        kb_results = []

        # Optionally augment with knowledge base
        if use_knowledge_base:
            if not knowledge_base_uuid:
                return {
                    "success": False,
                    "error": "knowledge_base_uuid is required when use_knowledge_base=true",
                }

            self.context.require_permission("knowledge_access")

            # Search knowledge base
            self.context.trace("kb_search_started", {"query": question})
            try:
                kb_results = self.api.knowledge.search(
                    knowledge_base_uuid=knowledge_base_uuid, query=question, top_k=3, score_threshold=0.7
                )

                if kb_results:
                    # Filter out results with None content
                    kb_context = "\n\n".join([result.content for result in kb_results if result.content])
                    if kb_context:
                        full_context = f"{context}\n\nAdditional information from knowledge base:\n{kb_context}"
                        self.context.trace("kb_results_added", {"result_count": len(kb_results)})
            except Exception as e:
                self.context.warn(f"Knowledge base search failed: {str(e)}")
                self.context.trace("kb_search_failed", {"error": str(e)})
                kb_results = []

        # Prepare LLM prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on provided context. "
                "If the answer cannot be found in the context, say so clearly.",
            },
            {
                "role": "user",
                "content": f"Context:\n{full_context}\n\nQuestion: {question}\n\nAnswer:",
            },
        ]

        try:
            response = self.api.llm.invoke(messages=messages, temperature=0.5, max_tokens=500)

            if not response or not hasattr(response, 'content') or not response.content:
                self.context.end_step()
                return {
                    "success": False,
                    "error": "LLM returned empty or invalid response"
                }

            answer = response.content.strip()
            self.context.watch_variable("answer_length", len(answer))

            self.context.end_step()

            result = {
                "success": True,
                "answer": answer,
                "question": question,
                "used_knowledge_base": use_knowledge_base and len(kb_results) > 0,
                "model": response.model_name,
                "tokens_used": response.usage.get("total_tokens", 0) if response.usage else 0,
            }

            if kb_results:
                result["knowledge_sources"] = [
                    {"chunk_id": r.chunk_id, "score": r.score, "metadata": r.metadata} for r in kb_results
                ]

            return result
        except Exception as e:
            self.context.end_step()
            return {
                "success": False,
                "error": f"Question answering failed: {str(e)}"
            }

    @tool(name="batch_summarize", description="Summarize multiple texts in batch")
    @parameter("texts", type="array", required=True, description="Array of texts to summarize")
    @parameter("length", type="string", required=False, default="short", description="Summary length for all texts")
    @validator("length", allowed_values=["short", "medium", "long"])
    @permission_required("llm_access", "storage")
    def batch_summarize(self, texts: list, length: str = "short") -> dict:
        """
        Summarize multiple texts in batch

        Args:
            texts: List of texts to summarize
            length: Summary length

        Returns:
            dict with summaries for each text
        """
        self.context.start_step("batch_summarization")
        self.context.info(f"Batch summarizing {len(texts)} texts")
        self.context.watch_variable("batch_size", len(texts))

        if not isinstance(texts, list):
            return {"success": False, "error": "texts must be an array"}

        if len(texts) == 0:
            return {"success": False, "error": "texts array cannot be empty"}

        if len(texts) > 20:
            return {"success": False, "error": "Maximum 20 texts per batch"}

        summaries = []
        total_tokens = 0

        for idx, text in enumerate(texts):
            # Validate individual text
            if text is None:
                summaries.append({"index": idx, "error": "Text cannot be None"})
                continue

            text_str = str(text) if text is not None else ""
            if len(text_str) < 10:
                summaries.append({"index": idx, "error": "Text too short (minimum 10 characters)"})
                continue

            self.context.trace("processing_text", {"index": idx, "length": len(text_str)})

            # Use the summarize method with error handling
            try:
                result = self.summarize(text=text_str, length=length, style="informative")

                if result.get("success"):
                    summaries.append(
                        {
                            "index": idx,
                            "summary": result["summary"],
                            "from_cache": result.get("from_cache", False),
                        }
                    )
                    total_tokens += result.get("tokens_used", 0)
                else:
                    summaries.append({"index": idx, "error": result.get("error", "Unknown error")})
            except Exception as e:
                summaries.append({"index": idx, "error": f"Summarization failed: {str(e)}"})

        self.context.end_step()

        return {
            "success": True,
            "summaries": summaries,
            "total_processed": len(texts),
            "total_tokens": total_tokens,
            "length": length,
        }


# Export plugin instance
plugin = LLMSummarizerPlugin()
