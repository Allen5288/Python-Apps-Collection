# Medical AI Assistant Server

A FastAPI-based backend server for a medical AI assistant that uses RAG (Retrieval-Augmented Generation) to answer medical questions based on uploaded PDF documents.

## 🏗️ Architecture

```
PDF Documents → Text Extraction → Chunking → Embeddings → Vector Store (Pinecone)
                                                                     ↓
User Query → Query Embedding → Similarity Search → Context Retrieval → LLM (Groq) → Response
```

## 🚀 Features

- **PDF Document Processing**: Upload and process medical PDFs
- **Vector Storage**: Store document embeddings in Pinecone for fast retrieval
- **RAG Pipeline**: Retrieve relevant context and generate responses using LLaMA 3
- **RESTful API**: FastAPI endpoints for document upload and question answering
- **Error Handling**: Comprehensive error handling and logging

## 📋 Requirements

- Python 3.8+
- Pinecone account and API key
- Google AI Studio API key
- Groq API key

## 🛠️ Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd server
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the server directory:

```properties
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

4. **Get API Keys**
   - **Google AI Studio**: Visit [Google AI Studio](https://aistudio.google.com/) → Get API key
   - **Groq**: Visit [Groq Console](https://console.groq.com/) → Create API key
   - **Pinecone**: Visit [Pinecone](https://www.pinecone.io/) → Sign up → Get API key

## 🏃‍♂️ Running the Server

1. **Start the development server**

```bash
uvicorn main:app --reload
```

2. **Access the API**
   - Server: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - OpenAPI JSON: `http://localhost:8000/openapi.json`

## 📡 API Endpoints

### 1. Upload PDFs

**POST** `/upload_pdfs/`

Upload medical PDF documents to be processed and stored in the vector database.

```bash
curl -X POST "http://localhost:8000/upload_pdfs/" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@medical_document.pdf"
```

**Response:**

```json
{
  "message": "PDFs uploaded and processed successfully"
}
```

### 2. Ask Questions

**POST** `/ask/`

Ask questions about the uploaded medical documents.

```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the symptoms of diabetes?"}'
```

**Response:**

```json
{
  "answer": "Based on the uploaded medical documents, the symptoms of diabetes include...",
  "sources": ["document1.pdf", "document2.pdf"]
}
```

## 🏗️ Project Structure

```
server/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── uploaded_docs/         # Directory for uploaded PDFs
├── modules/
│   ├── __init__.py
│   ├── load_vectorstore.py    # PDF processing and vector storage
│   └── query_engine.py        # RAG query processing
├── routes/
│   ├── __init__.py
│   ├── upload_pdfs.py         # PDF upload endpoint
│   └── ask_question.py        # Question answering endpoint
├── middlewares/
│   ├── __init__.py
│   └── exception_handlers.py  # Error handling middleware
└── logger.py                  # Logging configuration
```

## 🔧 Configuration

### Vector Database (Pinecone)

- **Index Name**: `medical-index`
- **Dimension**: 768 (Google Generative AI embeddings)
- **Metric**: `dotproduct`
- **Cloud**: AWS
- **Region**: `us-east-1`

### Text Processing

- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters
- **Embedding Model**: `models/embedding-001` (Google)

### LLM Configuration

- **Provider**: Groq
- **Model**: LLaMA 3 70B
- **Use Case**: Medical question answering with RAG

## 🚨 Error Handling

The server includes comprehensive error handling:

- File upload validation
- PDF processing errors
- Vector database connection issues
- LLM API failures
- Custom exception middleware

## 📊 Monitoring & Logging

- Structured logging with Python's `logging` module
- Request/response logging
- Error tracking and debugging
- Performance monitoring

## 🔐 Security Notes

- **API Keys**: Never commit API keys to version control
- **File Uploads**: Validate file types and sizes
- **CORS**: Configure appropriately for production
- **Rate Limiting**: Consider implementing rate limiting for production

## 🧪 Testing

```bash
# Run the server
uvicorn main:app --reload

# Test PDF upload
curl -X POST "http://localhost:8000/upload_pdfs/" \
  -F "files=@test_document.pdf"

# Test question answering
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 🚀 Deployment

For production deployment:

1. **Environment Variables**: Set production API keys
2. **Database**: Consider PostgreSQL for metadata storage
3. **Caching**: Implement Redis for query caching
4. **Monitoring**: Add application monitoring (e.g., Sentry)
5. **Load Balancing**: Use reverse proxy (e.g., Nginx)

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs for debugging information
