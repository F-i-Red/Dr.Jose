# bot/jose.py
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

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
1. Baseia as tuas respostas APENAS no contexto jurídico fornecido.
2. Se a informação não estiver no contexto, diz claramente que não tens essa informação.
3. Cita sempre os artigos e diplomas legais quando possível (ex.: "Artigo 217.º do Código Penal").
4. És um assistente informativo — NÃO substituis aconselhamento jurídico profissional.
5. Usa linguagem clara, acessível e educada.
6. NUNCA inventas artigos ou leis. Se não souberes, admite-o.

Nota obrigatória no final de respostas jurídicas:
"Nota: Esta é uma resposta informativa baseada em legislação portuguesa. Para situações concretas, consulta sempre um advogado inscrito na Ordem dos Advogados."
"""

    def __init__(self):
        logger.info("Inicializando Dr. José...")
        
        try:
            config.validate()
        except Exception as e:
            logger.error(f"Erro de configuração: {e}")
            print(f"\nErro: {e}")
            print("Verifica o ficheiro .env")
            sys.exit(1)
        
        self.retriever = LegalRetriever()
        self.conversation_history: List[Dict[str, Any]] = []
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
        )
        
        if not self.retriever._collection:
            logger.warning("Base vetorial ChromaDB não está pronta.")
            print("\nAviso: Executa primeiro: python scripts/ingest.py")
    
    def sanitize_input(self, user_input: str) -> str:
        if not user_input:
            return ""
        
        dangerous = ["ignore previous instructions", "ignore the above", "system:", "you are now"]
        lower = user_input.lower()
        for d in dangerous:
            if d in lower:
                logger.warning("Possível prompt injection bloqueada")
                return "[Input bloqueado por segurança]"
        
        if len(user_input) > 2000:
            user_input = user_input[:2000] + "..."
        return user_input.strip()
    
    def get_response(self, user_input: str) -> str:
        user_input = self.sanitize_input(user_input)
        if user_input.startswith("["):
            return user_input
        
        context = self.retriever.get_context(user_input) if hasattr(self.retriever, 'get_context') else ""
        
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if context and "nenhum artigo relevante" not in context.lower():
            messages.append({
                "role": "user",
                "content": f"Contexto jurídico:\n{context}\n\nPergunta: {user_input}\nResponde com base apenas neste contexto."
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Pergunta: {user_input}\nNão encontrei informação específica na base de leis. Responde honestamente."
            })
        
        # Histórico
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        try:
            response = self.client.chat.completions.create(
                model=config.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                timeout=40
            )
            answer = response.choices[0].message.content.strip()
            
            self.conversation_history.append({
                "user": user_input,
                "assistant": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer
            
        except Exception as e:
            logger.error(f"Erro API: {e}")
            return f"Erro ao contactar o modelo: {str(e)}\nVerifica a tua chave API no .env"
    
    def run(self):
        print("\n" + "="*65)
        print("⚖️  Dr. José - Assistente Jurídico Português")
        print("="*65)
        print("Comandos: /ajuda | /historico | /limpar | /sair")
        print("-" * 65)
        
        while True:
            try:
                user_input = input("\nVocê: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() == '/sair':
                    print("\nDr. José: Até breve!")
                    break
                elif user_input.lower() == '/ajuda':
                    print("\nPergunta-me sobre leis portuguesas. Ex: 'O que diz o artigo 32 da CRP?'")
                    continue
                elif user_input.lower() == '/limpar':
                    self.conversation_history.clear()
                    print("Histórico limpo.")
                    continue
                elif user_input.lower() == '/historico':
                    print(f"Histórico ({len(self.conversation_history)}):")
                    for i, t in enumerate(self.conversation_history[-3:], 1):
                        print(f"{i}. {t['user'][:60]}...")
                    continue
                
                print("\nDr. José: A pensar...")
                answer = self.get_response(user_input)
                print(f"\nDr. José: {answer}")
                
            except KeyboardInterrupt:
                print("\n\nAté breve!")
                break
            except Exception as e:
                print(f"\nErro: {e}")

if __name__ == "__main__":
    bot = DrJoseBot()
    bot.run()
