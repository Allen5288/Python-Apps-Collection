# Medical AI Assistant Client

A Streamlit-based frontend client for the Medical AI Assistant that provides an intuitive interface for uploading medical documents and asking questions using RAG (Retrieval-Augmented Generation).

## 🎯 Features

- **Document Upload**: Upload multiple PDF medical documents
- **Interactive Chat**: Ask questions about uploaded documents
- **Real-time Responses**: Get AI-powered answers based on document content
- **Clean UI**: Modern Streamlit interface with intuitive design
- **File Management**: View and manage uploaded documents
- **Error Handling**: User-friendly error messages and validation

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **HTTP Client**: Requests
- **File Processing**: PDF handling
- **UI Components**: Streamlit widgets and components

## 📋 Requirements

- Python 3.8+
- Running Medical AI Assistant Server (backend)
- Internet connection for API calls

## 🚀 Installation

1. **Navigate to client directory**

```bash
cd client
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure server connection**
Check `config.py` and ensure it points to your running server:

```python
API_URL = "http://localhost:8000"  # Default server URL
```

## 🏃‍♂️ Running the Client

1. **Start the backend server first**

```bash
# In the server directory
cd ../server
uvicorn main:app --reload
```

2. **Launch the Streamlit app**

```bash
# In the client directory
streamlit run app.py
```

3. **Access the application**
Open your browser and go to: `http://localhost:8501`

## 📱 Using the Application

### 1. Upload Documents

- Click on the file uploader in the sidebar
- Select one or more PDF files
- Click "Upload PDFs" to process documents
- Wait for confirmation message

### 2. Ask Questions

- Type your medical question in the text input
- Click "Ask Question" or press Enter
- View the AI-generated response
- Ask follow-up questions as needed

### 3. Example Questions

- "What are the symptoms of diabetes?"
- "How is hypertension treated?"
- "What medications are recommended for asthma?"
- "Explain the side effects of this medication"

## 🏗️ Project Structure

```
client/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── utils/
│   ├── __init__.py
│   ├── api.py            # API client functions
│   └── helpers.py        # Helper functions
├── components/
│   ├── __init__.py
│   ├── sidebar.py        # Sidebar components
│   └── chat.py           # Chat interface components
└── static/
    ├── style.css         # Custom CSS styles
    └── images/           # Application images
```

## 🔧 Configuration

### API Settings

Edit `config.py` to configure the backend server:

```python
# Server configuration
API_URL = "http://localhost:8000"  # Backend server URL
TIMEOUT = 30                       # Request timeout in seconds
MAX_FILE_SIZE = 10                 # Max file size in MB
ALLOWED_EXTENSIONS = ['.pdf']      # Allowed file types
```

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[server]
port = 8501
headless = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 📡 API Integration

The client communicates with the backend through these endpoints:

### Upload PDFs

```python
def upload_pdfs_api(files):
    files_payload = [("files", (f.name, f.read(), "application/pdf")) for f in files]
    return requests.post(f"{API_URL}/upload_pdfs/", files=files_payload)
```

### Ask Questions

```python
def ask_question(question):
    return requests.post(f"{API_URL}/ask/", data={"question": question})
```

## 🎨 User Interface

### Main Features

- **Sidebar**: Document upload and file management
- **Main Area**: Chat interface for questions and answers
- **Header**: Application title and navigation
- **Footer**: Status information and help

### Components

- **File Uploader**: Multi-file PDF selection
- **Chat Interface**: Question input and response display
- **Status Messages**: Success/error notifications
- **Loading Indicators**: Progress feedback

## 🚨 Error Handling

The client handles various error scenarios:

- **Server Connection**: Network connectivity issues
- **File Upload**: Invalid file types or sizes
- **API Errors**: Backend server errors
- **Timeout**: Request timeout handling
- **Validation**: Input validation and sanitization

## 🧪 Testing

### Manual Testing

1. **Upload Test**: Try uploading various PDF files
2. **Question Test**: Ask different types of questions
3. **Error Test**: Test with invalid inputs
4. **Performance Test**: Test with large files

### Test Commands

```bash
# Run the client
streamlit run app.py

# Test API endpoints
python -c "from utils.api import *; print('API functions loaded')"
```

## 🔐 Security Considerations

- **File Validation**: Only PDF files are accepted
- **Input Sanitization**: User inputs are validated
- **API Security**: Secure communication with backend
- **Error Messages**: No sensitive information in error messages

## 📊 Performance Tips

- **File Size**: Keep PDF files under 10MB for optimal performance
- **Concurrent Users**: Streamlit handles multiple users efficiently
- **Caching**: Use Streamlit caching for repeated operations
- **Network**: Ensure stable connection to backend server

## 🚀 Deployment

### Local Development

```bash
streamlit run app.py
```

### Production Deployment

```bash
# Using Docker
docker build -t medical-ai-client .
docker run -p 8501:8501 medical-ai-client

# Using Streamlit Cloud
# Push to GitHub and deploy via Streamlit Cloud
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Not Running**
   - Error: Connection refused
   - Solution: Start the backend server first

2. **File Upload Failed**
   - Error: 422 Unprocessable Entity
   - Solution: Check file format and size

3. **No Response to Questions**
   - Error: Empty response
   - Solution: Ensure documents are uploaded first

4. **Slow Performance**
   - Issue: Long response times
   - Solution: Check network connection and server performance

## 📄 Requirements

```
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.0.0
```

**Note**: Make sure the backend server is running before starting the client application.
