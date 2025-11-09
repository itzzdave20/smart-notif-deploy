import streamlit as st
from datetime import datetime
from ai_features import AIFeatures

def show_ai_chatbot(role: str = "student"):
    """Show AI Chatbot interface"""
    st.header("🤖 AI Chatbot Assistant")
    st.caption("Ask me anything! I can help with assignments, classes, attendance, and more.")
    
    # Initialize conversation history in session state
    if f'{role}_chat_history' not in st.session_state:
        st.session_state[f'{role}_chat_history'] = []
    
    # Initialize AI features
    if 'ai_features' not in st.session_state:
        st.session_state.ai_features = AIFeatures()
    
    ai = st.session_state.ai_features
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state[f'{role}_chat_history']:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    if 'timestamp' in message:
                        st.caption(f"Response time: {message.get('timestamp', '')}")
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state[f'{role}_chat_history'].append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response
        with st.spinner("Thinking..."):
            conversation_history = [
                {'role': msg['role'], 'content': msg['content']} 
                for msg in st.session_state[f'{role}_chat_history'][-10:]  # Last 10 messages for context
            ]
            
            ai_response = ai.chat_with_ai(user_input, conversation_history)
            
            # Add AI response to history
            st.session_state[f'{role}_chat_history'].append({
                'role': 'assistant',
                'content': ai_response['response'],
                'timestamp': ai_response.get('timestamp', datetime.now().isoformat())
            })
        
        # Rerun to show new messages
        st.rerun()
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### Chat Controls")
        if st.button("🗑️ Clear Chat History", key=f"clear_chat_{role}"):
            st.session_state[f'{role}_chat_history'] = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.info("""
        **I can help you with:**
        - 📝 Assignment help and tips
        - 📚 Class information
        - ✅ Attendance questions
        - ❓ General inquiries
        
        Just ask me anything!
        """)
        
        # Show conversation stats
        if st.session_state[f'{role}_chat_history']:
            st.metric("Messages", len(st.session_state[f'{role}_chat_history']))

