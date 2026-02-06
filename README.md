# RAG Backend API

A FastAPI-based backend service for PDF document processing and intelligent Q&A using Retrieval Augmented Generation (RAG) with LangChain and FAISS vector store.

## 📋 Overview

This project provides a REST API that allows users to upload PDF documents, process them into a vector database, and interact with the content through an AI-powered chat interface. The system uses vector similarity search to retrieve relevant document chunks and generates contextual responses using Large Language Models. The API includes a complete authentication system with JWT token-based security.

## ✨ Features

- **User Authentication**: Complete signup/login system with JWT tokens
- **Password Security**: Bcrypt password hashing and verification
- **Protected Routes**: JWT-based route protection middleware
- **PDF Upload & Processing**: Upload multiple PDF documents in batches
- **Vector Store Integration**: Automatic document embedding and FAISS indexing
- **Intelligent Chat**: AI-powered question answering based on uploaded documents
- **Database Integration**: PostgreSQL database for user and chat management
- **CORS Enabled**: Ready for frontend integration
- **Batch Management**: Organized file storage with timestamp-based batch directories
- **Modular Architecture**: Separated routers for auth, chat, and upload operations
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
│   └── routeprotect.py     # Protected route middleware
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

#### 4. Chat with Documents
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

### Protected Routes

#### 5. Protected Endpoint (Example)
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

#### 6. Root Endpoint
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

#### 7. Health Check
```http
GET /health
```
Returns service health status.

**Response**:
```json
{
  "health": "okay"
}

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

### Chat Table
- `chat_id` (Integer, Primary Key, Auto-increment)
- `chat_name` (String) - Chat session identifier

## 🔄 Workflow

1. **Signup**: User creates an account via `/signup` endpoint with email and password
2. **Login**: User authenticates via `/login` and receives a JWT token (24-hour expiration)
3. **Upload**: User uploads PDF files via `/upload-pdfs` endpoint (with JWT token)
4. **Processing**: PDFs are saved in timestamped batch directories
5. **Indexing**: Documents are processed and embedded into FAISS vector store
6. **Query**: User sends questions via `/chat` endpoint (with JWT token)
7. **Retrieval**: Relevant document chunks are retrieved from vector store
8. **Generation**: LLM generates contextual response based on retrieved content
9. **Response**: Answer is returned to user

## 🔒 Security Features & Notes

### Implemented Security Features
- **Password Hashing**: Passwords are hashed using bcrypt with salt before storage
- **JWT Authentication**: Token-based authentication with 24-hour expiration
- **Protected Routes**: Middleware validates JWT tokens on protected endpoints
- **Email Validation**: Prevents duplicate user registration

### Production Security Recommendations
- **CORS**: Currently allows all origins (`*`) - restrict this in production to specific domains
- **JWT Secret**: Change `JWT_SECRET` in `.env` to a strong, randomly generated key
- **Database Credentials**: Store all sensitive credentials in environment variables
- **HTTPS**: Use HTTPS in production to encrypt data in transit
- **Rate Limiting**: Implement rate limiting on authentication endpoints
- **Input Validation**: Enhanced validation for file uploads and user inputs
- **Token Refresh**: Consider implementing refresh tokens for better UX
- **Password Requirements**: Enforce strong password policies (length, complexity)

## 🐳 Docker Support

A Dockerfile is included for containerized deployment.

## � Authentication Flow

1. User signs up with email, username, and password
2. Password is hashed with bcrypt and stored securely
3. User logs in with email and password
4. System validates credentials and generates JWT token (expires in 24 hours)
5. Client includes token in Authorization header: `Bearer <token>`
6. Protected routes verify token and extract user information
7. Invalid or expired tokens return 401 Unauthorized
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

# 4. Upload PDFs (if protected)
curl -X POST http://localhost:8000/upload-pdfs \
  -H "Authorization: Bearer eyJhbG..." \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"

# 5. Chat with documents
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbG..." \
  -d '{
    "chat_id": "20260205_143022",
    "query": "What is the main topic?"
  }'
```
## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please ensure code quality and add appropriate tests.

---

**Note**: This project includes a production-ready authentication system with JWT and bcrypt. For production deployment, ensure proper security configurations (JWT_SECRET, HTTPS, CORS restrictions), environment variable management, error handling, and regular security audits.