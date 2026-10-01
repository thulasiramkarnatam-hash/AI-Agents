"""
Streamlit frontend for OpenAI Chat XML Backend
Simple chat interface that formats messages as XML and sends to backend
"""
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="OpenAI Chat XML Frontend",
    page_icon="💬",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .message-bubble {
        border-radius: 18px;
        padding: 12px 18px;
        margin: 8px 0;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border: 1px solid #9c27b0;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def format_xml_message(role: str, content: str) -> str:
    """Format a single chat message as XML string"""
    return f"""<conversation>
    <message>
        <role>{role}</role>
        <content>{content}</content>
    </message>
</conversation>"""

def parse_conversation_xml(xml_text: str) -> List[Dict[str, str]]:
    """Parse XML and return list of message dictionaries"""
    messages = []
    try:
        root = ET.fromstring(xml_text)
        for message_elem in root.findall('message'):
            role_elem = message_elem.find('role')
            content_elem = message_elem.find('content')
            if role_elem is not None and content_elem is not None:
                messages.append({
                    "role": role_elem.text or "",
                    "content": content_elem.text or ""
                })
    except ET.ParseError:
        pass
    return messages

def check_backend() -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def send_message_to_backend(message: str) -> Dict[str, Any]:
    """Send user message wrapped in XML to backend"""
    xml_input = format_xml_message("user", message)
    try:
        response = requests.post(
            f"{API_URL}/chat/xml",
            json={"xml_input": xml_input},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_messages():
    """Display chat messages"""
    for i, msg in enumerate(st.session_state["messages"]):
        msg_class = "user-message" if msg["role"] == "user" else "assistant-message"
        role_display = "👤 You" if msg["role"] == "user" else "🤖 Assistant"
        st.markdown(f"""
        <div class="message-bubble {msg_class}">
            <strong>{role_display}:</strong><br>
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("💬 OpenAI Chat")
    st.markdown("Simple chat with XML data format and in-memory history (last 5 messages)")

    # Display chat messages
    if st.session_state["messages"]:
        st.subheader("Conversation")
        display_messages()
    else:
        st.info("👋 Start the conversation below!")

    # Input section
    st.subheader("Send a Message")

    message = st.text_input(
        "Type your message here:",
        placeholder="Hello! How can I help you today?"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        send_btn = st.button("🚀 Send", type="primary", disabled=not message.strip())

    with col2:
        if st.button("🗑️ Clear Chat"):
            try:
                requests.post(f"{API_URL}/conversation/clear")
                st.session_state["messages"] = []
                st.rerun()
            except:
                st.session_state["messages"] = []
                st.rerun()

    # Handle send button click
    if send_btn and message.strip():
        # Add user message to local state
        st.session_state["messages"].append({"role": "user", "content": message})
        st.rerun()

    # XML input section (raw XML mode)
    st.subheader("📝 Raw XML Input")
    st.markdown("Or enter conversation directly as XML:")

    xml_input = st.text_area(
        "XML Conversation:",
        height=120,
        placeholder="""<conversation>
    <message>
        <role>user</role>
        <content>Hello, how are you?</content>
    </message>
</conversation>"""
    )

    if st.button("📤 Send XML", disabled=not xml_input.strip()):
        with st.spinner("Sending..."):
            result = send_message_to_backend(xml_input)

            if result.get("success"):
                # Update local messages with backend response
                response = result.get("response", "")
                st.session_state["messages"].append({"role": "assistant", "content": response})

                # Display response
                st.success("✅ Message processed successfully!")
                st.markdown(f"""
                <div class="message-bubble assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {response}
                </div>
                """, unsafe_allow_html=True)

                # Show XML
                st.subheader("Response XML")
                st.code(result.get("response_xml", ""), language="xml")

                # Show conversation history
                st.subheader("Backend Conversation History")
                history = result.get("conversation_history", [])
                if history:
                    history_xml = "\n".join(
                        [f"<message><role>{m['role']}</role><content>{m['content']}</content></message>" for m in history]
                    )
                    st.code(f"<conversation>\n{history_xml}\n</conversation>", language="xml")
                st.info(f"Backend stores last 5 messages in memory")
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666;">
            <small>Frontend: Streamlit | Backend: FastAPI | Data Format: XML | Storage: In-memory (5 messages)</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
