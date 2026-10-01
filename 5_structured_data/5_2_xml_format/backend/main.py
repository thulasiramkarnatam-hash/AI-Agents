import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import openai
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ChatMessage:
    role: str
    content: str

class ConversationHistory:
    def __init__(self, max_messages: int = 5):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str):
        """Add a message to conversation history, maintaining max size"""
        self.messages.append(ChatMessage(role, content))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_messages(self) -> List[ChatMessage]:
        """Get all messages in conversation history"""
        return self.messages.copy()

    def clear(self):
        """Clear conversation history"""
        self.messages.clear()

    def to_dict_list(self) -> List[Dict[str, str]]:
        """Convert to list of dictionaries for OpenAI API"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

class XMLChatFormatter:
    """Handles XML formatting and parsing for chat messages"""

    @staticmethod
    def format_message_xml(role: str, content: str) -> str:
        """Format a single chat message as XML"""
        return f"<message><role>{role}</role><content>{content}</content></message>"

    @staticmethod
    def parse_message_xml(xml_string: str) -> Dict[str, str]:
        """Parse a single chat message from XML"""
        try:
            root = ET.fromstring(xml_string)
            role = root.find('role').text if root.find('role') is not None else ''
            content = root.find('content').text if root.find('content') is not None else ''
            return {"role": role, "content": content}
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")

    @staticmethod
    def format_conversation_xml(messages: List[ChatMessage]) -> str:
        """Format entire conversation as XML"""
        xml_parts = ['<conversation>']
        for msg in messages:
            xml_parts.append(XMLChatFormatter.format_message_xml(msg.role, msg.content))
        xml_parts.append('</conversation>')
        return '\n'.join(xml_parts)

    @staticmethod
    def parse_conversation_xml(xml_string: str) -> List[Dict[str, str]]:
        """Parse entire conversation from XML"""
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
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = ConversationHistory(max_messages=5)
        self.xml_formatter = XMLChatFormatter()

    def add_user_message(self, role: str, content: str):
        """Add a user message to conversation history"""
        self.conversation_history.add_message(role, content)

    def get_chat_response(self, system_prompt: str = "You are a helpful assistant.") -> str:
        """Get chat response from OpenAI"""
        # Prepare messages for OpenAI API
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

            # Add assistant response to conversation history
            self.conversation_history.add_message("assistant", assistant_response)

            return assistant_response
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def process_xml_input(self, xml_input: str) -> Dict[str, Any]:
        """Process XML input and return formatted response"""
        try:
            # Parse XML input
            parsed_messages = self.xml_formatter.parse_conversation_xml(xml_input)

            # Clear existing history and add parsed messages
            self.conversation_history.clear()
            for msg in parsed_messages:
                self.conversation_history.add_message(msg["role"], msg["content"])

            # Get response from OpenAI
            response = self.get_chat_response()

            # Format response as XML
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
        """Get current conversation history as XML"""
        return self.xml_formatter.format_conversation_xml(self.conversation_history.get_messages())

# Example usage
if __name__ == "__main__":
    # This would be used in the actual application
    service = OpenAIChatService()

    # Example XML input
    example_xml = """<conversation>
        <message>
            <role>user</role>
            <content>Hello, how are you?</content>
        </message>
        <message>
            <role>assistant</role>
            <content>I'm doing well, thank you! How can I help you today?</content>
        </message>
    </conversation>"""

    # Process the example
    result = service.process_xml_input(example_xml)
    print(result)