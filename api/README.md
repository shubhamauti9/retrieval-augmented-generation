# RAG Pipeline API

Enterprise RAG system for document ingestion and intelligent querying.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api.main:app --reload

# Open API docs
# http://localhost:8000/docs
```

## API Endpoints

### Document Ingestion

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/upload` | Upload a single document |
| POST | `/ingest/batch` | Upload multiple documents |
| DELETE | `/ingest/source/{name}` | Delete by source |
| GET | `/ingest/stats` | Ingestion statistics |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | Query the knowledge base |
| POST | `/query/retrieve` | Get documents without LLM |
| POST | `/query/stream` | Streaming response |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/health` | Health check |
| GET | `/admin/collections` | List collections |
| DELETE | `/admin/collections/{name}` | Delete collection |
| GET | `/admin/stats` | System statistics |

## Supported File Formats

- PDF (`.pdf`)
- Word (`.docx`)
- Excel (`.xlsx`)
- PowerPoint (`.pptx`)
- Text (`.txt`, `.md`)

## Collections

Organize documents by type:
- `sebi_circulars` - SEBI regulatory documents
- `hr_policies` - Company HR policies
- `default` - General documents

## Example Usage

### Upload a Document

```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -F "file=@leave_policy.pdf" \
  -F "collection=hr_policies"
```

### Query the Knowledge Base

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the leave policy?",
    "collection": "hr_policies",
    "top_k": 5
  }'
```

### Response

```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "content": "...",
      "source": "leave_policy.pdf",
      "score": 0.92
    }
  ]
}
```
