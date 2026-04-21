# app.py
import streamlit as st
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from bot.jose import DrJoseBot
from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Dr. José - Assistente Jurídico Português",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado para melhor aparência
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>⚖️ Dr. José</h1>
    <h3>Assistente Jurídico Português</h3>
    <p><i>Baseado em legislação oficial portuguesa</i></p>
</div>
""", unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.markdown("## 📚 Sobre o Dr. José")
    st.markdown("""
    Assistente especializado em direito português, alimentado por:
    
    - Constituição da República Portuguesa
    - Código Penal
    - Código Civil
    - Código do Trabalho
    - Código de Processo Penal
    
    ---
    ### ⚠️ Aviso Legal
    Este assistente fornece **informação de caráter geral e educativo**.
    **Não substitui** aconselhamento jurídico profissional.
    
    Para questões legais específicas, consulte um advogado.
    ---
    ### 🔧 Informação Técnica
    - Modelo: OpenRouter (fallback automático)
    - Base vetorial: ChromaDB
    """)
    
    # Verificar estado da base de conhecimento
    if st.button("🔄 Verificar Base de Conhecimento"):
        with st.spinner("A verificar..."):
            try:
                from rag.retriever import LegalRetriever
                retriever = LegalRetriever()
                if retriever.is_ready():
                    count = retriever._collection.count()
                    st.success(f"✅ Base ativa com {count} documentos indexados")
                else:
                    st.warning("⚠️ Base vazia. Executa: python scripts/ingest.py")
            except Exception as e:
                st.error(f"Erro: {e}")

# Inicializar o bot (apenas uma vez, usar session_state)
if "bot" not in st.session_state:
    with st.spinner("A iniciar o Dr. José..."):
        try:
            st.session_state.bot = DrJoseBot()
            st.session_state.messages = []
            st.success("✅ Dr. José pronto para responder!")
        except Exception as e:
            st.error(f"❌ Erro ao iniciar: {e}")
            st.stop()

# Exibir histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do utilizador
if prompt := st.chat_input("Faça a sua pergunta sobre direito português..."):
    # Adicionar mensagem do utilizador
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("A consultar a legislação..."):
            try:
                response = st.session_state.bot.get_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Erro: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Rodapé com aviso legal
st.markdown("""
<div class="disclaimer">
    ⚖️ Dr. José — Assistente Jurídico Português | Baseado em legislação oficial<br>
    <strong>Nota:</strong> Esta ferramenta não substitui o aconselhamento de um advogado inscrito na Ordem dos Advogados.
</div>
""", unsafe_allow_html=True)
