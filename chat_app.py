import streamlit as st
import json
from chat_engine import ChatBot
from usersconfig import UserKeys

st.set_page_config(
    page_icon="🤖",
    page_title="Gamma-Bot",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

def initialize_session_state():
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot(st.secrets["GROQ_API"])
    if "users_config" not in st.session_state:
        st.session_state.users_config = UserKeys()

initialize_session_state()

with st.sidebar:
    st.subheader("🅞🆇 Z 🅴🅴 - 🇩🇵🇦-🇧 ", divider="gray")
    st.write('`DPAB Chatbot` | `Support & Déploiement Infra`')
    
    user_key = st.text_input("🔐 :grey-background[Clé Utilisateur]", value="", key="user_key_input")
    
    if not st.session_state.chat_started:
        if st.button("Démarrer Chat", use_container_width=True):
            # If no user key provided, use 'guest' thread
            thread_id = user_key if user_key else 'guest'
            
            # If user key is provided, get personalized system prompt
            system_prompt = None
            user_info = None
            if user_key:
                user_info = st.session_state.users_config.get_user_by_key(user_key)
                if user_info:
                    system_prompt = user_info['personalized_system_prompt']
                    st.success(f"Connecté en tant que {user_info['user_name']}")
                else:
                    st.error("Clé utilisateur invalide")
                    st.stop()
            
            st.session_state.chat_started = True
            st.session_state.messages = []
            st.session_state.thread_id = thread_id
            st.session_state.system_prompt = system_prompt
            st.session_state.user_info = user_info  # Store user info in session state
            st.rerun()
    else:
        # Display user info if available
        if hasattr(st.session_state, 'user_info') and st.session_state.user_info:
            st.write(f"👨🏻‍💻 Accès : **`{st.session_state.user_info['user_name']}`** ✅")
            #st.write(f"**Domaine:** {st.session_state.user_info['it_domain']}")
            #st.write(f"**Compétences:** {', '.join(st.session_state.user_info['skills'])}")
        
        if st.button("Terminer le chat", use_container_width=True, type="primary"):
            # Option to download chat history
            chat_history_json = json.dumps(st.session_state.messages, indent=2)
            
            # Customize filename based on user info if available
            filename = f"chat_history_{st.session_state.thread_id}.json"
            if hasattr(st.session_state, 'user_info') and st.session_state.user_info:
                filename = f"chat_history_{st.session_state.user_info['user_name']}_{st.session_state.thread_id}.json"
            
            st.download_button(
                label="Télécharger l'historique de chat",
                data=chat_history_json,
                file_name=filename,
                mime="application/json"
            )
            
            st.session_state.chat_started = False
            st.rerun()


#st.subheader("၊၊||၊ 🍓 Đ🅿🅰🅱 :grey[CHAT]🅱🅞🆃 ☰", divider="gray")
st.subheader("☰ :grey-background[DPAB] :grey[CHAT]🅱🅞🆃 🍓", divider="gray")

if st.session_state.chat_started:
    if not st.session_state.messages:
        hello_message = ":sparkles: Bonjour, comment puis-je vous aider aujourd'hui ?"
        st.session_state.messages = [{"role": "assistant", "content": hello_message}]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Votre message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Use the thread_id and optional system_prompt from session state
            response = st.session_state.chatbot.chat(
                prompt, 
                thread_id=st.session_state.thread_id, 
                system_prompt=st.session_state.system_prompt
            )
            
            response_content = response["messages"][-1].content
            response_str = ""
            response_container = st.empty()
            for token in response_content:
                response_str += token
                response_container.markdown(response_str)
            st.session_state.messages.append(
                {"role": "assistant", "content": response["messages"][-1].content}
            )
