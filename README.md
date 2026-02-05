# RAG Backend API

A FastAPI-based backend service for PDF document processing and intelligent Q&A using Retrieval Augmented Generation (RAG) with LangChain and FAISS vector store.

## 📋 Overview

This project provides a REST API that allows users to upload PDF documents, process them into a vector database, and interact with the content through an AI-powered chat interface. The system uses vector similarity search to retrieve relevant document chunks and generates contextual responses using Large Language Models.

## ✨ Features

- **PDF Upload & Processing**: Upload multiple PDF documents in batches
- **Vector Store Integration**: Automatic document embedding and FAISS indexing
- **Intelligent Chat**: AI-powered question answering based on uploaded documents
- **Database Integration**: PostgreSQL database for user and chat management
- **CORS Enabled**: Ready for frontend integration
- **Batch Management**: Organized file storage with timestamp-based batch directories
- **Health Check Endpoint**: Monitor service status

## 🏗️ Project Structure

```
rag_backend/
├── db/                      # Database configuration and models
│   ├── config.py           # Database session management
│   ├── database.py         # SQLAlchemy engine and connection
│   └── data_models.py      # User and Chat table models
├── llm/                     # Language model integration
│   └── chatmodel.py        # Chat response generation logic
├── models/                  # Pydantic models
│   └── pymodel.py          # Request/Response schemas
├── retriver/                # Document retrieval system
│   └── fas.py              # FAISS vector store operations
├── uploads/                 # PDF storage directory (timestamped batches)
├── main.py                  # FastAPI application and endpoints
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── .env                     # Environment variables
```

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag_backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv myenv
   # Windows
   myenv\Scripts\activate
   # Linux/Mac
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   - Create a PostgreSQL database named `rag_database`
   - Update connection string in `db/database.py` if needed:
     ```python
     DATABASE_URI = "postgresql://postgres:password@localhost:5432/rag_database"
     ```

5. **Set up environment variables**
   - Create `.env` file with necessary API keys (Google Generative AI, etc.)

### Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📡 API Endpoints

### 1. Root Endpoint
```http
GET /
```
Returns API status message.

### 2. Upload PDFs
```http
POST /upload-pdfs
```
**Description**: Upload one or multiple PDF files for processing.

**Request**: 
- Content-Type: `multipart/form-data`
- Body: `files` (List of PDF files)

**Response**:
```json
{
  "message": "Successfully uploaded 2 file(s)",
  "files": [
    {
      "filename": "document.pdf",
      "size": 124567,
      "path": "uploads/20260205_143022/document.pdf",
      "batch": "20260205_143022"
    }
  ],
  "chat_id": "20260205_143022",
  "errors": null
}
```

### 3. Chat with Documents
```http
POST /chat
```
**Description**: Ask questions about uploaded documents.

**Request Body**:
```json
{
  "chat_id": "20260205_143022",
  "query": "What is the main topic of the document?"
}
```

**Response**:
```json
{
  "response": "Based on the uploaded documents..."
}
```

### 4. Health Check
```http
GET /health
```
Returns service health status.

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **LLM Integration**: LangChain with Google Generative AI
- **Document Processing**: PyPDF, LangChain Text Splitters
- **Async Support**: asyncpg
- **CORS**: Enabled for frontend integration

## 📦 Key Dependencies

- `fastapi` - Modern web framework for building APIs
- `langchain-google-genai` - Google AI integration
- `langchain-community` - Community integrations for LangChain
- `faiss-cpu` - Vector similarity search
- `pypdf` - PDF document parsing
- `sqlalchemy` - SQL toolkit and ORM
- `asyncpg` - Async PostgreSQL driver
- `pydantic` - Data validation
- `uvicorn` - ASGI server

## 🗄️ Database Schema

### Users Table
- `user_id` (Integer, Primary Key)
- `user_name` (String)
- `Password` (String)

### Chat Table
- `chat_id` (Integer, Primary Key)
- `chat_name` (String)

## 🔄 Workflow

1. **Upload**: User uploads PDF files via `/upload-pdfs` endpoint
2. **Processing**: PDFs are saved in timestamped batch directories
3. **Indexing**: Documents are processed and embedded into FAISS vector store
4. **Query**: User sends questions via `/chat` endpoint
5. **Retrieval**: Relevant document chunks are retrieved from vector store
6. **Generation**: LLM generates contextual response based on retrieved content
7. **Response**: Answer is returned to user

## 🔒 Security Notes

- CORS is currently set to allow all origins (`*`) - restrict this in production
- Database credentials should be stored in environment variables
- Implement authentication and authorization for production use

## 🐳 Docker Support

A Dockerfile is included for containerized deployment.

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please ensure code quality and add appropriate tests.

---

**Note**: This is a development setup. For production deployment, ensure proper security configurations, environment variable management, and error handling.