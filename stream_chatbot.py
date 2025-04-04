import streamlit as st
from groq import Groq
import datetime

# === GROQ Client ===
client = Groq(api_key=st.secrets['GROQ_API'])

# === Liste des ingénieurs autorisés ===
ENGINEERS = {
    "1234-ABCD": {
        "name": "Alice Dupont",
        "prompt": (
            "Vous êtes Alice Dupont, ingénieure spécialisée en réseaux et sécurité dans un fournisseur cloud. "
            "Vous conseillez sur la configuration réseau, les VPN, le SDN, et la sécurité des infrastructures cloud."
        )
    },
    "5678-EFGH": {
        "name": "Jean Morel",
        "prompt": (
            "Vous êtes Jean Morel, ingénieur DevOps dans un département cloud. Vous aidez sur la CI/CD, "
            "l'automatisation avec Ansible/Terraform, le monitoring, et la conteneurisation (Docker, K8s)."
        )
    },
    "9012-IJKL": {
        "name": "Claire Martin",
        "prompt": (
            "Vous êtes Claire Martin, ingénieure cloud spécialisée en architecture haute disponibilité et migration. "
            "Vous conseillez sur le design scalable, la gestion des pannes, et les stratégies de migration vers le cloud."
        )
    }
}

# === Prompt invité par défaut ===
GUEST_PROMPT = (
    "Vous êtes un assistant expert en infrastructure IT, spécialisé dans la planification et le déploiement "
    "dans une entreprise de services cloud. Répondez de manière technique, détaillée et claire."
)

# === INIT SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = GUEST_PROMPT
if "engineer_mode" not in st.session_state:
    st.session_state.engineer_mode = False


# === SIDEBAR ===
st.sidebar.subheader("💎 D-ChatBot", divider='orange')
engineer_mode = st.sidebar.toggle("  | `Accès personnalisé` ")

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

if st.sidebar.button("Nouveau Chat 💬 ", use_container_width=True):
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
st.subheader("🧠 Assistant IT – Cloud & Infra 💎", divider='orange')

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

def stream_groq_response(messages):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.4,
        top_p=1,
        max_completion_tokens=1024,
        stream=True,
    )

# === Input utilisateur ===
if prompt := st.chat_input("Posez votre question technique..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_text = ""
        context = context_messages(prompt)

        for chunk in stream_groq_response(context):
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                placeholder.markdown(response_text + "▌🤖✨")

        placeholder.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
