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
    
    # Initialize AI features - recreate if method doesn't exist
    if 'ai_features' not in st.session_state or not hasattr(st.session_state.ai_features, 'chat_with_ai'):
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
            try:
                # Get conversation history (exclude the current user message we just added)
                conversation_history = [
                    {'role': msg['role'], 'content': msg['content']} 
                    for msg in st.session_state[f'{role}_chat_history'][:-1][-10:]  # Last 10 messages, excluding current
                ]
                
                ai_response = ai.chat_with_ai(user_input, conversation_history)
                
                # Add AI response to history
                if ai_response and isinstance(ai_response, dict) and 'response' in ai_response:
                    response_text = ai_response['response']
                    if response_text and response_text.strip():
                        st.session_state[f'{role}_chat_history'].append({
                            'role': 'assistant',
                            'content': response_text,
                            'timestamp': ai_response.get('timestamp', datetime.now().isoformat())
                        })
                    else:
                        # Fallback if response is empty
                        st.session_state[f'{role}_chat_history'].append({
                            'role': 'assistant',
                            'content': "I'm here to help! Could you please rephrase your question?",
                            'timestamp': datetime.now().isoformat()
                        })
                else:
                    # Fallback if response format is wrong
                    st.error("Failed to get AI response. Please try again.")
                    st.session_state[f'{role}_chat_history'].append({
                        'role': 'assistant',
                        'content': "I apologize, but I couldn't process your question. Please try rephrasing it.",
                        'timestamp': datetime.now().isoformat()
                    })
            except AttributeError as e:
                st.error(f"AI Chatbot error: {str(e)}. Please refresh the page.")
                # Recreate AI features instance
                st.session_state.ai_features = AIFeatures()
                st.session_state[f'{role}_chat_history'].append({
                    'role': 'assistant',
                    'content': "I encountered an error. Please try asking your question again.",
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                st.error(f"An error occurred: {str(e)}. Please try again.")
                import traceback
                st.error(traceback.format_exc())
                # Add a fallback response
                st.session_state[f'{role}_chat_history'].append({
                    'role': 'assistant',
                    'content': "I apologize, but I encountered an error. Please try rephrasing your question or refresh the page.",
                    'timestamp': datetime.now().isoformat()
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

