"""
Unit tests for LLM Summarizer Plugin
"""

import unittest
from nadoo_plugin.testing import PluginTestCase
from nadoo_plugin.exceptions import PluginExecutionError
from main import LLMSummarizerPlugin


class TestLLMSummarizerPlugin(PluginTestCase):
    """Test cases for LLMSummarizerPlugin"""

    plugin_class = LLMSummarizerPlugin

    def test_summarize_basic(self):
        """Test basic text summarization"""
        # Mock LLM response
        self.mock_llm_response("This is a concise summary of the text.")

        # Execute
        result = self.execute_tool(
            "summarize",
            {
                "text": "This is a long text that needs to be summarized. " * 10,
                "length": "short",
                "style": "informative",
            },
        )

        # Assertions
        self.assertSuccess(result)
        self.assertHasKey(result, "summary")
        self.assertEqual(result["summary"], "This is a concise summary of the text.")
        self.assertEqual(result["length"], "short")
        self.assertEqual(result["style"], "informative")
        self.assertFalse(result["from_cache"])

        # Verify LLM was called
        self.assertLLMCalled(temperature=0.7, max_tokens=500)

        # Verify storage was used for caching
        self.assertStorageSet("summary:{}:short:informative".format(hash("This is a long text that needs to be summarized. " * 10)))

    def test_summarize_cached(self):
        """Test that cached summaries are returned"""
        text = "Some text to summarize"
        cache_key = f"summary:{hash(text)}:medium:informative"

        # Pre-populate cache
        self.set_storage(cache_key, {"summary": "Cached summary"})

        # Execute (should not call LLM)
        result = self.execute_tool("summarize", {"text": text})

        # Assertions
        self.assertSuccess(result)
        self.assertEqual(result["summary"], "Cached summary")
        self.assertTrue(result["from_cache"])

        # Verify LLM was NOT called
        self.assertLLMNotCalled()

    def test_summarize_different_lengths(self):
        """Test summarization with different lengths"""
        text = "Test text" * 50

        for length in ["short", "medium", "long"]:
            with self.subTest(length=length):
                self.mock_llm_response(f"Summary in {length} format")

                result = self.execute_tool("summarize", {"text": text, "length": length})

                self.assertSuccess(result)
                self.assertEqual(result["length"], length)

    def test_summarize_different_styles(self):
        """Test summarization with different styles"""
        text = "Test text" * 50

        for style in ["informative", "technical", "casual"]:
            with self.subTest(style=style):
                self.mock_llm_response(f"Summary in {style} style")

                result = self.execute_tool("summarize", {"text": text, "style": style})

                self.assertSuccess(result)
                self.assertEqual(result["style"], style)

    def test_summarize_invalid_length(self):
        """Test summarization with invalid length"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("summarize", {"text": "Test text" * 50, "length": "invalid"})

        self.assertIn("must be one of", str(context.exception))

    def test_summarize_invalid_style(self):
        """Test summarization with invalid style"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("summarize", {"text": "Test text" * 50, "style": "invalid"})

        self.assertIn("must be one of", str(context.exception))

    def test_summarize_text_too_short(self):
        """Test summarization with text that's too short"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("summarize", {"text": "short"})

        self.assertIn("must have length >=", str(context.exception))

    def test_summarize_text_too_long(self):
        """Test summarization with text that's too long"""
        long_text = "a" * 50001  # Exceeds max_length=50000

        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("summarize", {"text": long_text})

        self.assertIn("must have length <=", str(context.exception))

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction"""
        # Mock LLM response
        self.mock_llm_response("artificial intelligence, machine learning, deep learning, neural networks, data science")

        # Execute
        result = self.execute_tool(
            "extract_keywords",
            {"text": "Article about AI and machine learning technologies.", "max_keywords": 10},
        )

        # Assertions
        self.assertSuccess(result)
        self.assertHasKey(result, "keywords")
        self.assertEqual(len(result["keywords"]), 5)
        self.assertIn("artificial intelligence", result["keywords"])
        self.assertEqual(result["count"], 5)

        # Verify LLM was called with correct parameters
        self.assertLLMCalled(temperature=0.3, max_tokens=200)

    def test_extract_keywords_limited(self):
        """Test keyword extraction with limit"""
        # Mock LLM response with many keywords
        self.mock_llm_response("kw1, kw2, kw3, kw4, kw5, kw6, kw7, kw8, kw9, kw10, kw11, kw12")

        result = self.execute_tool("extract_keywords", {"text": "Test text" * 50, "max_keywords": 5})

        # Should only return 5 keywords despite more being provided
        self.assertSuccess(result)
        self.assertEqual(len(result["keywords"]), 5)
        self.assertEqual(result["count"], 5)

    def test_extract_keywords_invalid_max(self):
        """Test keyword extraction with invalid max_keywords"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("extract_keywords", {"text": "Test text" * 50, "max_keywords": 100})

        self.assertIn("must be <=", str(context.exception))

    def test_answer_question_basic(self):
        """Test basic question answering"""
        # Mock LLM response
        self.mock_llm_response("The capital of France is Paris.")

        # Execute
        result = self.execute_tool(
            "answer_question",
            {
                "context": "France is a country in Europe. Its capital is Paris.",
                "question": "What is the capital of France?",
            },
        )

        # Assertions
        self.assertSuccess(result)
        self.assertHasKey(result, "answer")
        self.assertEqual(result["answer"], "The capital of France is Paris.")
        self.assertEqual(result["question"], "What is the capital of France?")
        self.assertFalse(result["used_knowledge_base"])

        # Verify LLM was called
        self.assertLLMCalled(temperature=0.5, max_tokens=500)

    def test_answer_question_with_kb(self):
        """Test question answering with knowledge base"""
        # Mock knowledge base results
        self.mock_knowledge_results(
            [
                {"chunk_id": "chunk1", "content": "Additional context from KB", "score": 0.9, "metadata": {}},
                {"chunk_id": "chunk2", "content": "More information", "score": 0.8, "metadata": {}},
            ]
        )

        # Mock LLM response
        self.mock_llm_response("Answer based on context and KB.")

        # Execute
        result = self.execute_tool(
            "answer_question",
            {
                "context": "Some context",
                "question": "What is this about?",
                "use_knowledge_base": True,
                "knowledge_base_uuid": "kb-uuid-123",
            },
        )

        # Assertions
        self.assertSuccess(result)
        self.assertTrue(result["used_knowledge_base"])
        self.assertHasKey(result, "knowledge_sources")
        self.assertEqual(len(result["knowledge_sources"]), 2)

    def test_answer_question_kb_missing_uuid(self):
        """Test question answering with KB enabled but no UUID"""
        result = self.execute_tool(
            "answer_question",
            {"context": "Some context", "question": "What?", "use_knowledge_base": True},
        )

        # Should return error
        self.assertError(result, "knowledge_base_uuid is required")

    def test_batch_summarize_basic(self):
        """Test batch summarization"""
        # Mock LLM responses for each text
        self.mock_llm_response("Summary 1")
        self.mock_llm_response("Summary 2")
        self.mock_llm_response("Summary 3")

        # Execute
        result = self.execute_tool(
            "batch_summarize", {"texts": ["Text one" * 10, "Text two" * 10, "Text three" * 10], "length": "short"}
        )

        # Assertions
        self.assertSuccess(result)
        self.assertHasKey(result, "summaries")
        self.assertEqual(result["total_processed"], 3)
        self.assertEqual(len(result["summaries"]), 3)

        # Check individual summaries
        for idx, summary_item in enumerate(result["summaries"]):
            self.assertEqual(summary_item["index"], idx)
            self.assertIn("summary", summary_item)

    def test_batch_summarize_empty_array(self):
        """Test batch summarization with empty array"""
        result = self.execute_tool("batch_summarize", {"texts": []})

        self.assertError(result, "cannot be empty")

    def test_batch_summarize_not_array(self):
        """Test batch summarization with non-array input"""
        result = self.execute_tool("batch_summarize", {"texts": "not an array"})

        self.assertError(result, "must be an array")

    def test_batch_summarize_too_many(self):
        """Test batch summarization with too many texts"""
        texts = ["Text" * 10] * 25  # More than max of 20

        result = self.execute_tool("batch_summarize", {"texts": texts})

        self.assertError(result, "Maximum 20 texts")

    def test_debug_information_collection(self):
        """Test that debug information is properly collected"""
        # Mock LLM response
        self.mock_llm_response("Test summary")

        # Execute a tool
        self.execute_tool("summarize", {"text": "Test text that will be summarized."})

        # Get debug data
        debug_data = self.get_debug_data()

        # Verify steps were tracked
        steps = debug_data["steps"]
        self.assertGreater(len(steps), 0)

        step_names = [step["step_name"] for step in steps]
        self.assertIn("summarization", step_names)

        # Verify variables were watched
        variables = debug_data["variables"]
        self.assertIn("text_length", variables)

        # Verify trace events
        trace = debug_data["trace"]
        self.assertGreater(len(trace), 0)

        trace_events = [t["event"] for t in trace]
        self.assertIn("llm_invocation_prepared", trace_events)
        self.assertIn("summary_cached", trace_events)

        # Verify API calls were recorded
        api_calls = debug_data["api_calls"]
        self.assertGreater(len(api_calls), 0)

        # Should have LLM and storage API calls
        api_types = [call["api_type"] for call in api_calls]
        self.assertIn("llm", api_types)
        self.assertIn("storage", api_types)

    def test_step_timing(self):
        """Test that step timing is measured"""
        # Mock LLM response
        self.mock_llm_response("Summary")

        # Execute
        self.execute_tool("summarize", {"text": "Test text" * 50})

        # Check step completion
        self.assertStepCompleted("summarization")

        # Get debug data and verify duration
        debug_data = self.get_debug_data()
        steps = debug_data["steps"]

        summarization_step = next(s for s in steps if s["step_name"] == "summarization")
        self.assertIsNotNone(summarization_step["duration"])
        self.assertGreater(summarization_step["duration"], 0)


if __name__ == "__main__":
    unittest.main()
