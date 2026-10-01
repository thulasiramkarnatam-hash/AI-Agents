from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = FastAPI(title="OpenAI Chat XML Backend")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class ChatMessage:
    role: str
    content: str

class ConversationHistory:
    """In-memory conversation history with max 5 messages"""
    def __init__(self, max_messages: int = 5):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str):
        """Add message and trim to max size"""
        self.messages.append(ChatMessage(role, content))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_messages(self) -> List[ChatMessage]:
        return self.messages.copy()

    def clear(self):
        self.messages.clear()

    def to_dict_list(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

class XMLChatFormatter:
    """Handles XML formatting and parsing for chat messages"""

    @staticmethod
    def format_message_xml(role: str, content: str) -> str:
        return f"<message><role>{role}</role><content>{content}</content></message>"

    @staticmethod
    def parse_message_xml(xml_string: str) -> Dict[str, str]:
        try:
            root = ET.fromstring(xml_string)
            role = root.find('role').text if root.find('role') is not None else ''
            content = root.find('content').text if root.find('content') is not None else ''
            return {"role": role, "content": content}
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

    @staticmethod
    def format_conversation_xml(messages: List[ChatMessage]) -> str:
        xml_parts = ['<conversation>']
        for msg in messages:
            xml_parts.append(XMLChatFormatter.format_message_xml(msg.role, msg.content))
        xml_parts.append('</conversation>')
        return '\n'.join(xml_parts)

    @staticmethod
    def parse_conversation_xml(xml_string: str) -> List[Dict[str, str]]:
        try:
            root = ET.fromstring(xml_string)
            messages = []
            for message_elem in root.findall('message'):
                role_elem = message_elem.find('role')
                content_elem = message_elem.find('content')
                if role_elem is not None and content_elem is not None:
                    messages.append({
                        "role": role_elem.text or "",
                        "content": content_elem.text or ""
                    })
            return messages
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

class OpenAIChatService:
    """Service for handling OpenAI chat completions"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = ConversationHistory(max_messages=5)
        self.xml_formatter = XMLChatFormatter()

    def add_user_message(self, role: str, content: str):
        self.conversation_history.add_message(role, content)

    def get_chat_response(self, system_prompt: str = "You are a helpful assistant.") -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history.to_dict_list())

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            assistant_response = response.choices[0].message.content
            self.conversation_history.add_message("assistant", assistant_response)
            return assistant_response
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def process_xml_input(self, xml_input: str) -> Dict[str, Any]:
        try:
            parsed_messages = self.xml_formatter.parse_conversation_xml(xml_input)
            # Add parsed messages to existing history (accumulate, keep last 5)
            for msg in parsed_messages:
                self.conversation_history.add_message(msg["role"], msg["content"])

            response = self.get_chat_response()
            response_xml = self.xml_formatter.format_message_xml("assistant", response)

            return {
                "success": True,
                "response": response,
                "response_xml": response_xml,
                "conversation_history": self.conversation_history.to_dict_list()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_conversation_xml(self) -> str:
        return self.xml_formatter.format_conversation_xml(self.conversation_history.get_messages())

# Initialize service
chat_service = OpenAIChatService()

@app.get("/")
async def root():
    return {"message": "OpenAI Chat XML Backend is running"}

@app.post("/chat/xml")
async def chat_with_xml(request_data: dict):
    """Accept JSON body with xml_input field and return XML-formatted response"""
    xml_input = request_data.get("xml_input", "")
    if not xml_input.strip():
        raise HTTPException(status_code=400, detail="xml_input field is required")
    result = chat_service.process_xml_input(xml_input)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/conversation/xml")
async def get_conversation_xml():
    """Get current conversation history as XML"""
    return {"xml": chat_service.get_conversation_xml()}

@app.post("/conversation/clear")
async def clear_conversation():
    """Clear conversation history"""
    chat_service.conversation_history.clear()
    return {"message": "Conversation history cleared"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message_count": len(chat_service.conversation_history.messages)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)