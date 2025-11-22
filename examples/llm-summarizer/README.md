# LLM Summarizer Plugin

An advanced text analysis plugin demonstrating LLM integration, knowledge base access, and intelligent caching in the Nadoo Plugin SDK.

## Features

This plugin demonstrates:

- **LLM Integration** - Using Internal API to invoke language models
- **Permission Management** - Requiring specific permissions (`llm_access`, `storage`, `knowledge_access`)
- **Caching Strategy** - Intelligent caching with TTL for performance
- **Knowledge Base Integration** - Augmenting LLM responses with KB search
- **Batch Processing** - Efficient processing of multiple items
- **Debug Instrumentation** - Comprehensive step tracking and variable watching
- **Error Handling** - Robust validation and error messages

## Tools

### 1. summarize

Generate concise summaries with customizable length and style.

**Parameters:**
- `text` (string, required): Text to summarize (10-50,000 characters)
- `length` (string, optional): Summary length - "short", "medium", or "long" (default: "medium")
- `style` (string, optional): Summary style - "informative", "technical", or "casual" (default: "informative")

**Features:**
- Automatic caching (1 hour TTL)
- Multiple length options with specific constraints
- Style-based prompt engineering
- Token usage tracking

**Example:**
```json
{
  "text": "Long article text here...",
  "length": "short",
  "style": "technical"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Concise technical summary...",
  "from_cache": false,
  "length": "short",
  "style": "technical",
  "model": "gpt-4",
  "tokens_used": 150
}
```

### 2. extract_keywords

Extract key terms and concepts from text.

**Parameters:**
- `text` (string, required): Text to analyze (10-50,000 characters)
- `max_keywords` (number, optional): Maximum keywords to extract (1-50, default: 10)

**Example:**
```json
{
  "text": "Article about artificial intelligence and machine learning...",
  "max_keywords": 5
}
```

**Response:**
```json
{
  "success": true,
  "keywords": [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural networks",
    "data science"
  ],
  "count": 5,
  "model": "gpt-4",
  "tokens_used": 80
}
```

### 3. answer_question

Answer questions based on provided context with optional knowledge base integration.

**Parameters:**
- `context` (string, required): Context text containing information (10-50,000 characters)
- `question` (string, required): Question to answer (3-500 characters)
- `use_knowledge_base` (boolean, optional): Search knowledge base for additional context (default: false)
- `knowledge_base_uuid` (string, optional): Knowledge base UUID (required if use_knowledge_base=true)

**Features:**
- Context-based Q&A
- Optional knowledge base augmentation
- Source tracking for KB results
- Confidence indication

**Example:**
```json
{
  "context": "France is a country in Europe. Its capital is Paris...",
  "question": "What is the capital of France?",
  "use_knowledge_base": true,
  "knowledge_base_uuid": "kb-uuid-123"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The capital of France is Paris.",
  "question": "What is the capital of France?",
  "used_knowledge_base": true,
  "model": "gpt-4",
  "tokens_used": 120,
  "knowledge_sources": [
    {
      "chunk_id": "chunk-1",
      "score": 0.92,
      "metadata": {"source": "geography.pdf"}
    }
  ]
}
```

### 4. batch_summarize

Efficiently summarize multiple texts in a single operation.

**Parameters:**
- `texts` (array, required): Array of texts to summarize (max 20 items)
- `length` (string, optional): Summary length for all texts (default: "short")

**Features:**
- Parallel processing
- Individual error handling per text
- Cache utilization for duplicates
- Aggregate token tracking

**Example:**
```json
{
  "texts": [
    "First article text...",
    "Second article text...",
    "Third article text..."
  ],
  "length": "short"
}
```

**Response:**
```json
{
  "success": true,
  "summaries": [
    {
      "index": 0,
      "summary": "Summary of first article...",
      "from_cache": false
    },
    {
      "index": 1,
      "summary": "Summary of second article...",
      "from_cache": true
    },
    {
      "index": 2,
      "summary": "Summary of third article...",
      "from_cache": false
    }
  ],
  "total_processed": 3,
  "total_tokens": 450,
  "length": "short"
}
```

## Installation

1. Install the Nadoo CLI:
```bash
pip install nadoo-cli
```

