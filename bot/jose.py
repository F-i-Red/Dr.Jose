# bot/jose.py
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
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
"Nota: Esta é uma resposta informativa baseada em legislação portuguesa. Para situações concretas, consulta sempre um advogado inscrito na Ordem dos Advogados."

Formato da resposta:
1. Resposta direta à questão
2. Fundamentação legal (artigos/diplomas citados)
3. Nota de responsabilidade (quando aplicável)
"""
    
    def __init__(self):
        logger.info("Inicializando Dr. José...")
        
        try:
            config.validate()
        except Exception as e:
            logger.error(f"Erro de configuração: {e}")
            print(f"\nErro: {e}")
            print("Verifica o ficheiro .env com a OPENROUTER_API_KEY")
            sys.exit(1)
        
        self.retriever = LegalRetriever()
        self.conversation_history = []
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
        )
        
        if not self.retriever.is_ready():
            logger.warning("Base vetorial não encontrada!")
            print("\nAviso: Base vetorial não encontrada!")
            print(f"   Executa: python scripts/ingest.py")
            print("   O bot vai funcionar apenas com conhecimento geral.\n")
    
    def sanitize_input(self, user_input: str) -> str:
        dangerous_patterns = [
            "ignore previous instructions", "ignore the above", "system:", 
            "you are now", "forget your", "new role:"
        ]
        user_input_lower = user_input.lower()
        for pattern in dangerous_patterns:
            if pattern in user_input_lower:
                logger.warning(f"Possível prompt injection bloqueada: {user_input[:50]}")
                return "[Input bloqueado por razões de segurança]"
        
        if len(user_input) > 2000:
            user_input = user_input[:2000] + "..."
        return user_input.strip()
    
    def get_response(self, user_input: str) -> Tuple[str, str]:
        """Retorna (resposta, contexto_recuperado)"""
        user_input = self.sanitize_input(user_input)
        if user_input.startswith("["):
            return user_input, ""
        
        context = self.retriever.get_context(user_input)
        
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if context and "nenhum documento" not in context.lower():
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

Responde honestamente que não tens informação específica sobre este tópico na tua base de conhecimento."""
            })
        
        # Histórico (últimas 3 interações)
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        try:
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
            
            self.conversation_history.append({
                "user": user_input,
                "assistant": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer, context
            
        except Exception as e:
            logger.error(f"Erro na API: {str(e)}")
            return f"""Erro ao contactar o assistente: {str(e)}

Verifica a chave API e a ligação à internet.""", ""
    
    def run(self):
        """Interface de linha de comando completa"""
        print("\n" + "="*60)
        print("Dr. José - Assistente Jurídico Português")
        print("="*60)
        print("\nEspecializado em: CRP | Código Penal | Código Civil | Código do Trabalho")
        print("Aviso: Este assistente NÃO substitui aconselhamento jurídico profissional")
        print("\nComandos especiais:")
        print("   /ajuda     - Mostrar ajuda")
        print("   /contexto  - Ver contexto da última pergunta")
        print("   /historico - Ver histórico")
        print("   /limpar    - Limpar histórico")
        print("   /sair      - Sair")
        print("\n" + "-"*60)
        
        last_context = None
        
        while True:
            try:
                user_input = input("\nVocê: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() == '/sair':
                    print("\nDr. José: Até breve! Em caso de dúvida, consulta sempre um advogado.")
                    break
                
                elif user_input.lower() == '/ajuda':
                    print("\nDr. José: Pergunta-me qualquer coisa sobre direito português!")
                    print("Exemplos: 'O que diz o artigo 217º do Código Penal?'")
                    continue
                
                elif user_input.lower() == '/limpar':
                    self.conversation_history.clear()
                    print("\nDr. José: Histórico limpo!")
                    continue
                
                elif user_input.lower() == '/historico':
                    if not self.conversation_history:
                        print("\nDr. José: Ainda não há histórico.")
                    else:
                        print(f"\nHistórico ({len(self.conversation_history)} interações):")
                        for i, turn in enumerate(self.conversation_history[-5:], 1):
                            print(f"\n{i}. Você: {turn['user'][:100]}...")
                            print(f"   Dr. José: {turn['assistant'][:100]}...")
                    continue
                
                elif user_input.lower() == '/contexto':
                    if last_context:
                        print("\nÚltimo contexto recuperado:")
                        print(last_context[:1500] + "..." if len(last_context) > 1500 else last_context)
                    else:
                        print("\nDr. José: Ainda não tens contexto. Faz uma pergunta primeiro.")
                    continue
                
                # Pergunta normal
                print("\nDr. José: A pensar...")
                answer, context = self.get_response(user_input)
                last_context = context
                
                print(f"\nDr. José: {answer}")
                
            except KeyboardInterrupt:
                print("\n\nAté breve!")
                break
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                print("\nOcorreu um erro. Tenta novamente.")

if __name__ == "__main__":
    bot = DrJoseBot()
    bot.run()
