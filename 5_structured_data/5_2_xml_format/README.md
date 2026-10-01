# OpenAI Chat XML Format Backend

A simple chat system using XML formatting for structured data exchange between a Streamlit frontend and a FastAPI backend.

## 📁 Project Structure

```
5_2_xml_format/
├── backend/
│   ├── app.py                 # FastAPI backend with XML handling
│   ├── main.py                # Original XML chat logic (backup/reference)
│   └── requirements.txt       # Python dependencies for backend
├── frontend/
│   └── app.py                 # Streamlit frontend with chat interface
├── .env.example               # Example environment variables
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## 🏗️ Architecture

```
User Interface (Streamlit) ↔ API Layer (FastAPI) ↔ OpenAI Service ↔ XML Format ↔ Conversation Memory
```

## 🚀 Quick Start

### 1. Clone / Navigate to Project

```bash
cd D:\AI-Agents\5_structured_data\5_2_xml_format
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
pip install streamlit requests
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

### 4. Start the Backend Server

```bash
cd backend
uvicorn app:app --reload
```

Backend API will be available at: `http://localhost:8000`

### 5. Start the Frontend

```bash
cd frontend
streamlit run app.py
```

Frontend web interface will be available at: `http://localhost:8501`

## 🌐 API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | Health check | Returns service status |
| `POST` | `/chat/xml` | Send XML, get OpenAI response | `{ "xml_input": "<conversation>..." }` |
| `GET` | `/conversation/xml` | Get current conversation as XML | Returns last 5 messages |
| `POST` | `/conversation/clear` | Clear conversation history | Resets in-memory storage |
| `GET` | `/health` | Detailed health check | Status + message count |

### Request/Response Examples

**Request (POST /chat/xml):**
```json
{
  "xml_input": "<conversation>\n    <message>\n        <role>user</role>\n        <content>Hello, how are you?</content>\n    </message>\n</conversation>"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response": "I'm doing well! How can I help you today?",
  "response_xml": "<message><role>assistant</role><content>I'm doing well! How can I help you today?</content></message>",
  "conversation_history": [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well! How can I help you today?"}
  ]
}
```

**Get Conversation XML:**
```json
{
  "xml": "<conversation>\n    <message>\n        <role>user</role>\n        <content>Hello</content>\n    </message>\n    <message>\n        <role>assistant</role>\n        <content>Hi there!</content>\n    </message>\n</conversation>"
}
```

## 💬 Usage

### Simple Chat Mode

1. Open frontend at `http://localhost:8501`
2. Type a message in the text input
3. Click "Send" button
4. View the XML-formatted exchange
5. Assistant response appears with bubble styling

### Raw XML Mode

1. Navigate to "📝 Raw XML Input" section
2. Enter complete conversation as XML
3. Click "Send XML" button
4. View response and full conversation history

### Conversation Management

- **Messages are stored in-memory** (not persisted to disk)
- **Automatic limit**: Only last 5 messages retained
- **Clear chat**: Use "🗑️ Clear Chat" button or `POST /conversation/clear`
- **Reset**: Restart the application to clear all memory

### Example XML Format

```xml
<conversation>
    <message>
        <role>user</role>
        <content>Hello, how are you?</content>
    </message>
    <message>
        <role>assistant</role>
        <content>I'm doing well! How can I help you today?</content>
    </message>
    <message>
        <role>user</role>
        <content>Can you help me with Python?</content>
    </message>
</conversation>
```

## 🛠️ Technical Details

### Backend (`backend/app.py`)

- **Framework**: FastAPI (modern, fast web framework)
- **XML Handling**: Uses `xml.etree.ElementTree` for parsing/formatting
- **Chat Memory**: In-memory `ConversationHistory` class with max 5 messages
- **OpenAI Integration**: Uses `openai` Python library with gpt-3.5-turbo
- **CORS**: Enabled for cross-origin frontend communication
- **Error Handling**: Comprehensive try/except blocks with informative messages

### Frontend (`frontend/app.py`)

- **Framework**: Streamlit (easy Python web apps)
- **XML Parsing**: Uses `xml.etree.ElementTree` for consistency with backend
- **State Management**: Uses `st.session_state` for conversation persistence
- **Styling**: Custom CSS for message bubbles and layout
- **Responsive**: Centered layout with sidebar controls

### Data Format

**XML Schema:**
```xml
<conversation>
    <!-- Root element wrapping all messages -->
    <message>
        <!-- Individual message element -->
        <role>user|assistant</role>
        <!-- Message role (required) -->
        <content>Message text content</content>
        <!-- Message content (required) -->
    </message>
    <!-- Additional messages... -->
</conversation>
```

### Conversation Memory

- **Storage Type**: In-memory Python list
- **Capacity**: Exactly 5 messages maximum
- **Behavior**: FIFO (First-In-First-Out) - oldest messages discarded when limit exceeded
- **Persistence**: Lost on application restart
- **Thread Safety**: Single-process, not designed for concurrent access

## 📦 Dependencies

### Backend (`backend/requirements.txt`)

```
fastapi>=0.100.0      # Web framework
uvicorn>=0.23.0       # ASGI server
openai>=1.0.0         # OpenAI API client
python-dotenv>=1.0.0  # Environment variable loading
```

### Frontend (installed via pip)

```
streamlit             # Web interface framework
requests              # HTTP client for API calls
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```
OPENAI_API_KEY=your-openai-api-key-here
```

- Required: OpenAI API key for chat completions
- Optional: Can customize other settings in code

### Customization Options

**Backend (`backend/app.py`):**
- Change model: Edit `model="gpt-3.5-turbo"` line
- Adjust temperature: Modify `temperature=0.7` parameter
- Change message limit: Modify `ConversationHistory(max_messages=5)` 
- Add system prompts: Modify `get_chat_response()` method

**Frontend (`frontend/app.py`):**
- Change API URL: Edit `API_URL = "http://localhost:8000"`
- Customize colors: Modify CSS in `st.markdown()` call
- Adjust timeout: Change `timeout=30` in API calls

## 🐛 Known Issues / Diagnostics

Some linting warnings that are non-critical:

1. **Import resolution** - Pylance may not detect installed packages in analysis environment, but imports work at runtime
2. **Variable access** - Minor code style issue in XML formatting that doesn't affect functionality

## 🔄 Data Flow Example

```
User Types "Hello!"
     ↓
Frontend wraps as XML: <conversation><message><role>user</role><content>Hello!</content></message></conversation>
     ↓
POST /chat/xml → FastAPI backend
     ↓
Backend parses XML → Adds to conversation history (keep last 5)
     ↓
Backend sends to OpenAI gpt-3.5-turbo with conversation context
     ↓
OpenAI returns response
     ↓
Backend formats response as XML
     ↓
POST response returned to frontend
     ↓
Frontend displays message bubbles
     ↓
Conversation history updated (5 messages max)
```

## 📄 License

This project is for educational and demonstration purposes. Feel free to modify and use as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- Check the `.env.example` for required configuration
- Ensure OpenAI API key is valid and has sufficient quota
- Review API endpoints at `http://localhost:8000/docs` (auto-generated FastAPI docs)
- Check console output for any runtime errors

---

**Built with FastAPI, Streamlit, and OpenAI**  
**Data Format: XML**  
**Conversation Memory: Last 5 messages in RAM**