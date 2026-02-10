# RAG Backend API

A FastAPI-based backend service for PDF document processing and intelligent Q&A using Retrieval Augmented Generation (RAG) with LangChain and FAISS vector store.

## 📋 Overview

This project provides a REST API that allows users to upload PDF documents, process them into a vector database, and interact with the content through an AI-powered chat interface. The system uses vector similarity search to retrieve relevant document chunks and generates contextual responses using Large Language Models. The API includes a complete authentication system with JWT token-based security, user authorization for chat access, and persistent conversation history storage for each chat session.

## ✨ Features

- **User Authentication**: Complete signup/login system with JWT tokens
- **Password Security**: Bcrypt password hashing and verification
- **Protected Routes**: JWT-based route protection middleware
- **User Authorization**: Chat ownership verification - users can only access their own chats
- **PDF Upload & Processing**: Upload multiple PDF documents in batches
- **Vector Store Integration**: Automatic document embedding using Google Generative AI and FAISS indexing
- **Intelligent Chat**: AI-powered question answering based on uploaded documents
- **Conversation History**: Full message history stored and retrievable for each chat session
- **Multi-Chat Support**: Users can manage multiple chat sessions with different document sets
- **Database Integration**: PostgreSQL database with Users, Chat, and Message tables
- **Transaction Safety**: Database rollback on errors to maintain data integrity
- **CORS Enabled**: Ready for frontend integration
- **Batch Management**: Organized file storage with timestamp-based batch directories
- **Modular Architecture**: Separated routers for auth, chat, and upload operations
- **Health Check Endpoint**: Monitor service status
- **Error Handling**: Comprehensive error handling with detailed error messages

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
├── route/                   # API route handlers (modular routers)
│   ├── auth_route/         # Authentication endpoints
│   │   └── auth_router.py  # Signup and login routes
│   ├── chat_route/         # Chat endpoints
│   │   └── chat_router.py  # Document Q&A routes
│   └── upload_route/       # Upload endpoints
│       └── upload_router.py # PDF upload routes
├── utils/                   # Utility functions
│   ├── hash.py             # Password hashing with bcrypt
│   ├── jwt.py              # JWT token generation and verification
│   └── protectroute.py     # Protected route middleware
├── uploads/                 # PDF storage directory (timestamped batches)
├── main.py                  # FastAPI application and router registration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── .env                     # Environment variables (JWT_SECRET, etc.)
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
   - Create `.env` file with necessary configuration:
     ```
     JWT_SECRET=your-secret-key-change-this-in-production
     JWT_ALGORITHM=HS256
     # Add your Google Generative AI API key
     GOOGLE_API_KEY=your-google-api-key
     ```

### Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📡 API Endpoints

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
  "question": "What is the main topic of the document?"
}
```

**Response**:
```json
{
  "response": "Based on the uploaded documents, the main topic is...",
  "Successful": true
}
```

**Error Response**:
```json
{
  "response": "Chat not found or access denied",
  "Successful": false
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

### Protected Routes

#### 7. Protected Endpoint (Example)
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

#### 8. Root Endpoint
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

#### 9. Health Check
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

- **Framework**: FastAPI
- **Authentication**: JWT (JSON Web Tokens) with PyJWT
- **Password Security**: Bcrypt password hashing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **LLM Integration**: LangChain with Google Generative AI
- **Document Processing**: PyPDF, LangChain Text Splitters
- **Async Support**: asyncpg
- **CORS**: Enabled for frontend integration

## 📦 Key Dependencies

- `fastapi` - Modern web framework for building APIs
- `pyjwt` - JWT token encoding and decoding
- `bcrypt` - Password hashing and verification
- `langchain-google-genai` - Google AI integration
- `langchain-community` - Community integrations for LangChain
- `faiss-cpu` - Vector similarity search
- `pypdf` - PDF document parsing
- `sqlalchemy` - SQL toolkit and ORM
- `asyncpg` - Async PostgreSQL driver
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

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

1. **Signup**: User creates an account via `/signup` endpoint with email and password
2. **Login**: User authenticates via `/login` and receives a JWT token (24-hour expiration)
3. **Upload**: User uploads PDF files via `/upload-pdfs` endpoint (requires JWT token)
4. **Processing**: 
   - PDFs are saved in timestamped batch directories (e.g., `uploads/20260210_223829/`)
   - A new Chat record is created in the database with the first PDF filename as chat name
   - Documents are embedded using Google Generative AI embeddings
   - FAISS vector store index is created and saved in batch's `faiss_index` subdirectory
5. **Get Chats**: User retrieves their chat sessions via `/getchat` endpoint
6. **Query**: User sends questions via `/chat` endpoint with chat_id (requires JWT token)
7. **Security Check**: System verifies the chat belongs to the authenticated user
8. **Message Storage**: User's question is stored in Message table with role="user"
9. **Retrieval**: Relevant document chunks are retrieved from the chat's FAISS vector store
10. **Generation**: LLM generates contextual response based on retrieved content
11. **Response Storage**: System's answer is stored in Message table with role="system"
12. **Response**: Answer is returned to user
13. **History**: User can retrieve full conversation history via `/getchatconversation` endpoint

## 🔒 Security Features & Notes

### Implemented Security Features
- **Password Hashing**: Passwords are hashed using bcrypt with salt before storage
- **JWT Authentication**: Token-based authentication with 24-hour expiration
- **Protected Routes**: Middleware validates JWT tokens on protected endpoints
- **User Authorization**: Chat ownership verification prevents unauthorized access to other users' chats
- **Database Transactions**: Rollback support on errors to prevent partial updates
- **Email Validation**: Prevents duplicate user registration
- **Query Parameter Validation**: Pydantic models ensure proper data types

### Production Security Recommendations
- **CORS**: Currently allows all origins (`*`) - restrict this in production to specific domains
- **JWT Secret**: Change `JWT_SECRET` in `.env` to a strong, randomly generated key
- **Database Credentials**: Store all sensitive credentials in environment variables
- **HTTPS**: Use HTTPS in production to encrypt data in transit
- **Rate Limiting**: Implement rate limiting on authentication and upload endpoints
- **Input Validation**: Enhanced validation for file uploads and user inputs
- **File Upload Limits**: Configure maximum file size and number of files per upload
- **Token Refresh**: Consider implementing refresh tokens for better UX
- **Password Requirements**: Enforce strong password policies (length, complexity)
- **SQL Injection Protection**: SQLAlchemy ORM provides protection, but validate all inputs
- **Path Traversal Protection**: Validate file paths to prevent directory traversal attacks

## 🐳 Docker Support

A Dockerfile is included for containerized deployment.

## � Authentication Flow

1. User signs up with email, username, and password
2. Password is hashed with bcrypt and stored securely
3. User logs in with email and password
4. System validates credentials and generates JWT token (expires in 24 hours)
5. Client includes token in Authorization header: `Bearer <token>`
6. Protected routes verify token and extract user information
7. Chat routes additionally verify that the requested chat belongs to the authenticated user
8. Invalid or expired tokens return 401 Unauthorized
9. Unauthorized chat access attempts return error message
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
```
## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please ensure code quality and add appropriate tests.

---

**Note**: This project includes a production-ready authentication system with JWT and bcrypt. For production deployment, ensure proper security configurations (JWT_SECRET, HTTPS, CORS restrictions), environment variable management, error handling, and regular security audits.