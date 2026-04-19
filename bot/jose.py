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
5. Usa linguagem clara, acessível e educada, explicando termos técnicos quando necessário.
6. Se a pergunta for ambígua, pede esclarecimentos adicionais.
7. NUNCA inventas artigos, leis ou informações. Se não souberes, admite-o.

RESPONSABILIDADE LEGAL (obrigatória em todas as respostas jurídicas):
Inclui sempre no final:
"Nota: Esta é uma resposta informativa baseada em legislação portuguesa. Para situações concretas, consulta sempre um advogado inscrito na Ordem dos Advogados ou fontes oficiais."

Formato recomendado da resposta:
1. Resposta direta e clara à questão
2. Fundamentação legal com citações
3. Nota de responsabilidade"""

    def __init__(self):
        """Inicializa o bot"""
        logger.info("Inicializando Dr. José...")
        
        # Validar configuração
        try:
            config.validate()
        except Exception as e:
            logger.error(f"Erro de configuração: {e}")
            print(f"\nErro: {e}")
            print("Verifica o ficheiro .env com a OPENROUTER_API_KEY")
            sys.exit(1)
        
        # Inicializar componentes
        self.retriever = LegalRetriever()
        self.conversation_history: List[Dict[str, Any]] = []
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
        )
        
        # Verificar se o retriever está pronto
        if not self.retriever.is_ready():
            logger.warning("Base vetorial não encontrada!")
            print("\nAviso: Base vetorial não encontrada!")
            print("   Executa primeiro: python scripts/ingest.py")
            print("   O bot vai funcionar apenas com conhecimento geral.\n")
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitiza o input do utilizador para prevenir prompt injection"""
        if not user_input:
            return ""
        
        dangerous_patterns = [
            "ignore previous instructions", "ignore the above", "system:",
            "you are now", "forget your", "new role:", "act as", "roleplay"
        ]
        
        user_input_lower = user_input.lower()
        for pattern in dangerous_patterns:
            if pattern in user_input_lower:
                logger.warning(f"Possível prompt injection bloqueada: {user_input[:80]}...")
                return "[Input bloqueado por razões de segurança]"
        
        # Limitar tamanho
        if len(user_input) > 2000:
            user_input = user_input[:2000] + "..."
        
        return user_input.strip()
    
    def get_response(self, user_input: str) -> str:
        """Gera resposta baseada no contexto recuperado"""
        user_input = self.sanitize_input(user_input)
        if user_input.startswith("["):
            return user_input
        
        # Recuperar contexto jurídico
        context = self.retriever.get_context(user_input)
        
        # Construir mensagens para o modelo
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        if context and "nenhum documento relevante" not in context.lower():
            messages.append({
                "role": "user",
                "content": f"""Contexto jurídico recuperado da base de conhecimento portuguesa:

{context}

Pergunta do utilizador: {user_input}

Responde com base APENAS neste contexto. Cita os artigos relevantes quando aplicável."""
            })
        else:
            messages.append({
                "role": "user",
                "content": f"""Não foi encontrado contexto jurídico específico na base de conhecimento para a seguinte pergunta:

{user_input}

Responde de forma honesta, dizendo que não tens informação específica sobre este tópico na tua base atualizada de legislação. Sugere que o utilizador consulte um advogado ou fontes oficiais (DRE, PGDL, etc.)."""
            })
        
        # Adicionar histórico recente (últimas 3 interações)
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        try:
            # Chamada à API com retry simples
            for attempt in range(3):
                try:
                    response = self.client.chat.completions.create(
                        model=config.OPENROUTER_MODEL,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1200,
                        timeout=45
                    )
                    answer = response.choices[0].message.content.strip()
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    logger.warning(f"Tentativa {attempt + 1}/3 falhou: {e}")
                    continue
            
            # Guardar no histórico
            self.conversation_history.append({
                "user": user_input,
                "assistant": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer
            
        except Exception as e:
            logger.error(f"Erro na chamada à API: {str(e)}")
            return f"""Ocorreu um erro ao processar a tua pergunta: {str(e)}

Verifica:
1. Se a chave OPENROUTER_API_KEY está correta no ficheiro .env
2. A tua ligação à internet
3. Se o modelo está disponível no OpenRouter

Tenta novamente mais tarde."""

    def run(self):
        """Interface de linha de comando completa"""
        print("\n" + "=" * 70)
        print("⚖️  Dr. José - Assistente Jurídico Português")
        print("=" * 70)
        print("Especializado em: Constituição da República Portuguesa, Código Penal,")
        print("Código Civil, Código do Trabalho e outros diplomas principais.")
        print("\n⚠️  AVISO: Este assistente NÃO substitui aconselhamento jurídico profissional.")
        print("\nComandos especiais:")
        print("   /ajuda      → Mostrar ajuda")
        print("   /contexto   → Ver contexto da última pergunta")
        print("   /historico  → Ver histórico recente")
        print("   /limpar     → Limpar histórico")
        print("   /sair       → Sair do programa")
        print("-" * 70)
        
        last_context: str = ""
        
        while True:
            try:
                user_input = input("\nVocê: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiais
                if user_input.lower() == '/sair':
                    print("\nDr. José: Até breve! Em caso de dúvida jurídica séria, consulta sempre um advogado.")
                    break
                
                elif user_input.lower() == '/ajuda':
                    print("\nDr. José: Podes perguntar-me qualquer coisa sobre direito português.")
                    print("Exemplos:")
                    print("   - O que diz o artigo 217.º do Código Penal?")
                    print("   - Quais são os direitos do arrendatário na lei do arrendamento urbano?")
                    print("   - Como funciona a prescrição em direito penal?")
                    continue
                
                elif user_input.lower() == '/limpar':
                    self.conversation_history.clear()
                    print("\nDr. José: Histórico limpo com sucesso.")
                    continue
                
                elif user_input.lower() == '/historico':
                    if not self.conversation_history:
                        print("\nDr. José: Ainda não há histórico.")
                    else:
                        print(f"\nHistórico ({len(self.conversation_history)} interações):")
                        for i, turn in enumerate(self.conversation_history[-5:], 1):
                            print(f"\n{i}. Você: {turn['user'][:90]}{'...' if len(turn['user']) > 90 else ''}")
                            print(f"   Dr. José: {turn['assistant'][:90]}{'...' if len(turn['assistant']) > 90 else ''}")
                    continue
                
                elif user_input.lower() == '/contexto':
                    if last_context:
                        print("\nÚltimo contexto recuperado:")
                        print(last_context[:1500] + "..." if len(last_context) > 1500 else last_context)
                    else:
                        print("\nDr. José: Ainda não existe contexto. Faz primeiro uma pergunta normal.")
                    continue
                
                # Pergunta normal
                print("\nDr. José: A consultar a legislação...")
                answer = self.get_response(user_input)
                
                # Guardar contexto para o comando /contexto
                context = self.retriever.get_context(user_input)
                last_context = context if context else ""
                
                print(f"\nDr. José: {answer}")
                
            except KeyboardInterrupt:
                print("\n\nAté breve!")
                break
            except Exception as e:
                logger.error(f"Erro inesperado no run(): {e}")
                print("\nOcorreu um erro inesperado. Tenta novamente.")

if __name__ == "__main__":
    bot = DrJoseBot()
    bot.run()
