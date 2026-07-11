# RAG Backend API

A production-ready FastAPI backend service for PDF document processing and intelligent Q&A using Retrieval Augmented Generation (RAG) with the **OpenAI Agents SDK** and **pgvector** for vector similarity search.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#-configuration)
  - [Running the Application](#running-the-application)
- [API Endpoints](#-api-endpoints)
- [Technology Stack](#-technology-stack)
- [Database Schema](#-database-schema)
- [Workflow](#-workflow)
- [Authentication Flow](#-authentication-flow)
- [Security](#-security-features--notes)
- [Docker Support](#-docker-support)
- [Usage Examples](#-usage-example)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-frequently-asked-questions-faq)
- [Contributing](#-contributing)
- [License](#-license)

## 📋 Overview

This project provides a comprehensive REST API that enables users to upload PDF documents, process them into **PostgreSQL with pgvector**, and interact with the content through an AI-powered chat interface powered by OpenAI's `gpt-4o-mini` via the **OpenAI Agents SDK**. The system uses a single, unified vector store backed entirely by PostgreSQL — no separate FAISS files on disk.

The API features a complete authentication system with JWT token-based security, bcrypt password hashing, user authorization for chat access, and persistent conversation history storage in PostgreSQL. LLM responses include structured output with answer, key points, confidence level, source citations, and follow-up suggestions. Both uploaded document chunks **and** Q&A history pairs are stored as vector embeddings in the `document_chunk` table, enabling semantic retrieval across all previous interactions.

### Recent Changes
- **pgvector migration** *(latest)*: Replaced FAISS on-disk vector stores with PostgreSQL + pgvector. The `document_chunk` table stores embeddings (768-dim) for both PDF chunks and Q&A history. No FAISS files are written to disk.
- **OpenAI Agents SDK**: The LLM core uses the OpenAI Agents SDK (`openai-agents`). The agent dynamically calls `search_knowledge_base`, `search_chat_history`, `generate_citation`, and `WebSearchTool`.
- **Embedded Q&A history**: After every `/chat` response, the user question and the Q&A pair are each embedded and saved as `DocumentChunk` rows, making past answers retrievable by future queries.
- **Structured AI message storage**: Assistant messages in the `Message` table now persist `key_points`, `sources_cited`, and `follow_up_suggestions` as JSON columns, fully exposed via `/getchatconversation`.
- **PDF management routes**: Added `GET /pdf` to list PDFs in a chat and `GET /pdf/download` to stream a specific PDF back to the client.
- **Chat rename route**: Added `PATCH /renamechat` to rename a chat session.
- **Source citations**: Every `/chat` response includes a `sources` array where each entry contains `filename` and 1-indexed `page` derived from the top-4 nearest `DocumentChunk` rows (deduplicated by `(filename, page)`).

## 🚀 Quick Start

```bash
# 1. Clone and navigate to project
git clone <your-repo-url>
cd rag_backend

# 2. Create virtual environment
python -m venv myenv
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL with pgvector extension
# psql -U postgres -c "CREATE DATABASE rag_database;"
# psql -U postgres -d rag_database -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Configure environment variables (.env file)
# JWT_SECRET=your-secret-key
# OPENAI_API_KEY=sk-proj-...
# DATABASE_URI=postgresql://postgres:password@localhost:5432/rag_database
# Optional: CLIENT_ID, CLIENT_SECRET, FRONTEND_URL (GitHub OAuth)

# 6. Run the application
uvicorn main:app --reload

# 7. Visit http://127.0.0.1:8000/docs for interactive API documentation
```

## ✨ Features

### Core Functionality
✅ **Complete Authentication System**
- **Traditional Auth**: User signup and login with email/password
- **OAuth 2.0**: GitHub OAuth integration for social login
- JWT token-based authentication (24-hour expiration)
- Bcrypt password hashing with salt for traditional auth
- Protected route middleware
- User-specific data isolation
- Automatic user creation/login from GitHub profile
- Email retrieval from public or private GitHub accounts

✅ **Document Processing**
- Multi-file PDF upload support
- Automatic text extraction from PDFs using `PyPDFDirectoryLoader`
- Intelligent document chunking with `RecursiveCharacterTextSplitter`
- Batch organization with timestamps
- Persistent file storage in `uploads/<timestamp>/`

✅ **RAG (Retrieval Augmented Generation)**
- OpenAI `gpt-4o-mini` model via **OpenAI Agents SDK**
- Intelligent agent tools:
  - `search_knowledge_base` — cosine similarity search over pgvector `document_chunk` table
  - `search_chat_history` — fetches the last 10 messages from the `Message` table
  - `generate_citation` — formats a proper citation for document content
  - `WebSearchTool` — built-in SDK web search for information outside uploaded docs
- **pgvector storage**: all embeddings (document chunks + Q&A history) stored in PostgreSQL `document_chunk` table; 768-dimensional vectors using `sentence-transformers/all-mpnet-base-v2`
- **Retriever top-K = 5** for `search_knowledge_base`; top-4 used for source citations
- **Source Citations**: every `/chat` response includes a `sources` list with `filename` and 1-indexed `page`, deduplicated by `(filename, page)` pair
- Structured output with Pydantic output type (`LLMResponseFormat`):
  - `answer` — main response text
  - `key_points` — extracted key bullet points
  - `confidence_level` — `"high"`, `"medium"`, or `"low"`
  - `sources_cited` — LLM-generated source references
  - `needs_clarification` / `clarification_needed` — clarification flags
  - `follow_up_suggestions` — suggested follow-up questions
- Per-chat isolated retrieval scoped by `chat_id`

✅ **Chat Management**
- Multiple chat sessions per user
- Create new chats automatically on PDF upload
- Rename chat sessions via `/renamechat`
- Delete chats with automatic cleanup (files + all database records including embeddings)
- Full conversation history stored in PostgreSQL `Message` table
- Structured assistant messages: `key_points`, `sources_cited`, `follow_up_suggestions` persisted as JSON
- Retrieve past conversations with full structured data via `/getchatconversation`
- Chat ownership verification for security

✅ **PDF File Management**
- List all PDFs belonging to a chat (`GET /pdf`)
- Stream / download individual PDF files (`GET /pdf/download`)
- Path-traversal-safe filename handling

✅ **API Features**
- RESTful API design with FastAPI
- Interactive Swagger documentation (`/docs`)
- Alternative ReDoc documentation (`/redoc`)
- CORS enabled for frontend integration
- Comprehensive error handling and transaction rollback
- Health check endpoint

✅ **Data Management**
- PostgreSQL database with SQLAlchemy ORM
- Relational data model: `Users`, `Chat`, `Message`, `DocumentChunk`
- `DocumentChunk` stores both PDF content embeddings and Q&A history embeddings
- Database transaction safety with automatic rollback on errors

### Technical Features
- 🚀 **High Performance**: FastAPI framework with async support
- 🔒 **Security**: JWT + Bcrypt authentication
- 📦 **Modular Architecture**: Organized routers and utilities
- 🐳 **Docker Ready**: Containerization support
- 🔧 **Type Safety**: Pydantic models for validation
- 📊 **Scalable**: pgvector enables production-grade vector search within PostgreSQL

## 🏗️ Project Structure

```
rag_backend/
├── agent/                   # OpenAI Agents SDK agent definition
│   ├── __init__.py
│   └── rag_agent.py        # RAGContext dataclass, function tools, agent instantiation
├── db/                      # Database configuration and models
│   ├── config.py           # Database session dependency (init_db)
│   ├── database.py         # SQLAlchemy engine and connection
│   └── data_models.py      # Users, Chat, Message, DocumentChunk table models
├── llm/                     # LLM response layer
│   └── chatmodel.py        # get_response() — runs the agent and builds source citations
├── models/                  # Pydantic schemas
│   └── pymodel.py          # Request/Response schemas and LLMResponseFormat
├── retriver/                # Embedding and retrieval utilities
│   ├── embedding.py        # HuggingFace embeddings instance (sentence-transformers)
│   ├── fas.py              # Legacy FAISS helpers (unused by current routes)
│   ├── retriver.py         # similarityretriver() — pgvector cosine distance search
│   ├── text_spilter.py     # RecursiveCharacterTextSplitter instance
│   └── vector.py           # add_vector_to_db() — load PDFs and insert DocumentChunk rows
├── route/                   # API route handlers (modular routers)
│   ├── auth_route/
│   │   ├── auth_router.py       # POST /signup, POST /login
│   │   └── auth_github_route.py # GET /githublogin, GET /github/callback
│   ├── chat_route/
│   │   └── chat_router.py       # POST /chat, GET /getchat, GET /getchatconversation,
│   │                            # PATCH /renamechat, DELETE /deletechat,
│   │                            # GET /pdf, GET /pdf/download
│   └── upload_route/
│       └── upload_router.py     # POST /upload-pdfs
├── utils/                   # Utility functions
│   ├── hash.py             # Password hashing with bcrypt
│   ├── jwt.py              # JWT token generation and verification
│   └── protectroute.py     # get_current_user dependency
├── uploads/                 # PDF storage directory (timestamped batches)
│   └── YYYYMMDD_HHMMSS/    # Each batch directory contains uploaded PDF files
├── main.py                  # FastAPI app, CORS, and router registration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Compose file for app + PostgreSQL
└── .env                     # Environment variables (not committed)
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 12+** with the **pgvector** extension installed
- **OpenAI API Key** (required for the LLM agent)
- **GitHub OAuth App** (optional, for social login)
- **Virtual environment** (strongly recommended)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
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

4. **Set up PostgreSQL with pgvector**
   ```sql
   -- Create the database
   CREATE DATABASE rag_database;

   -- Enable pgvector (must be done once per database)
   \c rag_database
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

5. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   # JWT Configuration
   JWT_SECRET=your-super-secret-key-minimum-32-characters
   JWT_ALGORITHM=HS256

   # OpenAI (Required for the RAG agent)
   OPENAI_API_KEY=sk-proj-...your-key-here
   OPENAI_MODEL=gpt-4o-mini   # optional, defaults to gpt-4o-mini

   # PostgreSQL connection string
   DATABASE_URI=postgresql://postgres:password@localhost:5432/rag_database

   # GitHub OAuth (Optional)
   CLIENT_ID=your-github-oauth-client-id
   CLIENT_SECRET=your-github-oauth-client-secret
   REDIRECT_URI=http://localhost:8000/github/callback
   FRONTEND_URL=http://localhost:5173
   ```

   > **Important**:
   > - Generate a strong `JWT_SECRET` (minimum 32 characters) for production.
   > - Obtain `OPENAI_API_KEY` from [platform.openai.com](https://platform.openai.com/api-keys).
   > - For GitHub OAuth, create an OAuth App at [GitHub Developer Settings](https://github.com/settings/developers).
   > - Never commit `.env` to version control (already in `.gitignore`).

6. **Start the application** — SQLAlchemy will create all tables automatically on first run.

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | Yes | — | Secret key for JWT signing (min 32 chars) |
| `JWT_ALGORITHM` | No | `HS256` | JWT encoding algorithm |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for the agent |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model name used by the agent |
| `DATABASE_URI` | Yes | — | PostgreSQL connection string (must include pgvector DB) |
| `CLIENT_ID` | No | — | GitHub OAuth App Client ID |
| `CLIENT_SECRET` | No | — | GitHub OAuth App Client Secret |
| `REDIRECT_URI` | No | `http://localhost:8000/github/callback` | GitHub OAuth callback URL |
| `FRONTEND_URL` | No | `http://localhost:5173` | Frontend URL for post-OAuth redirect |

### Application Settings

Other tuneable settings in source files:

| Setting | Location | Default |
|---------|----------|---------|
| JWT expiration | `utils/jwt.py` | 24 hours |
| Upload directory | `route/upload_route/upload_router.py` | `uploads/` |
| CORS origins | `main.py` | `*` (all) |
| Embedding model | `retriver/embedding.py` | `sentence-transformers/all-mpnet-base-v2` (768-dim) |
| Chunk size / overlap | `retriver/text_spilter.py` | 500 / 300 |
| Retriever top-K (agent) | `agent/rag_agent.py` → `search_knowledge_base` | 5 |
| Source citation top-K | `llm/chatmodel.py` | 4 |

### Running the Application

**Development mode (with auto-reload):**
```bash
uvicorn main:app --reload
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API is available at:
- Local: `http://127.0.0.1:8000`
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Alternative Docs: `http://127.0.0.1:8000/redoc`

## 📡 API Endpoints

### Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API status check |
| GET | `/health` | No | Health check endpoint |
| POST | `/signup` | No | User registration |
| POST | `/login` | No | User authentication (returns JWT) |
| GET | `/githublogin` | No | Initiate GitHub OAuth flow |
| GET | `/github/callback` | No | GitHub OAuth callback handler |
| GET | `/getuserdata` | Yes | Get current user data from token |
| POST | `/upload-pdfs` | Yes | Upload PDF files and create a chat |
| POST | `/chat` | Yes | Ask questions about uploaded documents |
| GET | `/getchat` | Yes | List all user chat sessions |
| GET | `/getchatconversation` | Yes | Get full message history for a chat |
| PATCH | `/renamechat` | Yes | Rename a chat session |
| GET | `/pdf` | Yes | List PDF files in a chat |
| GET | `/pdf/download` | Yes | Stream/download a specific PDF |
| DELETE | `/deletechat` | Yes | Delete a chat and all associated data |

---

### Authentication Routes

#### 1. User Signup
```http
POST /signup
```
**Request Body:**
```json
{
  "user_name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```
**Response:**
```json
{
  "User": { "user_id": 1, "user_name": "John Doe", "email": "john@example.com" },
  "Successful": true,
  "message": "User created successfully"
}
```

#### 2. User Login
```http
POST /login
```
**Request Body:**
```json
{ "email": "john@example.com", "password": "securePassword123" }
```
**Response:**
```json
{
  "User": {
    "user_id": 1, "user_name": "John Doe",
    "email": "john@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "Successful": true,
  "message": "User logged in successfully"
}
```

#### 3. GitHub OAuth Login
```http
GET /githublogin
```
Redirects the browser to GitHub for authorization. Must be opened directly in a browser (cannot be tested from Swagger UI).

#### 4. GitHub OAuth Callback
```http
GET /github/callback?code={authorization_code}
```
Exchanges the GitHub code for a user JWT and redirects to:
```
{FRONTEND_URL}/auth/github/callback?token={jwt}&user_id={id}&user_name={name}&email={email}
```

#### 5. Get User Data
```http
GET /getuserdata
Authorization: Bearer <token>
```
**Response:**
```json
{ "user": { "user_id": 1, "user_name": "John Doe", "email": "john@example.com" } }
```

---

### Document Management Routes

#### 6. Upload PDFs
```http
POST /upload-pdfs
Authorization: Bearer <token>
Content-Type: multipart/form-data
```
**Body:** `files` — one or more PDF files.

**Behaviour:**
1. Saves PDFs to `uploads/<YYYYMMDD_HHMMSS>/`
2. Creates a `Chat` record (named after the first file)
3. Loads PDFs, splits into chunks, generates embeddings, inserts `DocumentChunk` rows into PostgreSQL

**Response:**
```json
{
  "message": "Successfully uploaded 2 file(s)",
  "files": [
    { "filename": "document.pdf", "size": 124567, "path": "uploads/20260210_223829/document.pdf", "batch": "20260210_223829" }
  ],
  "chat_id": 1,
  "chat_name": "document.pdf",
  "errors": null
}
```

#### 7. List PDFs in a Chat
```http
GET /pdf?chatid=1
Authorization: Bearer <token>
```
Returns metadata for every PDF file in the chat's upload directory.

**Response:**
```json
{
  "Successful": true,
  "files": [
    { "filename": "lecture1.pdf", "size_bytes": 204800, "download_url": "/pdf/download?chatid=1&filename=lecture1.pdf" }
  ]
}
```

#### 8. Download a PDF
```http
GET /pdf/download?chatid=1&filename=lecture1.pdf
Authorization: Bearer <token>
```
Streams the PDF file back to the client with `Content-Type: application/pdf`. Performs path-traversal sanitization (only the basename is used).

---

### Chat Routes

#### 9. Chat with Documents
```http
POST /chat
Authorization: Bearer <token>
```
**Request Body:**
```json
{
  "chat_id": 1,
  "question": "What is the main topic of the document?",
  "chat_history": [
    { "role": "user", "content": "Previous question" },
    { "role": "assistant", "content": "Previous answer" }
  ]
}
```

**Processing flow:**
1. Verifies chat ownership
2. Stores user message in `Message` table and embeds question as `DocumentChunk`
3. Runs the RAG agent (searches knowledge base, chat history, optionally web)
4. Stores structured assistant message in `Message` table
5. Embeds the Q&A pair as a new `DocumentChunk` for future retrieval
6. Queries top-4 nearest `DocumentChunk` rows for source citations

**Response:**
```json
{
  "success": true,
  "chat_id": 1,
  "response": "{\"answer\": \"Based on the uploaded documents...\", \"key_points\": [\"Point 1\"], \"confidence_level\": \"high\", \"sources_cited\": [\"document.pdf - page 2\"], \"needs_clarification\": false, \"follow_up_suggestions\": [\"Related question?\"]}",
  "role": "assistant",
  "timestamp": "2026-07-11T10:30:00",
  "sources_used": 2,
  "sources": [
    { "filename": "lecture1.pdf", "page": 3 },
    { "filename": "notes.pdf", "page": 12 }
  ],
  "error_message": null
}
```

> **Note on `response` field**: This is a JSON-encoded string containing the full `LLMResponseFormat` object. Parse it with `JSON.parse()` on the client side.
>
> **Note on `sources`**: These are pgvector-retrieved citations from the `document_chunk` table (top-4, deduplicated by `(filename, page)`). Pages are 1-indexed. This field is `null` on error.

**Error Response:**
```json
{
  "success": false,
  "chat_id": 1,
  "response": "",
  "role": "assistant",
  "timestamp": "2026-07-11T10:30:00",
  "sources_used": null,
  "sources": null,
  "error_message": "Chat not found or access denied"
}
```

#### 10. Get User Chats
```http
GET /getchat
Authorization: Bearer <token>
```
**Response:**
```json
{
  "chats": [
    { "chat_id": 1, "chat_name": "document.pdf" },
    { "chat_id": 2, "chat_name": "report.pdf" }
  ],
  "Successful": true
}
```

#### 11. Get Chat Conversation
```http
GET /getchatconversation?chatid=1
Authorization: Bearer <token>
```
Returns all messages in chronological order, including structured metadata for assistant messages.

**Response:**
```json
{
  "messages": [
    { "role": "user", "content": "What is the main topic?", "key_points": null, "sources_cited": null, "follow_up_suggestions": null },
    {
      "role": "assistant",
      "content": "The main topic is...",
      "key_points": ["Key point 1", "Key point 2"],
      "sources_cited": ["document.pdf - page 3"],
      "follow_up_suggestions": ["Could you explain more about X?"]
    }
  ],
  "Successful": true
}
```

#### 12. Rename a Chat
```http
PATCH /renamechat
Authorization: Bearer <token>
```
**Request Body:**
```json
{ "chat_id": 1, "chat_name": "New Chat Name" }
```
**Response:**
```json
{ "Successful": true, "message": "Chat renamed successfully", "chat_id": 1, "chat_name": "New Chat Name" }
```

#### 13. Delete Chat
```http
DELETE /deletechat?chatid=1
Authorization: Bearer <token>
```
Deletes the chat record, all associated `Message` rows, all associated `DocumentChunk` embeddings, and the PDF upload folder (safety check ensures only subfolders of `uploads/` are removed).

**Response:**
```json
{ "Successful": true, "message": "Chat deleted successfully" }
```

---

### System Routes

#### 14. Root
```http
GET /
```
```json
{ "message": "PDF Upload API is running" }
```

#### 15. Health Check
```http
GET /health
```
```json
{ "health": "okay" }
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** — modern, high-performance async web framework
- **Uvicorn** — ASGI server

### Authentication & Security
- **PyJWT** — JWT token encoding, decoding, and verification
- **Bcrypt** — password hashing with salt
- **Email Validator** — email format validation

### Database & Vector Store
- **PostgreSQL** — relational database and vector store (via pgvector)
- **pgvector** — PostgreSQL extension for vector similarity search (`<=>` cosine distance)
- **SQLAlchemy** — SQL toolkit and ORM
- **psycopg2-binary** — PostgreSQL adapter for Python

### RAG & AI Components
- **OpenAI Agents SDK** (`openai-agents`) — framework for tool-using AI agents
- **LangChain Community** — `PyPDFDirectoryLoader` for PDF loading
- **LangChain Text Splitters** — `RecursiveCharacterTextSplitter` for chunking
- **LangChain HuggingFace** — `HuggingFaceEmbeddings` wrapper
- **Sentence Transformers** — `all-mpnet-base-v2` embedding model (768-dim)

### Document Processing
- **PyPDF** — PDF parsing and text extraction

### Utilities
- **Pydantic** — data validation and structured output types
- **Python Multipart** — file upload handling
- **Python Dotenv** — environment variable management
- **HTTPX** — async HTTP client for GitHub OAuth

## 📦 Key Dependencies

```
fastapi
pydantic
python-dotenv
python-multipart
uvicorn
langchain-core
langchain-community
langchain-text-splitters
openai-agents
faiss-cpu          # retained for fas.py (legacy); not used by active routes
pypdf
sqlalchemy
psycopg2-binary
pyJWT
bcrypt
email-validator
langchain-huggingface
sentence-transformers
httpx
```

> **Note**: `faiss-cpu` is still listed because `retriver/fas.py` imports it. That module is not called by any active route and can be removed once legacy code is cleaned up.

## 🗄️ Database Schema

### Users
| Column | Type | Notes |
|--------|------|-------|
| `user_id` | Integer PK | auto-increment |
| `user_name` | String | display name |
| `email` | String | unique identifier |
| `password` | String (nullable) | bcrypt hash; `null` for OAuth users |

### Chat
| Column | Type | Notes |
|--------|------|-------|
| `chat_id` | Integer PK | auto-increment |
| `chat_name` | String | defaults to first PDF filename |
| `chat_fileloc` | String | path to `uploads/<timestamp>/` batch directory |
| `user_id` | Integer FK → Users | |

### Message
| Column | Type | Notes |
|--------|------|-------|
| `message_id` | Integer PK | auto-increment |
| `chat_id` | Integer FK → Chat | |
| `role` | String | `"user"` or `"assistant"` |
| `content` | String | main message text |
| `key_points` | JSON (nullable) | assistant only — list of key bullets |
| `sources_cited` | JSON (nullable) | assistant only — list of citation strings |
| `follow_up_suggestions` | JSON (nullable) | assistant only — list of follow-up questions |

### DocumentChunk
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer PK | auto-increment |
| `chat_id` | Integer FK → Chat | scopes retrieval to a specific chat |
| `content` | Text | chunk text (PDF paragraph, user question, or Q&A pair) |
| `doc_metadata` | JSON (nullable) | `{"source": "file.pdf", "page": 2}` for PDF chunks; `{"source": "user"}` or `{"source": "AI", "question": "..."}` for history |
| `embedding` | Vector(768) | pgvector 768-dim embedding from `all-mpnet-base-v2` |

> **Three kinds of chunks stored per chat:**
> - **PDF chunk** — inserted on upload; enables document retrieval.
> - **User question chunk** — inserted before each LLM call; seeds semantic history.
> - **Q&A pair chunk** — inserted after each LLM response; lets future questions retrieve past answers.

## 🔄 Workflow

### System Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/HTTPS + JWT Bearer Token
       ▼
┌─────────────────────────────────────────┐
│              FastAPI Backend            │
│  ┌──────────────────────────────────┐  │
│  │   Authentication Layer           │  │
│  │   (JWT verify + Bcrypt)          │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │   API Routers                    │  │
│  │   Auth | Upload | Chat           │  │
│  └──────────────────────────────────┘  │
└────────┬────────────────┬──────────────┘
         │                │
         ▼                ▼
┌────────────────┐  ┌─────────────────────────────┐
│  PostgreSQL    │  │   File System (uploads/)     │
│                │  │                              │
│  • Users       │  │  uploads/<timestamp>/        │
│  • Chat        │  │    └── *.pdf                 │
│  • Message     │  └─────────────────────────────┘
│  • DocumentChunk│
│    (pgvector)  │
└────────┬───────┘
         │ cosine similarity retrieval
         ▼
┌────────────────────────────────────────────────┐
│           OpenAI Agents SDK (RAG Agent)        │
│                                                │
│  Tools:                                        │
│  ┌──────────────────────────────────────────┐ │
│  │ search_knowledge_base → pgvector query   │ │
│  │ search_chat_history   → Message table    │ │
│  │ generate_citation     → citation format  │ │
│  │ WebSearchTool         → live web search  │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  Model: gpt-4o-mini (OpenAI)                  │
│  Output type: LLMResponseFormat (Pydantic)    │
└────────────────────────────────────────────────┘
```

### Step-by-Step Workflow

1. **User Registration & Authentication**
   - Register via `/signup` (email + password, bcrypt hashed) or via GitHub OAuth (`/githublogin`)
   - Login via `/login` to receive a 24-hour JWT token

2. **PDF Upload & Processing**
   - Upload PDFs via `POST /upload-pdfs` (requires JWT)
   - Files saved in `uploads/<YYYYMMDD_HHMMSS>/`
   - A `Chat` record is created; documents are split into chunks
   - Each chunk is embedded with `all-mpnet-base-v2` and inserted as a `DocumentChunk` row in PostgreSQL

3. **Chat Session Management**
   - List sessions via `GET /getchat`
   - Rename sessions via `PATCH /renamechat`
   - Delete sessions via `DELETE /deletechat` (cascades to messages, embeddings, and PDF files)
   - List or download PDFs via `GET /pdf` and `GET /pdf/download`

4. **Question & Answer Flow**
   - User sends `POST /chat` with `chat_id`, `question`, and optional `chat_history`
   - **Ownership check**: verifies the chat belongs to the authenticated user
   - **User message stored** in `Message` table; question embedded and stored as `DocumentChunk`
   - **RAG Agent runs**:
     1. `search_knowledge_base` — cosine search over `document_chunk` (top-5)
     2. `search_chat_history` — last 10 `Message` rows
     3. `generate_citation` — for any referenced content
     4. `WebSearchTool` — if information is missing from uploaded docs
   - **Structured response** (`LLMResponseFormat`) returned by the agent
   - **Assistant message stored** with `key_points`, `sources_cited`, `follow_up_suggestions`
   - **Q&A pair embedded** and inserted as a `DocumentChunk` for future retrieval
   - **Source citations built** from top-4 nearest `DocumentChunk` rows (pgvector cosine distance)

5. **Conversation History**
   - Retrieve full history via `GET /getchatconversation`
   - Includes structured metadata (key_points, sources_cited, follow_up_suggestions) for all assistant messages

## 🔐 Authentication Flow

### Traditional Email/Password Authentication

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Database
    participant Bcrypt
    participant JWT

    User->>API: POST /signup (email, password, name)
    API->>Bcrypt: Hash password
    Bcrypt-->>API: Hashed password
    API->>Database: Store user with hashed password
    Database-->>API: User created
    API-->>User: Success response

    User->>API: POST /login (email, password)
    API->>Database: Get user by email
    Database-->>API: User data
    API->>Bcrypt: Verify password
    Bcrypt-->>API: Password valid
    API->>JWT: Generate token (expires 24h)
    JWT-->>API: JWT token
    API-->>User: Token + user data

    User->>API: Request with Bearer token
    API->>JWT: Verify token
    JWT-->>API: Token valid + user_id
    API->>Database: Verify chat ownership
    Database-->>API: Authorization confirmed
    API-->>User: Protected resource
```

### GitHub OAuth Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant GitHub
    participant Database
    participant JWT

    User->>Frontend: Click "Login with GitHub"
    Frontend->>API: GET /githublogin
    API-->>Frontend: Redirect to GitHub OAuth
    Frontend->>GitHub: Authorization request
    GitHub->>User: Login & authorize app
    User->>GitHub: Approve authorization
    GitHub-->>API: Redirect with code
    API->>GitHub: POST /oauth/access_token (code)
    GitHub-->>API: Access token
    API->>GitHub: GET /user (with token)
    GitHub-->>API: User profile data
    alt Email not public
        API->>GitHub: GET /user/emails
        GitHub-->>API: Email list
    end
    API->>Database: Find or create user
    Database-->>API: User data
    API->>JWT: Generate JWT token
    JWT-->>API: JWT token
    API-->>Frontend: Redirect with token & user data
    Frontend->>Frontend: Store token
    Frontend-->>User: Logged in successfully
```

## 🔒 Security Features & Notes

- **JWT**: HS256-signed tokens with 24-hour expiration
- **Password hashing**: bcrypt with automatic salt
- **Chat ownership**: every chat endpoint verifies `Chat.user_id == current_user.user_id`
- **Path traversal prevention**: `GET /pdf/download` strips the filename to its basename before constructing the file path
- **Upload folder safety**: `DELETE /deletechat` only removes subfolders inside `uploads/`, never the root upload directory
- **CORS**: currently set to `*` — restrict to your frontend origin in production
- **`.env`**: never committed; listed in `.gitignore`

## 🐳 Docker Support

### Dockerfile

The `Dockerfile` uses `python:3.11-slim` and installs dependencies via `requirements.txt`.

```bash
docker build -t rag-backend .
docker run -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e OPENAI_API_KEY=sk-proj-... \
  -e DATABASE_URI=postgresql://postgres:password@host:5432/rag_database \
  rag-backend
```

### Docker Compose

`docker-compose.yml` starts both the API and a PostgreSQL instance together:

```bash
docker compose up --build
```

> After starting, enable the pgvector extension in the PostgreSQL container:
> ```bash
> docker exec -it <db_container_name> psql -U postgres -d rag_database -c "CREATE EXTENSION IF NOT EXISTS vector;"
> ```

## 💡 Usage Example

### Full end-to-end flow with `curl`

```bash
# 1. Sign up
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"user_name":"Alice","email":"alice@example.com","password":"Secret123"}'

# 2. Login and capture the token
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Secret123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['User']['token'])")

# 3. Upload a PDF and capture the chat_id
CHAT_ID=$(curl -s -X POST http://localhost:8000/upload-pdfs \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@lecture.pdf" \
  | python -c "import sys,json; print(json.load(sys.stdin)['chat_id'])")

# 4. Ask a question
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": $CHAT_ID, \"question\": \"What are the main topics?\", \"chat_history\": []}"

# 5. List PDFs in the chat
curl "http://localhost:8000/pdf?chatid=$CHAT_ID" \
  -H "Authorization: Bearer $TOKEN"

# 6. Rename the chat
curl -X PATCH http://localhost:8000/renamechat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": $CHAT_ID, \"chat_name\": \"Lecture Notes\"}"

# 7. Delete the chat
curl -X DELETE "http://localhost:8000/deletechat?chatid=$CHAT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 Troubleshooting

### pgvector extension not found
```
sqlalchemy.exc.ProgrammingError: type "vector" does not exist
```
Run `CREATE EXTENSION IF NOT EXISTS vector;` in your PostgreSQL database before starting the app.

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set and valid
- The agent uses `gpt-4o-mini` by default; set `OPENAI_MODEL` in `.env` to change it
- Check your OpenAI usage limits / billing

### Embedding model download slow on first run
`sentence-transformers/all-mpnet-base-v2` (~420 MB) is downloaded from HuggingFace Hub on first use. Subsequent runs use the local cache.

### Upload fails with vector store error
If `add_vector_to_db` fails, the database transaction is rolled back and `chat_id` in the response will be `null`. Check server logs for the specific error (common causes: pgvector not installed, PDF with no extractable text, embedding model not loaded).

### CORS errors in browser
Add your frontend origin to `allow_origins` in `main.py`:
```python
allow_origins=["http://localhost:5173", "https://your-app.vercel.app"]
```

## ❓ Frequently Asked Questions (FAQ)

**Q: Does this support non-PDF documents?**
A: Not currently. Only `.pdf` files are accepted by the upload route.

**Q: Where are embeddings stored?**
A: All embeddings are stored in the `document_chunk` table in PostgreSQL using the pgvector `Vector(768)` column type. There are no FAISS index files written to disk by active routes.

**Q: Can I use a different OpenAI model?**
A: Yes — set `OPENAI_MODEL=gpt-4o` (or any supported model) in your `.env`.

**Q: Can I use a different embedding model?**
A: Yes, but you must also update the vector dimension. Change the model in `retriver/embedding.py` and update `Vector(768)` in `db/data_models.py` to match the new model's output size. Existing embeddings in the database will be incompatible and must be regenerated.

**Q: What is `retriver/fas.py` for?**
A: It is legacy code from the previous FAISS-based vector store implementation. It is not called by any active route and can be removed once you no longer need it.

**Q: How is conversation context passed to the agent?**
A: The `/chat` request accepts a `chat_history` list that is formatted into the agent's input string. The agent also calls `search_chat_history` to fetch the last 10 messages from the database, providing two layers of context.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please follow existing code style and add docstrings for new functions.

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
