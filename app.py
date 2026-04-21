# app.py
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from bot.jose import DrJoseBot
from scripts.fetch_laws import LawFetcher
from config import config

# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Dr. José — Advogado Português",
    page_icon="⚖️",
    layout="wide",
)

# ── CSS personalizado (cores institucionais portuguesas) ─────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1a3c2e; }
    [data-testid="stSidebar"] * { color: #f5e6c8 !important; }
    .stChatMessage { border-radius: 10px; }
    h1 { color: #1a3c2e; }
</style>
""", unsafe_allow_html=True)

# ── Inicializar bot UMA VEZ por sessão ───────────────────────────────────────
if "bot" not in st.session_state:
    try:
        config.validate()
        st.session_state.bot = DrJoseBot()
        st.session_state.bot_error = None
    except Exception as e:
        st.session_state.bot = None
        st.session_state.bot_error = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/200px-Flag_of_Portugal.svg.png",
        width=80,
    )
    st.markdown("## ⚖️ Dr. José")
    st.markdown("Assistente Jurídico Português")
    st.divider()

    # Estado da API
    if st.session_state.bot_error:
        st.error(f"⚠️ Erro de configuração:\n{st.session_state.bot_error}")
    else:
        st.success("✅ Sistema operacional")

    st.divider()

    # Gestão da base de conhecimento
    st.markdown("### 📚 Base de Conhecimento")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬇️ Atualizar\nleis", use_container_width=True):
            with st.spinner("A descarregar leis do DRE..."):
                fetcher = LawFetcher()
                if fetcher.fetch_all(force_refresh=True):
                    st.success("✅ Leis atualizadas!")
                else:
                    st.error("❌ Erro no download")

    with col2:
        if st.button("🔄 Re-indexar\nbase", use_container_width=True):
            with st.spinner("A indexar..."):
                import subprocess
                result = subprocess.run(
                    [sys.executable, "scripts/ingest.py"],
                    capture_output=True, text=True, cwd=str(Path(__file__).parent)
                )
                if result.returncode == 0:
                    st.success("✅ Indexado!")
                else:
                    st.error(f"❌ Erro:\n{result.stderr[:200]}")

    # Contar documentos indexados
    try:
        from rag.retriever import LegalRetriever
        r = LegalRetriever()
        count = r.collection.count()
        st.info(f"📊 {count} fragmentos indexados")
    except Exception:
        st.info("📊 Base ainda não indexada")

    st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    ---
    **Diplomas disponíveis:**
    - Constituição da República
    - Código Penal
    - Código Civil
    - Código do Trabalho
    - Código de Processo Penal
    """)

# ── Área principal ───────────────────────────────────────────────────────────
st.title("⚖️ Dr. José")
st.caption("Assistente Jurídico Português — baseado em legislação oficial")

# Verificar erro de configuração
if st.session_state.bot_error:
    st.error(f"""
    **Configuração incompleta**
    
    {st.session_state.bot_error}
    
    **Como resolver:**
    1. Copia o ficheiro `.env.example` para `.env`
    2. Preenche a tua chave OpenRouter (obter em https://openrouter.ai/keys)
    3. Reinicia a aplicação
    """)
    st.stop()

# Sugestões iniciais
if not st.session_state.messages:
    st.markdown("### 💡 Exemplos de perguntas")
    cols = st.columns(2)
    suggestions = [
        "Quais são os meus direitos se for despedido sem justa causa?",
        "O que diz a lei sobre violência doméstica?",
        "Tenho direito a indemnização por acidente de trabalho?",
        "Como posso contestar uma multa de trânsito?",
        "Quais são os direitos do inquilino se o senhorio não fizer obras?",
        "O que é a prisão preventiva e quando é aplicada?",
    ]
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"💬 {suggestion}", use_container_width=True, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()

# Histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
        st.markdown(msg["content"])

# Input do utilizador
if prompt := st.chat_input("Faz a tua pergunta jurídica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Dr. José a consultar a legislação..."):
            answer = st.session_state.bot.get_response(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
