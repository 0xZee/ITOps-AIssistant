import streamlit as st
from ollama import Client
import datetime
import os

# unset localhost proxy calls
os.environ["no_proxy"] = "127.0.0.1,localhost"

=== Liste des ingénieurs autorisés ===

ENGINEERS = {
    "X22222": {
        "name": "Emily Davis",
        "prompt": "You are Emily's personal AI assistant. You're good at providing health and wellness recommendations."
    },
    "X33333": {
        "name": "Michael Wilson",
        "prompt": "You are Michael's AI companion. You specialize in financial advice and investment strategies."
    }
}

# === Prompt invité par défaut ===
GUEST_PROMPT = (
    "Vous êtes un assistant expert en infrastructure IT, spécialisé dans la planification et le déploiement "
    "dans une entreprise de services cloud."
    "Répondez en français de manière concise."
)

# === INIT SESSION STATE ===
st.set_page_config(
    page_icon="🤖",
    page_title="DPAB_BOT",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)


# === INIT SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = GUEST_PROMPT
if "engineer_mode" not in st.session_state:
    st.session_state.engineer_mode = False


# === SIDEBAR ===
st.sidebar.image('sfr-altice-logo.jpg', width=220)
st.sidebar.subheader(":material/chat: | :red[:material/D_BOT:]  ", divider='red')
engineer_mode = st.sidebar.toggle("  | `Accès DPAB` ")

if engineer_mode:
    key = st.sidebar.text_input("🔐 Clé d'accès", type="password")
    if key in ENGINEERS:
        st.sidebar.success(f"✅ {ENGINEERS[key]['name']} 👷‍♂️")
        st.session_state.current_prompt = ENGINEERS[key]["prompt"]
        st.session_state.engineer_mode = True
    else:
        st.sidebar.warning("Clé invalide ou vide. Mode invité activé.")
        st.session_state.current_prompt = GUEST_PROMPT
        st.session_state.engineer_mode = False
else:
    st.session_state.current_prompt = GUEST_PROMPT
    st.session_state.engineer_mode = False

st.sidebar.divider()
if st.sidebar.button("💬 Nouveau Chat", use_container_width=True):
    st.session_state.messages = []

if st.session_state.messages:
    chat_text = "\n".join(
        [f"{m['role'].upper()} : {m['content']}" for m in st.session_state.messages]
    )
    st.sidebar.download_button(
        label="📥 Télécharger l'historique",
        data=chat_text,
        file_name=f"chat_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M')}.txt",
        mime="text/plain"
    )

# === Affichage des anciens messages ===
st.subheader(":material/chat: Assistant IT – :red[DPAB] 🛡️ 👨🏻‍💻", divider='red')

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# === Stream avec mémoire ===
def context_messages(user_message, memory_limit=2):
    history = st.session_state.messages[-memory_limit*2:]
    messages = [{"role": "system", "content": st.session_state.current_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages

def stream_response(messages):
    client = Client(host='http://127.0.0.1:11434')
    return client.chat(
        #model="mistral:latest",
        model="gemma3:4b",
        messages=messages,
        stream=True,
    )

# === Input utilisateur ===
if prompt := st.chat_input("Posez votre question technique..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("♻️ Réflexion en cours..."):
            placeholder = st.empty()
            response_text = ""
            context = context_messages(prompt)

            try:
                for chunk in stream_response(context):
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        response_text += content
                        placeholder.markdown(response_text + "🔲✨")
                
                # Remove the cursor indicator in the final display
                placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                error_message = f"Erreur de connection à Ollama: {str(e)}"
                placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
