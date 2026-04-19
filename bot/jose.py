# bot/jose.py
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from rag.retriever import LegalRetriever
from utils.logger import setup_logger
from openai import OpenAI

logger = setup_logger(__name__)

class DrJoseBot:
    """Assistente jurídico português Dr. José"""
    
    SYSTEM_PROMPT = """Tu és o Dr. José, um assistente jurídico especializado em direito português.

REGRAS IMPORTANTES:
1. Baseia as tuas respostas APENAS no contexto jurídico fornecido
2. Se a informação não estiver no contexto, diz claramente que não tens essa informação
3. Cita sempre os artigos e diplomas legais quando possível
4. Lembra que és um assistente informativo, NÃO substituis aconselhamento jurídico profissional
5. Usa linguagem clara e acessível, explicando termos técnicos quando necessário
6. Se a pergunta for ambígua, pede esclarecimentos adicionais
7. NUNCA inventas artigos ou informações - se não sabes, dizes que não sabes

RESPONSABILIDADE LEGAL:
Inclui sempre esta nota para perguntas jurídicas específicas:
"⚠️ Nota: Esta é uma resposta informativa baseada em legislação portuguesa. Para situações concretas, consulta sempre um advogado inscrito na Ordem dos Advogados."

Formato da resposta:
1. Resposta direta à questão
2. Fundamentação legal (artigos/diplomas citados)
3. Nota de responsabilidade (quando aplicável)
"""
    
    def __init__(self):
        """Inicializa o bot"""
        logger.info("Inicializando Dr. José...")
        
        # Validar configuração
        try:
            config.validate()
        except Exception as e:
            logger.error(f"Erro de configuração: {e}")
            print(f"\n❌ Erro: {e}")
            print("Verifica o ficheiro .env com a OPENROUTER_API_KEY")
            sys.exit(1)
        
        # Inicializar componentes
        self.retriever = LegalRetriever()
        self.conversation_history = []
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
        )
        
        # Verificar se o retriever está pronto
        if not self.retriever.is_ready():
            logger.warning("Base vetorial não encontrada!")
            print("\n⚠️ Aviso: Base vetorial não encontrada!")
            print(f"   Executa: python scripts/ingest.py")
            print("   O bot vai funcionar apenas com conhecimento geral.\n")
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitiza o input do utilizador para prevenir prompt injection"""
        # Remover tentativas de system prompt override
        dangerous_patterns = [
            "ignore previous instructions",
            "ignore the above",
            "system:",
            "you are now",
            "forget your",
            "new role:",
        ]
        
        user_input_lower = user_input.lower()
        for pattern in dangerous_patterns:
            if pattern in user_input_lower:
                logger.warning(f"Possível prompt injection bloqueada: {user_input[:50]}")
                return "⚠️ [Input bloqueado por razões de segurança]"
        
        # Limitar tamanho
        if len(user_input) > 2000:
            user_input = user_input[:2000] + "..."
        
        return user_input.strip()
    
    def get_response(self, user_input: str) -> str:
        """Gera resposta baseada no contexto recuperado"""
        
        # Sanitizar input
        user_input = self.sanitize_input(user_input)
        if user_input.startswith("⚠️"):
            return user_input
        
        # Recuperar contexto
        context = self.retriever.get_context(user_input)
        
        # Construir mensagens
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # Adicionar contexto se disponível
        if context and "nenhum documento" not in context:
            messages.append({
                "role": "user",
                "content": f"""Contexto jurídico recuperado:
{context}

Pergunta do utilizador: {user_input}

Com base APENAS no contexto acima, responde de forma clara e fundamentada."""
            })
        else:
            messages.append({
                "role": "user",
                "content": f"""Não foi encontrado contexto jurídico específico para: {user_input}

