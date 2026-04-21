# ⚖️ DR. JOSÉ — Assistente Jurídico Digital Português

## PROPOSTA TÉCNICA PARA O GOVERNO PORTUGUÊS

*Democratização do Acesso à Justiça através de Inteligência Artificial*

**Abril de 2026 — Versão 2.0**

---

## 1. Sumário Executivo

O **Dr. José** é um assistente jurídico digital de **fonte aberta (open source)**, desenvolvido especificamente para o direito português. O sistema combina uma base de conhecimento estruturada com legislação nacional e modelos de inteligência artificial generativa, permitindo que qualquer cidadão aceda a informação jurídica precisa, fundamentada e acessível, de forma **gratuita e permanente**.

Ao contrário das soluções comerciais existentes, o Dr. José foi concebido como **infraestrutura pública digital**: auditável, adaptável e controlada pelo Estado Português, não por entidades privadas.

| **Open Source** | **RGPD Conforme** | **Gratuito** | **Auditável** |
|----------------|-------------------|--------------|---------------|
| Código público no GitHub | Dados em servidores PT | Sem subscrições | Verificável pelo Estado |

---

## 2. Problema e Oportunidade

### 2.1 A Barreira ao Acesso à Justiça

Em Portugal, o acesso à informação jurídica continua a ser um privilégio de quem pode pagar advogado ou domina linguagem técnica complexa. Os cidadãos enfrentam três barreiras:

- **Linguagem jurídica inacessível** — a legislação portuguesa é extensa e técnica
- **Custos elevados** — uma consulta a advogado custa entre 80€ e 200€ por hora
- **Assimetria de informação** — empresários e grandes entidades têm acesso a equipas jurídicas; o cidadão comum não

### 2.2 O Que Já Existe (e Por Que Não Chega)

| **Solução** | **Gratuito** | **Open Source** | **Direito PT** | **Cidadão** |
|-------------|--------------|-----------------|----------------|-------------|
| LIA (Diário da República) | ✔ | ✘ | Parcial | Limitado |
| advIA / LeiPT | ✘ | ✘ | ✔ | Advogados |
| ChatGPT / Gemini | Parcial | ✘ | ✘ | Genérico |
| **Dr. José** | **✔** | **✔** | **✔** | **✔** |

---

## 3. Solução Técnica

### 3.1 Arquitetura do Sistema

O Dr. José assenta em quatro componentes integrados:

| # | Componente | Descrição | Tecnologia |
|---|------------|-----------|------------|
| 1 | **Base de Conhecimento (RAG)** | Fragmentos indexados da legislação portuguesa | ChromaDB + Sentence Transformers |
| 2 | **Motor de Pesquisa Semântica** | Identifica artigos relevantes por similaridade semântica | Python + paraphrase-multilingual |
| 3 | **Modelo de Linguagem (LLM)** | Gera respostas fundamentadas em português de Portugal | OpenRouter API (fallback automático) |
| 4 | **Interface Web + API REST** | Acessível a qualquer cidadão; integrável no ePortugal | Streamlit + FastAPI |

### 3.2 Estado Atual do Desenvolvimento

| Componente | Estado | Notas |
|------------|--------|-------|
| Motor RAG | ✅ Concluído | ChromaDB com PersistentClient |
| Interface Web (Streamlit) | ✅ Concluído | Disponível em localhost:8501 |
| Interface CLI | ✅ Concluído | Comandos /ajuda, /historico, etc. |
| Fallback de modelos | ✅ Concluído | Tenta 3+ modelos gratuitos automaticamente |
| Ingestão de leis (TXT/PDF/HTML) | ✅ Concluído | Suporte multi-formato |
| Download automático de leis | ⚠️ Parcial | Manual por enquanto (site PGDL bloqueia scraping) |

### 3.3 Base Legal Coberta (Atual)

Na versão atual, o Dr. José suporta os seguintes diplomas legais:

- Constituição da República Portuguesa (CRP)
- Código Penal Português (CP)
- Código de Processo Penal (CPP)
- Código Civil
- Código do Trabalho
- Código da Estrada
- Código do Procedimento Administrativo
- Lei do Arrendamento Urbano (NRAU)
- RGPD (adaptado)

---

## 4. Conformidade, Segurança e RGPD

| **Requisito** | **Como o Dr. José Cumpre** |
|---------------|----------------------------|
| **Dados pessoais (RGPD)** | Não armazena dados pessoais. As perguntas não são associadas a identidade. Histórico apenas em memória de sessão. |
| **Soberania digital** | Pode ser alojado em servidores portugueses ou da UE. Não depende de nuvens americanas. |
| **Auditabilidade** | Código totalmente aberto no GitHub. Qualquer técnico do Estado pode inspecionar o comportamento do sistema. |
| **AI Act (UE)** | Classifica-se como sistema de IA de baixo risco (informação geral). Inclui disclaimer obrigatório em todas as respostas. |
| **Disponibilidade** | API REST com monitorização. Pode ser integrado com sistemas de alerta existentes. |
| **Atualizações legais** | Processo de re-ingestão permite atualizar a base legal quando a legislação muda, sem alterar o código. |

---

## 5. Roadmap de Implementação

| Fase | Prazo | Entregável | Estado |
|------|-------|------------|--------|
| **Fase 1** | Mês 1-2 | Sistema RAG + API + Interface Web (MVP) | ✅ **Concluído** |
| **Fase 2** | Mês 3-4 | Ingestão completa de 10+ diplomas legais + testes com utilizadores | ✅ **Concluído** |
| **Fase 3** | Mês 5-6 | Integração com portal ePortugal + autenticação Chave Móvel Digital | 📋 **Planeado** |
| **Fase 4** | Mês 7-9 | Expansão para jurisprudência (acórdãos STJ, TRs) + modo multilingue | 📋 **Planeado** |
| **Fase 5** | Mês 10-12 | App móvel + acesso por voz + quiosques nos Espaços do Cidadão | 📋 **Futuro** |

---

## 6. Demonstração e Repositório

| Item | Link |
|------|------|
| **Repositório GitHub** | https://github.com/F-i-Red/Dr.Jose |
| **Documentação técnica** | Pasta `/docs` no repositório |
| **README** | https://github.com/F-i-Red/Dr.Jose/blob/main/README.md |
| **Licença** | MIT (livre para uso público e comercial) |
| **Demonstração ao vivo** | Disponível mediante solicitação |

---

## 7. Proposta de Colaboração com o Governo

Propomos ao Governo Português uma das seguintes modalidades de colaboração:

| Modalidade | Descrição | Benefício para o Estado |
|------------|-----------|-------------------------|
| **A — Piloto** | Disponibilizar o Dr. José como serviço experimental em 1-2 Espaços do Cidadão por 6 meses | Validação com utilizadores reais sem investimento significativo |
| **B — Parceria Técnica** | O Estado fornece infraestrutura de alojamento (nuvem portuguesa) e acesso à base do DRE | Acesso a legislação atualizada automática. Nenhum custo de licença |
| **C — Integração ePortugal** | Incorporar o Dr. José diretamente no portal ePortugal como complemento à LIA | Alcance nacional imediato. Diferenciação face a sistemas europeus |

---

## 8. Contacto e Próximos Passos

Para agendar uma demonstração ou discutir os próximos passos:

- **Repositório:** https://github.com/F-i-Red/Dr.Jose
- **Issues / Discussões:** Disponível no GitHub
- **Documentação completa:** Pasta `/docs` do repositório

---

> *"Aproximar a lei das pessoas, não as pessoas da lei."*

**Dr. José — Assistente Jurídico Português**

*Abril de 2026 — Versão 2.0*
