import streamlit as st
import requests
import uuid
import json

# Set page configuration
st.set_page_config(page_title="Chat with Steve Jobs' Digital Twin", page_icon="💬", layout="wide")

# Initialize session state for chat history if not exists
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title of the application
st.title("💬 Chat with Steve Jobs' Digital Twin")

# Function to generate a unique message ID
def generate_message_id():
    return str(uuid.uuid4())

# Function to call the first API endpoint
def get_llm_response(user_message, chat_history=None):
    try:
        # Prepare messages with chat history
        messages = []
        
        # Add previous chat history if exists
        if chat_history:
            messages.extend(chat_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare the request payload (OpenAI-compatible format)
        payload = {
            "messages": messages,
            "model": "Llama-3.2-3B-Instruct",
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": True
        }
        
        # Make the API call to the first endpoint
        response = requests.post(
            "https://0xe7f3b9d8c714d9063faac1ad6a169043a19810e7.gaia.domains/v1/chat/completions", 
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            stream=True
        )
        
        # Collect full response
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    # Skip lines that don't start with 'data: '
                    if not line.startswith(b'data: '):
                        continue
                    
                    # Remove 'data: ' prefix
                    json_str = line[6:].decode('utf-8')
                    
                    # Skip [DONE] marker
                    if json_str == '[DONE]':
                        break
                    
                    # Parse the JSON
                    chunk = json.loads(json_str)
                    
                    # Extract content from the chunk
                    if chunk.get('choices') and chunk['choices'][0].get('delta', {}).get('content'):
                        content = chunk['choices'][0]['delta']['content']
                        full_response += content
                except Exception as chunk_error:
                    st.error(f"Error processing chunk: {chunk_error}")
        
        return full_response.strip() if full_response else None
    
    except Exception as e:
        st.error(f"Exception in first API call: {e}")
        return None

# Function to translate to Korean
def translate_to_korean(text):
    try:
        payload = {
            "messages": [
                {"role": "system", "content": "당신은 전문적이고 정확한 번역기입니다. 주어진   텍스트를 한국어로 완벽하게 번역하세요. 절대로 영어나 다른 언어를 사용하지 마세요. 오직 한국어로만 응답해야 합니다."},
                {"role": "user", "content": f"다음   텍스트를 한국어로 번역해 주세요: {text}"}
            ],
            "model": "llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        # Add 'stream' parameter to enable streaming
        params = {
            "stream": True
        }
        
        response = requests.post(
            "https://korean.gaia.domains/v1/chat/completions",
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            params=params
        )
        
        # Extract the translation
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and 'message' in data['choices'][0]:
                return data['choices'][0]['message']['content'].strip()
            else:
                st.error("Invalid API response format")
                return None
        else:
            st.error(f"API request failed: {response.status_code}")
            return None
            
    except json.JSONDecodeError:
        st.error("Empty or invalid JSON response from API")
        return None
    except Exception as e:
        st.error(f"Exception in translation API call: {e}")
        return None

# Prepare chat history for API calls (excluding system messages)
def prepare_chat_history():
    return [
        msg for msg in st.session_state.messages 
        if msg['role'] in ['user', 'assistant'] and 'content' in msg
    ]

# Sidebar for clearing chat history
st.sidebar.title("Chat Options")
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Predefined questions
predefined_questions = [
    "What is the future of technology?",
    "How can I be more innovative?",
    "What was your vision for Apple?",
    "How do you stay motivated?",
    "What advice would you give to young entrepreneurs?"
]

# Display predefined questions as buttons
st.sidebar.title("Quick Start Questions")
for question in predefined_questions:
    if st.sidebar.button(question):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(question)
        
        # Prepare chat history for API call
        chat_history = prepare_chat_history()
        
        # Get LLM response
        with st.spinner("Generating response from our Steve Jobs' agent..."):
            llm_response = get_llm_response(question, chat_history)
        
        # Process and display LLM response
        if llm_response:
            # Display original LLM response
            with st.chat_message("assistant"):
                st.markdown(llm_response, unsafe_allow_html=True)
            
            # Add original response to chat history
            st.session_state.messages.append({"role": "assistant", "content": llm_response})
            
            # Translate to Korean
            with st.spinner("Translating to Korean..."):
                korean_translation = translate_to_korean(llm_response)
            
            # Display Korean translation if successful
            if korean_translation:
                with st.chat_message("assistant"):
                    st.markdown("**In Korean:**")
                    st.markdown(korean_translation, unsafe_allow_html=True)
                
                # Add Korean translation to chat history
                st.session_state.messages.append({"role": "assistant", "content": korean_translation})

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input with a whacky placeholder
if prompt := st.chat_input("What's on your mind, visionary? Think different..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare chat history for API call
    chat_history = prepare_chat_history()
    
    # Get LLM response
    with st.spinner("Generating response from our Steve Jobs' agent..."):
        llm_response = get_llm_response(prompt, chat_history)
    
    # Process and display LLM response
    if llm_response:
        # Display original LLM response
        with st.chat_message("assistant"):
            st.markdown(llm_response, unsafe_allow_html=True)
        
        # Add original response to chat history
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        
        # Translate to Korean
        with st.spinner("Translating to Korean..."):
            korean_translation = translate_to_korean(llm_response)
        
        # Display Korean translation if successful
        if korean_translation:
            with st.chat_message("assistant"):
                st.markdown("**In Korean:**")
                st.markdown(korean_translation, unsafe_allow_html=True)
            
            # Add Korean translation to chat history
            st.session_state.messages.append({"role": "assistant", "content": korean_translation})