Responde honestamente que não tens informação específica sobre este tópico na tua base de conhecimento, sugerindo que o utilizador consulte um advogado ou fontes oficiais."""
            })
        
        # Adicionar histórico (últimas 3 interações)
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        try:
            # Chamar API com retry
            for attempt in range(3):
                try:
                    response = self.client.chat.completions.create(
                        model=config.OPENROUTER_MODEL,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1000,
                        timeout=30
                    )
                    answer = response.choices[0].message.content
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    logger.warning(f"Tentativa {attempt+1} falhou: {e}")
            
            # Guardar no histórico
            self.conversation_history.append({
                "user": user_input,
                "assistant": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            # Limitar histórico
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer
            
        except Exception as e:
            logger.error(f"Erro na API: {str(e)}")
            return f"""❌ Erro ao contactar o assistente: {str(e)}

Por favor, verifica:
1. A tua chave API da OpenRouter no ficheiro .env
2. A tua ligação à internet
3. Se o modelo {config.OPENROUTER_MODEL} está disponível

Tenta novamente mais tarde."""
    
    def run(self):
        """Interface de linha de comando"""
        print("\n" + "="*60)
        print("⚖️  Dr. José - Assistente Jurídico Português  ⚖️")
        print("="*60)
        print("\n📚 Especializado em: CRP | Código Penal | Código Civil | Código do Trabalho")
        print("⚠️  Aviso: Este assistente NÃO substitui aconselhamento jurídico profissional")
        print("\n💡 Comandos especiais:")
        print("   /ajuda     - Mostrar esta mensagem")
        print("   /contexto  - Ver contexto recuperado para a última pergunta")
        print("   /historico - Ver histórico da conversa")
        print("   /limpar    - Limpar histórico")
        print("   /sair      - Sair do programa")
        print("\n" + "-"*60)
        
        last_context = None
        
        while True:
            try:
                user_input = input("\n👤 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiais
                if user_input.lower() == '/sair':
                    print("\n👋 Dr. José: Até breve! Lembra-te: em caso de dúvida jurídica, consulta sempre um advogado.")
                    break
                
                elif user_input.lower() == '/ajuda':
                    print("\n📖 Dr. José: Sou um assistente jurídico baseado em RAG. Pergunta-me sobre direito português!")
                    print("   Exemplos: 'Quais os prazos para impugnação de uma multa?', 'O que diz o artigo 217º do Código Penal?'")
                    continue
                
                elif user_input.lower() == '/limpar':
                    self.conversation_history.clear()
                    print("\n🧹 Dr. José: Histórico da conversa limpo!")
                    continue
                
                elif user_input.lower() == '/historico':
                    if not self.conversation_history:
                        print("\n📝 Dr. José: Ainda não há histórico de conversas.")
                    else:
                        print(f"\n📝 Histórico das últimas {len(self.conversation_history)} interações:")
                        for i, turn in enumerate(self.conversation_history[-5:], 1):
                            print(f"\n{i}. Você: {turn['user'][:100]}...")
                            print(f"   Dr. José: {turn['assistant'][:100]}...")
                    continue
                
                elif user_input.lower() == '/contexto':
                    if last_context:
                        print(f"\n📚 Contexto recuperado:\n{last_context}")
                    else:
                        print("\n📚 Ainda não foi recuperado contexto. Faz uma pergunta primeiro!")
                    continue
                
                # Processar pergunta normal
                print("\n🤔 Dr. José: A analisar a questão...")
                
                # Recuperar contexto para mostrar (opcional)
                last_context = self.retriever.get_context(user_input)
                
                # Obter resposta
                response = self.get_response(user_input)
                
                print(f"\n⚖️  Dr. José:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Dr. José: Sessão interrompida. Até breve!")
                break
            except Exception as e:
                logger.error(f"Erro não tratado: {str(e)}")
                print(f"\n❌ Ocorreu um erro inesperado. Verifica o ficheiro logs/dr_jose.log")

def main():
    """Ponto de entrada principal"""
    try:
        bot = DrJoseBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Falha ao iniciar o bot: {str(e)}")
        print(f"\n❌ Não foi possível iniciar o Dr. José: {e}")
        print("Verifica os logs para mais detalhes.")

if __name__ == "__main__":
    main()
