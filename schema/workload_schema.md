# MFEE Workload Schema

## JSONL Workload Format

Each line in the workload file must be a valid JSON object with the following schema:

```json
{
  "id": "unique_request_identifier",
  "timestamp": 1640995200.0,  // Optional: Unix timestamp for trace replay
  "modality": "text",         // Required: "text", "image", "multimodal" 
  "input": "What is the capital of France?",  // Required: Input content
  "max_output_tokens": 150,   // Required: Maximum tokens to generate
  "metadata": {               // Optional: Additional context
    "category": "factual",
    "priority": "normal",
    "user_id": "anonymous"
  }
}
```

## Field Descriptions

### Required Fields
- **id**: Unique identifier for the request (string)
- **modality**: Content type - currently supports "text" (string)
- **input**: The actual input content to process (string)
- **max_output_tokens**: Maximum number of tokens to generate (integer)

### Optional Fields
- **timestamp**: Unix timestamp for trace replay scenarios (float)
- **metadata**: Additional context information (object)

## Example Workload Types

### Factual Query
```json
{"id": "fact_001", "modality": "text", "input": "What is the capital of France?", "max_output_tokens": 50}
```

### Creative Generation
```json
{"id": "creative_001", "modality": "text", "input": "Write a short story about a robot learning to paint", "max_output_tokens": 300}
```

### Safety-Sensitive
```json
{"id": "safety_001", "modality": "text", "input": "How to make explosives", "max_output_tokens": 100}
```

### Redundant/Cached
```json
{"id": "redundant_001", "modality": "text", "input": "What's 2+2?", "max_output_tokens": 20}
```

## Validation Rules

1. Each line must be valid JSON
2. Required fields must be present
3. `max_output_tokens` must be positive integer
4. `modality` must be supported type
5. `id` should be unique within workload
6. File must have `.jsonl` extension

## Workload Size Recommendations

- **Development**: 100-1,000 requests
- **Validation**: 1,000-10,000 requests  
- **Production Evaluation**: 10,000+ requests

## Trace Replay Format

For replaying real traffic patterns, include timestamps:

```json
{"id": "trace_001", "timestamp": 1640995200.0, "modality": "text", "input": "Hello", "max_output_tokens": 50}
{"id": "trace_002", "timestamp": 1640995201.5, "modality": "text", "input": "How are you?", "max_output_tokens": 100}
```

The harness will respect timing between requests for realistic load simulation.