# RAG Backend API

A production-ready FastAPI backend service for PDF document processing and intelligent Q&A using Retrieval Augmented Generation (RAG) with LangChain and FAISS vector store.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## � Table of Contents

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
- [Performance](#-performance-considerations)
- [FAQ](#-frequently-asked-questions-faq)
- [Contributing](#-contributing)
- [License](#-license)

## �📋 Overview

This project provides a comprehensive REST API that enables users to upload PDF documents, process them into a vector database, and interact with the content through an AI-powered chat interface powered by Google Gemini 3 Flash Preview. The system leverages a dual vector store architecture with FAISS for both document retrieval and semantic chat history search, generating structured, contextual responses using Large Language Models with Pydantic output parsing.

The API features a complete authentication system with JWT token-based security, bcrypt password hashing, user authorization for chat access, and persistent conversation history storage for each chat session. All data is stored in PostgreSQL with full relational database support for users, chats, and messages. The LLM responses include structured output with answer, key points, confidence level, source citations, and follow-up suggestions.

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

# 4. Configure environment variables
# Create .env file with:
# JWT_SECRET=your-secret-key
# GOOGLE_API_KEY=your-google-api-key

# 5. Start PostgreSQL and create database
# psql -U postgres -c "CREATE DATABASE rag_database;"

# 6. Run the application
uvicorn main:app --reload

# 7. Visit http://127.0.0.1:8000/docs for interactive API documentation
```

## ✨ Features

### Core Functionality
✅ **Complete Authentication System**
- User signup and login with email/password
- JWT token-based authentication (24-hour expiration)
- Bcrypt password hashing with salt
- Protected route middleware
- User-specific data isolation

✅ **Document Processing**
- Multi-file PDF upload support
- Automatic text extraction from PDFs
- Intelligent document chunking
- Batch organization with timestamps
- Persistent file storage

✅ **RAG (Retrieval Augmented Generation)**
- Google Gemini 3 Flash Preview model
- Google Generative AI embeddings
- Dual FAISS vector store system:
  - Document vector store for PDF content
  - Chat history vector store for past conversations
- Structured output with Pydantic parser
- Context-aware response generation with:
  - Answer text
  - Key points extraction
  - Confidence level assessment
  - Source citations
  - Follow-up suggestions
- Semantic document and chat history retrieval
- Per-chat isolated vector stores
- HuggingFace and sentence transformers integration

✅ **Chat Management**
- Multiple chat sessions per user
- Create new chats with PDF uploads
- Delete chats with automatic cleanup (files + database)
- Full conversation history storage in both:
  - PostgreSQL database for persistence
  - FAISS vector store for semantic retrieval
- Message persistence with role-based storage (user/assistant)
- Chat ownership verification for security
- Retrieve past conversations
- Semantic search across chat history
- Structured JSON response format

✅ **API Features**
- RESTful API design
- Interactive Swagger documentation (`/docs`)
- Alternative ReDoc documentation (`/redoc`)
- CORS enabled for frontend integration
- Comprehensive error handling
- Health check endpoint

✅ **Data Management**
- PostgreSQL database with SQLAlchemy ORM
- Relational data model (Users, Chats, Messages)
- Database transaction safety
- Automatic rollback on errors
- Async database operations

### Technical Features
- 🚀 **High Performance**: FastAPI framework with async support
- 🔒 **Security**: JWT + Bcrypt authentication
- 📦 **Modular Architecture**: Organized routers and utilities
- 🐳 **Docker Ready**: Containerization support
- 🔧 **Type Safety**: Pydantic models for validation
- 📊 **Scalable**: Designed for production deployment

## 🏗️ Project Structure

```
rag_backend/
├── db/                      # Database configuration and models
│   ├── config.py           # Database session management
│   ├── database.py         # SQLAlchemy engine and connection
│   └── data_models.py      # User, Chat, and Message table models
├── llm/                     # Language model integration
│   └── chatmodel.py        # Structured chat response generation with Pydantic parser
├── models/                  # Pydantic models
│   └── pymodel.py          # Request/Response schemas and LLMResponseFormat
├── retriver/                # Document retrieval system
│   └── fas.py              # Dual FAISS vector store (document + chat history)
├── route/                   # API route handlers (modular routers)
│   ├── auth_route/         # Authentication endpoints
│   │   └── auth_router.py  # Signup and login routes
│   ├── chat_route/         # Chat endpoints
│   │   └── chat_router.py  # Document Q&A and chat management routes
│   └── upload_route/       # Upload endpoints
│       └── upload_router.py # PDF upload routes
├── utils/                   # Utility functions
│   ├── hash.py             # Password hashing with bcrypt
│   ├── jwt.py              # JWT token generation and verification
│   └── protectroute.py     # Protected route middleware
├── uploads/                 # PDF storage directory (timestamped batches)
│   └── YYYYMMDD_HHMMSS/    # Each batch contains:
│       ├── *.pdf            # Uploaded PDF files
│       ├── faiss_index_doc/ # Document vector store
│       └── faiss_index_chat/# Chat history vector store
├── main.py                  # FastAPI application and router registration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── .env                     # Environment variables (JWT_SECRET, etc.)
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** (This project uses Python 3.13)
- **PostgreSQL database** (Version 12 or higher recommended)
- **Google Generative AI API Key** (Required for embeddings and LLM)
- **Virtual environment** (Strongly recommended for dependency isolation)
- **Git** (For cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd rag_backend
   ```
   *Replace `<your-repository-url>` with your actual Git repository URL.*

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
   - Create a `.env` file in the root directory (`rag_backend/`) with the following configuration:
     ```env
     # JWT Configuration
     JWT_SECRET=your-secret-key-change-this-in-production-use-strong-random-string
     JWT_ALGORITHM=HS256
     
     # Google Generative AI API Key (Required)
     GOOGLE_API_KEY=your-google-api-key-here
     ```
   - **Important**: 
     - Generate a strong `JWT_SECRET` for production (minimum 32 characters)
     - Obtain `GOOGLE_API_KEY` from [Google AI Studio](https://makersuite.google.com/app/apikey)
     - Never commit the `.env` file to version control (already in `.gitignore`)

6. **Initialize the database**
   - The application will automatically create tables on first run
   - Ensure your PostgreSQL service is running

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | Yes | None | Secret key for JWT token signing (min 32 chars) |
| `JWT_ALGORITHM` | No | `HS256` | Algorithm for JWT encoding |
| `GOOGLE_API_KEY` | Yes | None | Google Generative AI API key |
| `DATABASE_URI` | No | See below | PostgreSQL connection string |

**Example `.env` file:**
```env
# Security
JWT_SECRET=your-super-secret-key-change-in-production-minimum-32-characters
JWT_ALGORITHM=HS256

# AI Model
GOOGLE_API_KEY=AIzaSyC...your-actual-key-here

# Database (optional if using default)
# DATABASE_URI=postgresql://postgres:password@localhost:5432/rag_database
```

### Database Configuration

The database connection is configured in [db/database.py](db/database.py). Default connection:
```python
DATABASE_URI = "postgresql://postgres:password@localhost:5432/rag_database"
```

**Customize for production:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:password@localhost:5432/rag_database")
```

**Application Settings**

Additional configuration options can be modified in source files:
- **JWT Token Expiration**: [utils/jwt.py](utils/jwt.py) - Default 24 hours
- **Upload Directory**: [route/upload_route/upload_router.py](route/upload_route/upload_router.py) - Default `uploads/`
- **CORS Origins**: [main.py](main.py) - Default allows all (`*`)
- **Chunk Size**: [retriver/fas.py](retriver/fas.py) - chunk_size=500, chunk_overlap=300
- **Embedding Model**: [retriver/fas.py](retriver/fas.py) - `sentence-transformers/all-mpnet-base-v2`
- **Retrieval Count**: [llm/chatmodel.py](llm/chatmodel.py) - Top 20 results for both document and chat retrieval

### Running the Application

**Option 1: Development Mode (with auto-reload)**
```bash
uvicorn main:app --reload
```

**Option 2: Production Mode**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- Local: `http://127.0.0.1:8000`
- Network: `http://0.0.0.0:8000` (production)
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Alternative Docs: `http://127.0.0.1:8000/redoc`

## 📡 API Endpoints

### Endpoints Summary

| Method | Endpoint | Authentication | Description |
|--------|----------|----------------|-------------|
| GET | `/` | No | API status check |
| GET | `/health` | No | Health check endpoint |
| POST | `/signup` | No | User registration |
| POST | `/login` | No | User authentication |
| GET | `/protected` | Yes | Protected route example |
| POST | `/upload-pdfs` | Yes | Upload PDF files |
| POST | `/chat` | Yes | Ask questions about documents |
| GET | `/getchat` | Yes | Get all user chat sessions |
| GET | `/getchatconversation` | Yes | Get chat message history |
| DELETE | `/deletechat` | Yes | Delete a chat session and its files |

### Authentication Routes

#### 1. User Signup
```http
POST /signup
```
**Description**: Register a new user account.

**Request Body**:
```json
{
  "user_name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response**:
```json
{
  "User": {
    "user_id": 1,
    "user_name": "John Doe",
    "email": "john@example.com"
  },
  "Successful": true,
  "message": "User created successfully"
}
```

#### 2. User Login
```http
POST /login
```
**Description**: Login and receive JWT authentication token.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response**:
```json
{
  "User": {
    "user_id": 1,
    "user_name": "John Doe",
    "email": "john@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "Successful": true,
  "message": "User logged in successfully"
}
```

### Document Management Routes

#### 3. Upload PDFs
```http
POST /upload-pdfs
```
**Description**: Upload one or multiple PDF files for processing. Creates a chat session and processes documents into vector store.

**Authentication**: Required (Bearer Token)

**Request**: 
- Content-Type: `multipart/form-data`
- Body: `files` (List of PDF files)
- Headers: `Authorization: Bearer <token>`

**Response**:
```json
{
  "message": "Successfully uploaded 2 file(s)",
  "files": [
    {
      "filename": "document.pdf",
      "size": 124567,
      "path": "uploads/20260210_223829/document.pdf",
      "batch": "20260210_223829"
    }
  ],
  "chat_id": 1,
  "errors": null
}
```

**Error Response** (Vector store creation fails):
```json
{
  "message": "Files uploaded but vector store update failed: <error details>",
  "files": [...],
  "chat_id": null,
  "errors": []
}
```

### Chat Routes

#### 4. Chat with Documents
```http
POST /chat
```
**Description**: Ask questions about uploaded documents. Maintains conversation history in database.

**Authentication**: Required (Bearer Token)

**Request Body**:
```json
{
  "chat_id": 1,
  "question": "What is the main topic of the document?",
  "chat_history": [
    {
      "role": "user",
      "content": "Previous question"
    },
    {
      "role": "assistant",
      "content": "Previous answer"
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "chat_id": 1,
  "response": "{\"answer\": \"Based on the uploaded documents, the main topic is...\", \"key_points\": [\"Point 1\", \"Point 2\"], \"confidence_level\": \"high\", \"sources_cited\": [\"document.pdf - page 2\"], \"needs_clarification\": false, \"follow_up_suggestions\": [\"Related question 1?\", \"Related question 2?\"]}",
  "role": "assistant",
  "timestamp": "2026-02-16T10:30:00",
  "sources_used": 3,
  "error_message": null
}
```

**Note**: The `response` field contains a JSON-encoded string with structured LLM output including answer, key points, confidence level, source citations, and follow-up suggestions.

**Error Response**:
```json
{
  "success": false,
  "chat_id": 1,
  "response": "",
  "role": "assistant",
  "timestamp": "2026-02-16T10:30:00",
  "sources_used": null,
  "error_message": "Chat not found or access denied"
}
```

#### 5. Get User Chats
```http
GET /getchat
```
**Description**: Retrieve all chat sessions for the authenticated user.

**Authentication**: Required (Bearer Token)

**Response**:
```json
{
  "chats": [
    {
      "chat_id": 1,
      "chat_name": "document.pdf"
    },
    {
      "chat_id": 2,
      "chat_name": "report.pdf"
    }
  ],
  "Successful": true
}
```

#### 6. Get Chat Conversation
```http
GET /getchatconversation?chatid=1
```
**Description**: Retrieve full conversation history for a specific chat.

**Authentication**: Required (Bearer Token)

**Query Parameters**:
- `chatid` (integer): The chat ID

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the main topic?"
    },
    {
      "role": "system",
      "content": "The main topic is..."
    }
  ],
  "Successful": true
}
```

**Error Response**:
```json
{
  "messages": [],
  "error": "Chat not found or access denied",
  "Successful": false
}
```

#### 7. Delete Chat
```http
DELETE /deletechat?chatid=1
```
**Description**: Delete a chat session, including all messages and associated files (PDFs and FAISS indexes).

**Authentication**: Required (Bearer Token)

**Query Parameters**:
- `chatid` (integer): The chat ID to delete

**Response**:
```json
{
  "Successful": true,
  "message": "Chat deleted successfully"
}
```

**Error Response**:
```json
{
  "Successful": false,
  "message": "Failed to delete chat"
}
```

**Note**: This endpoint performs:
- Ownership verification (ensures chat belongs to user)
- Deletion of all messages associated with the chat
- Deletion of the chat folder (PDFs + FAISS indexes)
- Deletion of the chat record from database
- Transaction rollback on errors

### Protected Routes

#### 8. Protected Endpoint (Example)
```http
GET /protected
```
**Description**: Example of JWT-protected route. Requires valid Bearer token.

**Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```json
{
  "user": {
    "user_id": 1,
    "user_name": "John Doe",
    "email": "john@example.com"
  }
}
```

### System Routes

#### 9. Root Endpoint
```http
GET /
```
Returns API status message.

**Response**:
```json
{
  "message": "PDF Upload API is running"
}
```

#### 10. Health Check
```http
GET /health
```
Returns service health status.

**Response**:
```json
{
  "health": "okay"
}
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** - Modern, high-performance web framework for building APIs
- **Uvicorn** - Lightning-fast ASGI server

### Authentication & Security
- **PyJWT** - JWT token encoding, decoding, and verification
- **Bcrypt** - Industry-standard password hashing with salt
- **Email Validator** - Email format validation

### Database
- **PostgreSQL** - Relational database for persistent storage
- **SQLAlchemy** - Powerful SQL toolkit and ORM
- **asyncpg** - High-performance async PostgreSQL driver
- **psycopg2-binary** - PostgreSQL adapter for Python

### RAG & AI Components
- **LangChain Core** - Foundation for LLM application development with Pydantic output parser
- **LangChain Community** - Community integrations and utilities
- **LangChain Google GenAI** - Google Gemini 3 Flash Preview integration
- **LangChain HuggingFace** - HuggingFace model integration
- **LangChain Text Splitters** - Document chunking utilities
- **FAISS (CPU)** - Facebook AI Similarity Search for dual vector store operations
- **Google Generative AI** - Embeddings and structured LLM responses
- **Sentence Transformers** - Text embeddings for semantic search
- **HuggingFace** - Model hub integration

### Document Processing
- **PyPDF** - PDF document parsing and text extraction

### Additional Libraries
- **Pydantic** - Data validation using Python type hints
- **Pydantic Settings** - Settings management
- **Python Multipart** - File upload handling
- **Python Dotenv** - Environment variable management
- **CORS Middleware** - Cross-Origin Resource Sharing support

## 📦 Key Dependencies

All dependencies are listed in [requirements.txt](requirements.txt). Install them using:
```bash
pip install -r requirements.txt
```

**Core Libraries:**
- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server implementation
- `pyjwt` - JWT token encoding and decoding
- `bcrypt` - Password hashing and verification
- `sqlalchemy` - SQL toolkit and ORM
- `asyncpg` - Async PostgreSQL driver
- `psycopg2-binary` - PostgreSQL adapter

**AI & RAG Libraries:**
- `langchain-core` - LangChain core functionality with output parsers
- `langchain-community` - Community integrations
- `langchain-google-genai` - Google Gemini 3 Flash Preview integration
- `langchain-huggingface` - HuggingFace model integration
- `sentence_transformers` - Text embeddings for semantic search
- `langchain-text-splitters` - Text splitting utilities
- `faiss-cpu` - Dual vector store for documents and chat history
- `pypdf` - PDF document parsing

**Utilities:**
- `pydantic` - Data validation using type hints
- `pydantic-settings` - Settings management
- `python-dotenv` - Environment variables
- `python-multipart` - File upload support
- `email-validator` - Email validation

## 🗄️ Database Schema

### Users Table
- `user_id` (Integer, Primary Key, Auto-increment)
- `user_name` (String) - User's full name
- `email` (String) - User's email address (unique)
- `password` (String) - Bcrypt hashed password
- **Relationships**: One-to-Many with Chat table

### Chat Table
- `chat_id` (Integer, Primary Key, Auto-increment)
- `chat_name` (String) - Chat session name (typically first PDF filename)
- `chat_fileloc` (String) - File location of the batch directory
- `user_id` (Integer, Foreign Key to Users table)
- **Relationships**: 
  - Many-to-One with Users table
  - One-to-Many with Message table

### Message Table
- `message_id` (Integer, Primary Key, Auto-increment)
- `chat_id` (Integer, Foreign Key to Chat table)
- `role` (String) - Message role: "user" or "system"
- `content` (String) - Message content
- **Relationships**: Many-to-One with Chat table

## 🔄 Workflow

### System Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/HTTPS
       │ JWT Token
       ▼
┌─────────────────────────────────────────┐
│           FastAPI Backend               │
│  ┌────────────────────────────────┐    │
│  │     Authentication Layer        │    │
│  │  (JWT Verify + Bcrypt)         │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │         API Routes              │    │
│  │  • Auth    • Upload  • Chat    │    │
│  └────────────────────────────────┘    │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────────┐
│  PostgreSQL  │   │   File System    │
│   Database   │   │   (uploads/)     │
│              │   │                  │
│  • Users     │   │  • PDFs          │
│  • Chat      │   │  • FAISS Indexes │
│  • Messages  │   └──────────────────┘
└──────────────┘
       │
       │ Query Context
       ▼
┌────────────────────────────────────────┐
│        LangChain + RAG System          │
│  ┌────────────┐    ┌───────────────┐  │
│  │   FAISS    │◄───│  Google Gen   │  │
│  │  Retriever │    │  AI Embeddings│  │
│  └────────────┘    └───────────────┘  │
│         ▼                              │
│  ┌────────────────────────────────┐   │
│  │  Google Generative AI (LLM)    │   │
│  │  Response Generation           │   │
│  └────────────────────────────────┘   │
└────────────────────────────────────────┘
```

### Workflow

1. **User Registration & Authentication**
   - User creates account via `/signup` endpoint with email and password
   - Password is hashed with bcrypt before storage
   - User logs in via `/login` and receives JWT token (24-hour expiration)

2. **PDF Upload & Processing**
   - User uploads PDF files via `/upload-pdfs` endpoint (requires JWT token)
   - PDFs are saved in timestamped batch directories (e.g., `uploads/20260216_143052/`)
   - New Chat record is created in database with first PDF filename as chat name
   - Documents are split into chunks for processing

3. **Vector Embedding & Storage (Dual Vector Store System)**
   - Document chunks are processed with RecursiveCharacterTextSplitter (chunk_size=500, chunk_overlap=300)
   - Embeddings generated using HuggingFace `sentence-transformers/all-mpnet-base-v2` model
   - **Document Vector Store**: FAISS index created for PDF content in batch's `faiss_index_doc` subdirectory
   - **Chat History Vector Store**: Separate FAISS index in `faiss_index_chat` subdirectory for storing past Q&A pairs
   - Both vector stores enable semantic similarity search
   - Each chat has isolated vector stores in its timestamped directory

4. **Chat Session Management**
   - User retrieves their chat sessions via `/getchat` endpoint
   - Each chat is linked to a specific batch of uploaded PDFs
   - Full conversation history is maintained in both PostgreSQL and vector store
   - Users can delete chats via `/deletechat` endpoint (removes files, indexes, and database records)

5. **Question & Answer Flow (Enhanced with Structured Output)**
   - User sends questions via `/chat` endpoint with chat_id and chat_history (requires JWT token)
   - **Security Check**: System verifies the chat belongs to authenticated user
   - **Message Storage**: User's question stored in Message table (role="user")
   - **Dual Retrieval**:
     - Retrieves top 20 relevant document chunks from document vector store
     - Retrieves top 20 relevant past conversations from chat history vector store
   - **Structured Generation**: Google Gemini 3 Flash Preview generates response with Pydantic output parser
   - **LLM Response Structure**:
     - `answer`: Main response text
     - `key_points`: List of important points
     - `confidence_level`: "high", "medium", or "low"
     - `sources_cited`: List of source references
     - `needs_clarification`: Boolean flag
     - `clarification_needed`: Optional clarification request
     - `follow_up_suggestions`: List of suggested follow-up questions
   - **Response Storage**: System's answer stored in Message table (role="assistant")
   - **Chat History Update**: Q&A pair added to chat history vector store for future semantic retrieval
   - **Response**: Full structured JSON returned to user with timestamp and metadata

6. **Conversation History**
   - User can retrieve full conversation history via `/getchatconversation` endpoint
   - History includes all user questions and system responses
   - Conversations persist across sessions in PostgreSQL
   - Past conversations are semantically searchable via chat history vector store

7. **Chat Deletion**
   - User can delete unwanted chats via `/deletechat` endpoint (requires JWT token)
   - **Comprehensive Cleanup**: 
     - Deletes all messages associated with the chat
     - Removes entire batch folder (PDFs + FAISS indexes)
     - Deletes chat record from database
   - **Safety Checks**: Ownership verification and path validation
   - **Transactional**: Automatic rollback on errors

1. **User Registration & Authentication**
   - User creates account via `/signup` endpoint with email and password
   - Password is hashed with bcrypt before storage
   - User logs in via `/login` and receives JWT token (24-hour expiration)

2. **PDF Upload & Processing**
   - User uploads PDF files via `/upload-pdfs` endpoint (requires JWT token)
   - PDFs are saved in timestamped batch directories (e.g., `uploads/20260216_143052/`)
   - New Chat record is created in database with first PDF filename as chat name
   - Documents are split into chunks for processing

3. **Vector Embedding & Storage (Dual Vector Store System)**
   - Document chunks are processed with RecursiveCharacterTextSplitter (chunk_size=500, chunk_overlap=300)
   - Embeddings generated using HuggingFace `sentence-transformers/all-mpnet-base-v2` model
   - **Document Vector Store**: FAISS index created for PDF content in batch's `faiss_index_doc` subdirectory
   - **Chat History Vector Store**: Separate FAISS index in `faiss_index_chat` subdirectory for storing past Q&A pairs
   - Both vector stores enable semantic similarity search
   - Each chat has isolated vector stores in its timestamped directory

4. **Chat Session Management**
   - User retrieves their chat sessions via `/getchat` endpoint
   - Each chat is linked to a specific batch of uploaded PDFs
   - Full conversation history is maintained in both PostgreSQL and vector store

5. **Question & Answer Flow (Enhanced with Structured Output)**
   - User sends questions via `/chat` endpoint with chat_id and chat_history (requires JWT token)
   - **Security Check**: System verifies the chat belongs to authenticated user
   - **Message Storage**: User's question stored in Message table (role="user")
   - **Dual Retrieval**:
     - Retrieves top 20 relevant document chunks from document vector store
     - Retrieves top 20 relevant past conversations from chat history vector store
   - **Structured Generation**: Google Gemini 3 Flash Preview generates response with Pydantic output parser
   - **LLM Response Structure**:
     - `answer`: Main response text
     - `key_points`: List of important points
     - `confidence_level`: "high", "medium", or "low"
     - `sources_cited`: List of source references
     - `needs_clarification`: Boolean flag
     - `clarification_needed`: Optional clarification request
     - `follow_up_suggestions`: List of suggested follow-up questions
   - **Response Storage**: System's answer stored in Message table (role="assistant")
   - **Chat History Update**: Q&A pair added to chat history vector store for future semantic retrieval
   - **Response**: Full structured JSON returned to user with timestamp and metadata

6. **Conversation History**
   - User can retrieve full conversation history via `/getchatconversation` endpoint
   - History includes all user questions and system responses
   - Conversations persist across sessions in PostgreSQL
   - Past conversations are semantically searchable via chat history vector store

## 🔒 Security Features & Notes

### Implemented Security Features
- ✅ **Password Hashing**: Passwords are hashed using bcrypt with salt before storage (never stored in plain text)
- ✅ **JWT Authentication**: Secure token-based authentication with 24-hour expiration
- ✅ **Protected Routes**: Middleware validates JWT tokens on all protected endpoints
- ✅ **User Authorization**: Chat ownership verification prevents unauthorized access to other users' chats
- ✅ **Database Transactions**: Automatic rollback support on errors to maintain data integrity
- ✅ **Email Validation**: Prevents duplicate user registration and validates email format
- ✅ **Query Parameter Validation**: Pydantic models ensure proper data types and prevent injection attacks
- ✅ **SQLAlchemy ORM**: Protection against SQL injection attacks
- ✅ **Type Safety**: Pydantic models enforce type checking on all API requests/responses

### Production Security Checklist

⚠️ **Critical - Must Change:**
- [ ] **JWT_SECRET**: Replace with a strong, randomly generated secret key (minimum 32 characters)
  ```bash
  # Generate secure secret key
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] **Database Credentials**: Change default PostgreSQL password
- [ ] **CORS Origins**: Restrict `allow_origins` from `["*"]` to specific frontend domains in [main.py](main.py)
  ```python
  allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
  ```

🔒 **Recommended Security Enhancements:**
- [ ] **HTTPS**: Deploy with SSL/TLS certificates (use Let's Encrypt for free certificates)
- [ ] **Rate Limiting**: Implement rate limiting on authentication and upload endpoints
- [ ] **File Upload Validation**: 
  - Validate file MIME types (ensure only PDFs are accepted)
  - Set maximum file size limits (e.g., 10MB per file)
  - Scan uploaded files for malware
- [ ] **Token Refresh**: Implement refresh tokens for better user experience
- [ ] **Password Policy**: Enforce strong password requirements:
  - Minimum length (8-12 characters)
  - Complexity requirements (uppercase, lowercase, numbers, special characters)
  - Password strength meter on frontend
- [ ] **Logging & Monitoring**: 
  - Log authentication attempts (successful and failed)
  - Monitor for suspicious activity
  - Implement alerting for security events
- [ ] **Environment Variables**: Use secret management service (AWS Secrets Manager, HashiCorp Vault)
- [ ] **API Versioning**: Implement API versioning (e.g., `/api/v1/`)
- [ ] **Request Validation**: Add comprehensive input validation and sanitization
- [ ] **Path Traversal Protection**: Validate all file paths (already using timestamped directories)
- [ ] **Session Management**: Consider session timeout and concurrent session limits
- [ ] **Audit Trail**: Log all data modifications (who, what, when)

## 🐳 Docker Support

A Dockerfile is included for containerized deployment.

### Building the Docker Image
```bash
docker build -t rag-backend:latest .
```

### Running with Docker
```bash
docker run -d \
  -p 8000:8000 \
  -e JWT_SECRET="your-jwt-secret" \
  -e GOOGLE_API_KEY="your-google-api-key" \
  -e DATABASE_URI="postgresql://user:password@host:5432/database" \
  --name rag-backend \
  rag-backend:latest
```

### Docker Compose (Recommended)

For a complete setup with PostgreSQL, create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_database
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URI=postgresql://postgres:password@postgres:5432/rag_database
      - JWT_SECRET=${JWT_SECRET}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## 🔐 Authentication Flow

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

### Flow Steps

1. **Signup**: User registers with email, username, and password
2. **Password Hashing**: Password is hashed with bcrypt and salt before database storage
3. **Login**: User authenticates with email and password
4. **Credential Validation**: System verifies hashed password matches
5. **Token Generation**: JWT token is created with 24-hour expiration
6. **Token Storage**: Client stores token (localStorage/sessionStorage)
7. **Authenticated Requests**: Client includes token in Authorization header: `Bearer <token>`
8. **Token Verification**: Protected routes validate JWT signature and expiration
9. **User Extraction**: User information is extracted from valid token
10. **Authorization Check**: Chat routes verify the resource belongs to the authenticated user
11. **Error Handling**: Invalid/expired tokens return 401, unauthorized access returns error message
## 💡 Usage Example

```bash
# 1. Sign up a new user
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "email": "john@example.com",
    "password": "securePassword123"
  }'

# 2. Login to get JWT token
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securePassword123"
  }'

# Response: { "User": { ..., "token": "eyJhbG..." }, ... }

# 3. Use token to access protected routes
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer eyJhbG..."

# 4. Upload PDFs (protected - requires token)
curl -X POST http://localhost:8000/upload-pdfs \
  -H "Authorization: Bearer eyJhbG..." \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"

# Response: { "message": "Successfully uploaded 2 file(s)", "chat_id": 1, ... }

# 5. Get all user chat sessions
curl -X GET http://localhost:8000/getchat \
  -H "Authorization: Bearer eyJhbG..."

# Response: { "chats": [{"chat_id": 1, "chat_name": "document1.pdf"}], "Successful": true }

# 6. Chat with documents
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbG..." \
  -d '{
    "chat_id": 1,
    "question": "What is the main topic?"
  }'

# Response: { "response": "The main topic is...", "Successful": true }

# 7. Get conversation history
curl -X GET "http://localhost:8000/getchatconversation?chatid=1" \
  -H "Authorization: Bearer eyJhbG..."

# Response: { "messages": [{"role": "user", "content": "..."}, {"role": "system", "content": "..."}], "Successful": true }

# 8. Delete a chat session
curl -X DELETE "http://localhost:8000/deletechat?chatid=1" \
  -H "Authorization: Bearer eyJhbG..."

# Response: { "Successful": true, "message": "Chat deleted successfully" }
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution:**
- Ensure PostgreSQL service is running
- Verify database credentials in [db/database.py](db/database.py)
- Check if database `rag_database` exists:
  ```bash
  psql -U postgres -c "CREATE DATABASE rag_database;"
  ```

#### 2. JWT Token Errors (401 Unauthorized)
```json
{"detail": "Invalid token"}
```
**Solution:**
- Ensure `.env` file exists with `JWT_SECRET`
- Check token format: `Authorization: Bearer <token>`
- Token may be expired (24-hour lifetime)
- Re-login to get a fresh token

#### 3. Google API Key Error
```
Error: GOOGLE_API_KEY not found
```
**Solution:**
- Add `GOOGLE_API_KEY` to `.env` file
- Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Restart the application after adding the key

#### 4. FAISS Index Error
```
Failed to load FAISS index
```
**Solution:**
- Delete corrupted index: `uploads/<batch_name>/faiss_index/`
- Re-upload PDFs to recreate the index
- Ensure sufficient disk space for vector storage

#### 5. PDF Upload Fails
```json
{"message": "Files uploaded but vector store update failed"}
```
**Solution:**
- Check PDF file is not corrupted
- Ensure PDF contains extractable text (not scanned images only)
- Verify GOOGLE_API_KEY is valid and has quota remaining
- Check disk space in `uploads/` directory

#### 6. Module Import Errors
```
ModuleNotFoundError: No module named 'xyz'
```
**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version is 3.13+

#### 7. Port Already in Use
```
ERROR: [Errno 10048] error while attempting to bind on address
```
**Solution:**
- Change port: `uvicorn main:app --port 8001`
- Or kill existing process on Windows:
  ```powershell
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

### Debug Mode

Enable detailed logging by adding to [main.py](main.py):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- Check the Issues section on your Git repository
- Review [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review [LangChain documentation](https://python.langchain.com/)

---

## ⚡ Performance Considerations

### Optimization Tips

1. **Database Connection Pooling**
   - SQLAlchemy automatically manages connection pools
   - Adjust pool size for high-traffic scenarios in [db/database.py](db/database.py)

2. **FAISS Index Optimization**
   - FAISS CPU version is used (suitable for moderate scale)
   - For large datasets, consider FAISS GPU version
   - Dual vector store system: one for documents (faiss_index_doc), one for chat history (faiss_index_chat)
   - Index loading is per-chat (memory efficient)
   - Embedding model: HuggingFace `sentence-transformers/all-mpnet-base-v2`
   - Top-k retrieval: 20 results from each vector store

3. **Document Chunking**
   - Current configuration: chunk_size=500, chunk_overlap=300 (RecursiveCharacterTextSplitter)
   - Chunk size affects retrieval quality and speed
   - Adjust in [retriver/fas.py](retriver/fas.py) if needed
   - Smaller chunks = more precise, larger chunks = more context
   - Overlap ensures context continuity across chunks

4. **API Rate Limiting**
   - Implement rate limiting for production to prevent abuse
   - Recommended: 100 requests/minute per user

5. **Caching**
   - Consider caching frequently accessed chat conversations
   - Redis integration for session management
   - Cache FAISS indexes in memory for active chats

6. **Async Operations**
   - FastAPI runs on ASGI (async support)
   - Database operations use async driver (asyncpg)
   - Consider async file operations for large uploads

### Scalability

- **Horizontal Scaling**: Deploy multiple instances behind load balancer
- **Database**: PostgreSQL supports read replicas
- **Storage**: Use object storage (S3, Azure Blob) for production file storage
- **Vector Store**: Consider managed solutions like Pinecone or Weaviate for scale

---

## ❓ Frequently Asked Questions (FAQ)

### General Questions

**Q: What types of documents are supported?**  
A: Currently, only PDF documents are supported. The system extracts text from PDFs using PyPDF library.

**Q: Can I upload scanned PDFs?**  
A: The system works best with PDFs containing extractable text. Scanned PDFs (images) may not work unless they have been OCR-processed.

**Q: How many files can I upload at once?**  
A: Multiple files can be uploaded in a single batch. Consider implementing file size limits in production.

**Q: How accurate are the responses?**  
A: Accuracy depends on document quality, question clarity, and LLM capabilities. The system uses retrieval to ground responses in your documents.

### Authentication & Security

**Q: How long do JWT tokens last?**  
A: JWT tokens expire after 24 hours. Users need to re-login after expiration.

**Q: Can I implement token refresh?**  
A: Yes, you can extend the system to support refresh tokens for better UX. See security recommendations.

**Q: Is my data secure?**  
A: Passwords are hashed with bcrypt, and JWT tokens are signed. For production, use HTTPS and follow security checklist.

### Technical Questions

**Q: Which LLM model is used?**  
A: Google Gemini 3 Flash Preview (`gemini-3-flash-preview`) is used for response generation, with Google Generative AI for embeddings. The system uses Pydantic output parser for structured responses.

**Q: Can I use a different LLM?**  
A: Yes, LangChain supports multiple LLM providers. Modify [llm/chatmodel.py](llm/chatmodel.py) to use OpenAI, Anthropic, etc.

**Q: How is conversation context maintained?**  
A: Conversations are maintained through a dual storage system:
- **PostgreSQL**: All messages stored in Message table with role (user/assistant) and content
- **FAISS Vector Store**: Past Q&A pairs are embedded and stored for semantic retrieval
- When asking new questions, the system retrieves both relevant document chunks (top 20) and relevant past conversations (top 20) to provide comprehensive context
- Chat history is passed in requests and used for contextual understanding

**Q: Can I delete uploaded documents?**  
A: Yes! The `/deletechat` endpoint allows you to delete a chat session along with all associated files (PDFs and FAISS indexes) and conversation history. The system ensures proper ownership verification before deletion.

**Q: What happens if PDF upload fails?**  
A: Files are uploaded first, then processed. If vector store creation fails, files remain but chat is not created. Error message is returned.

### Deployment

**Q: How do I deploy to production?**  
A: Use Docker for containerization, deploy to cloud platforms (AWS, GCP, Azure), use Kubernetes for orchestration. See Docker section.

**Q: What are the system requirements?**  
A: Minimum: 2GB RAM, 2 CPU cores, 10GB disk. Recommended: 4GB+ RAM, 4+ cores, SSD storage.

**Q: Can I use SQLite instead of PostgreSQL?**  
A: Yes, but PostgreSQL is recommended for production. Change DATABASE_URI in [db/database.py](db/database.py).

---

## 🗺️ Roadmap & Future Enhancements

### Planned Features

- [ ] **Document Management**
  - ~~Delete uploaded documents and associated chats~~ ✅ Implemented
  - Update/replace documents in existing chats
  - Support for more document formats (Word, TXT, Markdown)
  - Batch document upload optimization
  
- [ ] **Enhanced Security**
  - Refresh token implementation
  - Rate limiting middleware
  - API key authentication option
  - 2FA (Two-Factor Authentication)
  
- [ ] **User Experience**
  - Pagination for chat history
  - Search within chats
  - Favorite/pin important chats
  - Export conversation history
  
- [ ] **AI Capabilities**
  - Support for multiple LLM providers (OpenAI, Anthropic, etc.)
  - Custom system prompts per chat
  - Streaming responses for real-time feedback
  - Document summarization endpoint
  
- [ ] **Analytics & Monitoring**
  - Dashboard for usage statistics
  - Query performance metrics
  - Cost tracking for API calls
  - Logging and audit trails
  
- [ ] **Collaboration**
  - Share chats with other users
  - Team workspaces
  - Role-based access control (RBAC)
  
- [ ] **Infrastructure**
  - Redis caching for improved performance
  - Background task queue (Celery)
  - Webhook support for notifications
  - GraphQL API option

### Contributing Ideas

Have an idea? [Open an issue](../../issues) or submit a pull request!

---

## 📊 Project Statistics

- **Language**: Python 3.13
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Model**: Google Gemini 3 Flash Preview (`gemini-3-flash-preview`)
- **Embeddings**: Google Generative AI + HuggingFace Sentence Transformers
- **Vector Store**: Dual FAISS system (documents + chat history)
- **Output Format**: Structured with Pydantic parser
- **Architecture**: Modular (Routers, Models, Utils, DB)
- **Security**: JWT + Bcrypt
- **API Style**: RESTful with OpenAPI documentation

---

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure code quality, add appropriate tests, and follow the existing code style.

---

**Note**: This is a production-ready authentication system with JWT tokens and bcrypt password hashing. 

**For Production Deployment:**
- ✅ Replace `JWT_SECRET` with a strong random key
- ✅ Obtain Google Generative AI API key
- ✅ Restrict CORS origins to your frontend domain(s)
- ✅ Use HTTPS with SSL/TLS certificates
- ✅ Change default database credentials
- ✅ Implement rate limiting
- ✅ Set up monitoring and logging
- ✅ Regular security audits and dependency updates
- ✅ Back up your database regularly
- ✅ Use environment variable management service

**Interactive API Documentation:**
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 🙏 Acknowledgments

This project is built with amazing open-source technologies:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://python.langchain.com/) - LLM application framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search by Meta AI
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source database
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and ORM
- [Google Generative AI](https://ai.google.dev/) - AI embeddings and LLM
- [Pydantic](https://docs.pydantic.dev/) - Data validation library

Special thanks to the open-source community for making projects like this possible!

---

## 📧 Support & Contact

- **Issues**: Report bugs or request features via [GitHub Issues](../../issues)
- **Discussions**: Join conversations in [GitHub Discussions](../../discussions)
- **Documentation**: Check [Wiki](../../wiki) for additional guides

---

**Made with ❤️ using FastAPI, LangChain, and Python**

*Last Updated: February 16, 2026*
