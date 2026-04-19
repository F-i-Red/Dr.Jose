# app.py
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from bot.jose import DrJoseBot
from scripts.fetch_laws import LawFetcher
from config import config

st.set_page_config(page_title="Dr. José - Advogado Português", page_icon="⚖️", layout="wide")

st.title("⚖️ Dr. José")
st.subheader("O teu assistente jurídico português")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/1280px-Flag_of_Portugal.svg.png", width=100)
    st.markdown("### Sobre o Dr. José")
    st.info("Assistente baseado em RAG com toda a legislação portuguesa consolidada.")
    if st.button("🔄 Atualizar leis do DRE"):
        with st.spinner("A descarregar leis do Diário da República..."):
            fetcher = LawFetcher()
            if fetcher.fetch_all(force_refresh=True):
                st.success("Leis atualizadas!")
            else:
                st.error("Erro no download")
    
    if st.button("📥 Re-indexar base de conhecimento"):
        with st.spinner("A indexar documentos..."):
            import subprocess
            result = subprocess.run(["python", "scripts/ingest.py"], capture_output=True, text=True)
            st.text(result.stdout)

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Faz a tua pergunta jurídica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Dr. José a consultar a lei..."):
            bot = DrJoseBot()
            answer, _ = bot.get_response(prompt)
            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