2. Install the plugin:
```bash
nadoo plugin install llm-summarizer
```

3. Enable the plugin in your workspace:
```bash
nadoo plugin enable llm-summarizer
```

## Development

### Running Tests

```bash
cd examples/llm-summarizer
python -m pytest test_llm_summarizer.py -v
```

Or using unittest:

```bash
python test_llm_summarizer.py
```

### Code Structure

```
llm-summarizer/
├── main.py                    # Plugin implementation
├── manifest.yaml              # Plugin metadata and configuration
├── test_llm_summarizer.py    # Comprehensive unit tests
└── README.md                  # This file
```

### Key Implementation Patterns

#### LLM Invocation

```python
@permission_required("llm_access")
def my_tool(self, text: str) -> dict:
    messages = [
        {"role": "system", "content": "System prompt..."},
        {"role": "user", "content": f"User prompt: {text}"}
    ]

    response = self.api.llm.invoke(
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return {"result": response.content}
```

#### Caching Pattern

```python
# Check cache
cache_key = f"operation:{hash(input_data)}"
cached = self.api.storage.get(cache_key)
if cached:
    return cached

# Perform operation
result = expensive_operation(input_data)

# Cache result with TTL (1 hour)
self.api.storage.set(cache_key, result, ttl=3600)
```

#### Knowledge Base Integration

```python
@permission_required("llm_access", "knowledge_access")
def search_and_answer(self, query: str, kb_uuid: str) -> dict:
    # Search knowledge base
    results = self.api.knowledge.search(
        knowledge_base_uuid=kb_uuid,
        query=query,
        top_k=3,
        score_threshold=0.7
    )

    # Use results in LLM context
    context = "\n\n".join([r.content for r in results])
    # ... invoke LLM with context
```

#### Step Tracking

```python
def my_operation(self):
    self.context.start_step("operation_name")

    try:
        # Perform operation
        result = do_work()

        # Watch variables for debugging
        self.context.watch_variable("result_size", len(result))

        # Trace important events
        self.context.trace("operation_completed", {"status": "success"})

    finally:
        self.context.end_step("operation_name")
```

## Configuration

The plugin supports the following configuration options:

```yaml
default_summary_length: medium    # short, medium, or long
default_summary_style: informative  # informative, technical, or casual
cache_enabled: true
cache_ttl: 3600                   # seconds (1 hour)
max_batch_size: 20                # maximum texts per batch
```

## Testing

The plugin includes comprehensive tests demonstrating:

- **Mock LLM responses** - Simulating different LLM outputs
- **Mock knowledge base** - Testing KB integration without backend
- **Mock storage** - Testing caching behavior
- **Parameter validation** - Testing all validators
- **Error handling** - Testing edge cases and errors
- **Debug instrumentation** - Verifying steps, traces, and variables

Example test pattern:

```python
def test_summarize(self):
    # Mock LLM response
    self.mock_llm_response("This is a summary.")

    # Execute tool
    result = self.execute_tool("summarize", {
        "text": "Long text...",
        "length": "short"
    })

    # Assertions
    self.assertSuccess(result)
    self.assertEqual(result["summary"], "This is a summary.")

    # Verify LLM was called correctly
    self.assertLLMCalled(temperature=0.7, max_tokens=500)

    # Verify caching
    self.assertStorageSet("summary:...")
```

## Use Cases

1. **Content Summarization** - Summarize articles, documents, reports
2. **Document Analysis** - Extract key concepts and themes
3. **Knowledge Extraction** - Answer questions from documentation
4. **Batch Processing** - Process multiple documents efficiently
5. **Research Assistant** - Combine summaries with knowledge base search

## Performance Considerations

- **Caching**: Summaries are cached for 1 hour to reduce LLM costs
- **Batch Operations**: Use `batch_summarize` for multiple texts to optimize API calls
- **Token Tracking**: Monitor `tokens_used` to manage costs
- **Knowledge Base**: Use KB search sparingly as it adds latency

## Next Steps

After understanding this example:

1. Explore the [Internal API documentation](../../docs/internal-api.md)
2. Learn about [Permission Management](../../docs/permissions.md)
3. Read about [Testing Strategies](../../docs/testing.md)
4. Create your own LLM-powered plugin

## License

MIT License - see main SDK documentation for details.
