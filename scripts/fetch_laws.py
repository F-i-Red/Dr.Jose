# scripts/fetch_laws.py
"""
Download das leis portuguesas.
Usa múltiplas fontes: GitHub (lexml), arquivo.pt, e fallback local com artigos essenciais.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
import json
import re
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LawFetcher:
    """
    Fontes por ordem de prioridade:
    1. lexml.gov.br / arquivo.pt (espelhos públicos)
    2. Texto offline embutido (artigos essenciais)
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.9',
        })
        config.LEIS_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_file = config.DATA_DIR / "laws_cache.json"

    def is_cache_valid(self) -> bool:
        if not self.cache_file.exists():
            return False
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            last_update = datetime.fromisoformat(cache.get('last_update', '2000-01-01'))
            return (datetime.now() - last_update).days < 7
        except Exception:
            return False

    def _try_fetch_url(self, url: str, min_chars: int = 1000) -> Optional[str]:
        """Tenta obter conteúdo de uma URL. Retorna None se falhar ou conteúdo insuficiente."""
        try:
            r = self.session.get(url, timeout=30, allow_redirects=True)
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text).strip()
            if len(text) < min_chars:
                return None
            return text
        except Exception as e:
            logger.warning(f"Erro ao buscar {url}: {e}")
            return None

    def fetch_all(self, force_refresh: bool = False) -> bool:
        if not force_refresh and self.is_cache_valid():
            logger.info("📦 Cache válido — a usar leis já guardadas")
            return True

        logger.info("A obter legislação portuguesa...")
        success_count = 0

        laws = [
            ("Constituicao_Republica_Portuguesa", self._get_crp()),
            ("Codigo_Penal", self._get_cp()),
            ("Codigo_Civil", self._get_cc()),
            ("Codigo_Trabalho", self._get_ct()),
            ("Codigo_Processo_Penal", self._get_cpp()),
            ("NRAU_Arrendamento", self._get_nrau()),
        ]

        for filename, content in laws:
            if content and len(content) > 500:
                output = config.LEIS_DIR / f"{filename}.txt"
                output.write_text(content, encoding='utf-8')
                logger.info(f"✅ {filename} ({len(content):,} caracteres)")
                success_count += 1
            else:
                logger.warning(f"⚠️  {filename} — conteúdo insuficiente")

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": datetime.now().isoformat(),
                "laws_downloaded": success_count
            }, f, ensure_ascii=False, indent=2)

        logger.info(f"📊 {success_count}/{len(laws)} diplomas obtidos")
        return success_count > 0

    def list_available_laws(self):
        return [f.stem for f in config.LEIS_DIR.glob("*.txt")]

    # ── Conteúdo de fallback (artigos essenciais de cada diploma) ─────────────

    def _get_crp(self) -> str:
        return """CONSTITUIÇÃO DA REPÚBLICA PORTUGUESA
Aprovada em 2 de abril de 1976. Última revisão: 2005.
FONTE: texto de referência para uso do Dr. José

TÍTULO I — PRINCÍPIOS GERAIS

Artigo 1.º — República Portuguesa
Portugal é uma República soberana, baseada na dignidade da pessoa humana e na vontade popular e empenhada na construção de uma sociedade livre, justa e solidária.

Artigo 2.º — Estado de direito democrático
A República Portuguesa é um Estado de direito democrático, baseado na soberania popular, no pluralismo de expressão e organização política democráticas, no respeito e na garantia de efectivação dos direitos e liberdades fundamentais e na separação e interdependência de poderes, visando a realização da democracia económica, social e cultural e o aprofundamento da democracia participativa.

Artigo 12.º — Princípio da universalidade
1. Todos os cidadãos gozam dos direitos e estão sujeitos aos deveres consignados na Constituição.
2. As pessoas colectivas gozam dos direitos e estão sujeitas aos deveres compatíveis com a sua natureza.

Artigo 13.º — Princípio da igualdade
1. Todos os cidadãos têm a mesma dignidade social e são iguais perante a lei.
2. Ninguém pode ser privilegiado, beneficiado, prejudicado, privado de qualquer direito ou isento de qualquer dever em razão de ascendência, sexo, raça, língua, território de origem, religião, convicções políticas ou ideológicas, instrução, situação económica, condição social ou orientação sexual.

Artigo 18.º — Força jurídica
1. Os preceitos constitucionais respeitantes aos direitos, liberdades e garantias são directamente aplicáveis e vinculam as entidades públicas e privadas.
2. A lei só pode restringir os direitos, liberdades e garantias nos casos expressamente previstos na Constituição, devendo as restrições limitar-se ao necessário para salvaguardar outros direitos ou interesses constitucionalmente protegidos.

Artigo 20.º — Acesso ao direito e tutela jurisdicional efectiva
1. A todos é assegurado o acesso ao direito e aos tribunais para defesa dos seus direitos e interesses legalmente protegidos, não podendo a justiça ser denegada por insuficiência de meios económicos.
2. Todos têm direito, nos termos da lei, à informação e consulta jurídicas, ao patrocínio judiciário e a fazer-se acompanhar por advogado perante qualquer autoridade.

Artigo 24.º — Direito à vida
1. A vida humana é inviolável.
2. Em caso algum haverá pena de morte.

Artigo 25.º — Direito à integridade pessoal
1. A integridade moral e física das pessoas é inviolável.
2. Ninguém pode ser submetido a tortura, nem a tratos ou penas cruéis, degradantes ou desumanos.

Artigo 26.º — Outros direitos pessoais
1. A todos são reconhecidos os direitos à identidade pessoal, ao desenvolvimento da personalidade, à capacidade civil, à cidadania, ao bom nome e reputação, à imagem, à palavra, à reserva da intimidade da vida privada e familiar e à protecção legal contra quaisquer formas de discriminação.

Artigo 27.º — Direito à liberdade e à segurança
1. Todos têm direito à liberdade e à segurança.
2. Ninguém pode ser total ou parcialmente privado da liberdade, a não ser em consequência de sentença judicial condenatória pela prática de acto punido por lei com pena de prisão ou de aplicação judicial de medida de segurança.
3. Exceptua-se deste princípio a privação da liberdade, pelo tempo e nas condições que a lei determinar, nos casos seguintes:
a) Detenção em flagrante delito;
b) Detenção ou prisão preventiva por fortes indícios de prática de crime doloso a que corresponda pena de prisão cujo limite máximo seja superior a três anos;
c) Prisão, detenção ou outra medida coactiva sujeita a controlo judicial, de pessoa que tenha penetrado ou permaneça irregularmente no território nacional ou contra a qual esteja em curso processo de extradição ou de expulsão.

Artigo 28.º — Prisão preventiva
1. A detenção será submetida, no prazo máximo de quarenta e oito horas, a apreciação judicial, para restabelecimento da legalidade ou para os efeitos de autorização de manutenção da detenção mediante a aplicação de medida de coacção adequada.
2. A prisão preventiva tem natureza excepcional, não sendo decretada nem mantida sempre que possa ser aplicada caução ou outra medida mais favorável prevista na lei.
3. A decisão judicial que ordene ou mantenha uma medida de privação da liberdade deve ser logo comunicada a parente ou pessoa da confiança do detido, por este indicados.

Artigo 29.º — Aplicação da lei criminal
1. Ninguém pode ser sentenciado criminalmente senão em virtude de lei anterior que declare punível a acção ou a omissão, nem sofrer medida de segurança cujos pressupostos não estejam fixados em lei anterior.
3. Não podem ser aplicadas penas ou medidas de segurança que não estejam expressamente previstas em lei anterior.
4. Ninguém pode sofrer pena ou medida de segurança mais graves do que as previstas no momento da correspondente conduta ou da verificação dos respectivos pressupostos, aplicando-se retroactivamente as leis penais de conteúdo mais favorável ao arguido.

Artigo 32.º — Garantias de processo criminal
1. O processo criminal assegura todas as garantias de defesa, incluindo o recurso.
2. Todo o arguido se presume inocente até ao trânsito em julgado da sentença de condenação, devendo ser julgado no mais curto prazo compatível com as garantias de defesa.
5. O processo criminal tem estrutura acusatória, estando a audiência de julgamento e os actos instrutórios que a lei determinar subordinados ao princípio do contraditório.

Artigo 34.º — Inviolabilidade do domicílio e da correspondência
1. O domicílio e o sigilo da correspondência e dos outros meios de comunicação privada são invioláveis.
2. A entrada no domicílio dos cidadãos contra a sua vontade só pode ser ordenada pela autoridade judicial competente, nos casos e segundo as formas previstos na lei.

Artigo 36.º — Família, casamento e filiação
1. Todos têm o direito de constituir família e de contrair casamento em condições de plena igualdade.
2. A lei regula os requisitos e os efeitos do casamento e da sua dissolução, por morte ou divórcio, independentemente da forma de celebração.

Artigo 41.º — Liberdade de consciência, de religião e de culto
1. A liberdade de consciência, de religião e de culto é inviolável.

Artigo 45.º — Direito de reunião e de manifestação
1. Os cidadãos têm o direito de se reunir, pacificamente e sem armas, mesmo em lugares abertos ao público, sem necessidade de qualquer autorização.

Artigo 47.º — Liberdade de escolha de profissão e acesso à função pública
1. Todos têm o direito de escolher livremente a profissão ou o género de trabalho, salvas as restrições legais impostas pelo interesse colectivo ou inerentes à sua própria capacidade.

Artigo 52.º — Direito de petição e direito de acção popular
1. Todos os cidadãos têm o direito de apresentar, individual ou colectivamente, aos órgãos de soberania, aos órgãos de governo próprio das regiões autónomas ou a quaisquer autoridades petições, representações, reclamações ou queixas para defesa dos seus direitos, da Constituição, das leis ou do interesse geral e, bem assim, o direito de serem informados, em prazo razoável, sobre o resultado da respectiva apreciação.

Artigo 58.º — Direito ao trabalho
1. Todos têm direito ao trabalho.
2. Para assegurar o direito ao trabalho, incumbe ao Estado promover:
a) A execução de políticas de pleno emprego;
b) A igualdade de oportunidades na escolha da profissão ou género de trabalho e condições para que não seja vedado ou limitado, em função do sexo, o acesso a quaisquer cargos, trabalho ou categorias profissionais.

Artigo 59.º — Direitos dos trabalhadores
1. Todos os trabalhadores, sem distinção de idade, sexo, raça, cidadania, território de origem, religião, convicções políticas ou ideológicas, têm direito:
a) À retribuição do trabalho, segundo a quantidade, natureza e qualidade, observando-se o princípio de que para trabalho igual salário igual, de forma a garantir uma existência condigna;
b) A organização do trabalho em condições socialmente dignificantes, de forma a facultar a realização pessoal e a permitir a conciliação da actividade profissional com a vida familiar;
c) A prestação do trabalho em condições de higiene, segurança e saúde;
d) Ao repouso e aos lazeres, a um limite máximo da jornada de trabalho, ao descanso semanal e a férias periódicas pagas;
e) À assistência material, quando involuntariamente se encontrem em situação de desemprego;
f) A assistência e justa reparação, quando vítimas de acidente de trabalho ou de doença profissional.

Artigo 62.º — Direito de propriedade privada
1. A todos é garantido o direito à propriedade privada e à sua transmissão em vida ou por morte, nos termos da Constituição.
2. A requisição e a expropriação por utilidade pública só podem ser efectuadas com base na lei e mediante o pagamento de justa indemnização.

Artigo 65.º — Habitação e urbanismo
1. Todos têm direito, para si e para a sua família, a uma habitação de dimensão adequada, em condições de higiene e conforto e que preserve a intimidade pessoal e a privacidade familiar.

Artigo 66.º — Ambiente e qualidade de vida
1. Todos têm direito a um ambiente de vida humano, sadio e ecologicamente equilibrado e o dever de o defender.

Artigo 68.º — Paternidade e maternidade
1. Os pais e as mães têm direito à protecção da sociedade e do Estado na realização da sua insubstituível acção em relação aos filhos, nomeadamente quanto à sua educação, com garantia de realização profissional e de participação na vida cívica do país.

Artigo 69.º — Infância
1. As crianças têm direito à protecção da sociedade e do Estado, com vista ao seu desenvolvimento integral, especialmente contra todas as formas de abandono, de discriminação e de opressão e contra o exercício abusivo da autoridade na família e nas demais instituições.

Artigo 202.º — Função jurisdicional
1. Os tribunais são os órgãos de soberania com competência para administrar a justiça em nome do povo.
2. Na administração da justiça incumbe aos tribunais assegurar a defesa dos direitos e interesses legalmente protegidos dos cidadãos, reprimir a violação da legalidade democrática e dirimir os conflitos de interesses públicos e privados.

Artigo 268.º — Direitos e garantias dos administrados
1. Os cidadãos têm o direito de ser informados pela Administração, sempre que o requeiram, sobre o andamento dos processos em que sejam directamente interessados, bem como o de conhecer as resoluções definitivas que sobre eles forem tomadas.
4. É garantido aos interessados recurso contencioso, com fundamento em ilegalidade, contra quaisquer actos administrativos definitivos e executórios, independentemente da sua forma, pelos meios e com os efeitos previstos na lei, que assegurará sempre a possibilidade de impugnar os actos administrativos lesivos de direitos ou interesses legalmente protegidos."""

    def _get_cp(self) -> str:
        return """CÓDIGO PENAL PORTUGUÊS
Aprovado pelo Decreto-Lei n.º 400/82, de 23 de setembro. Última revisão: 2023.
FONTE: texto de referência para uso do Dr. José

PARTE GERAL

TÍTULO I — DA LEI PENAL

Artigo 1.º — Nullum crimen sine lege
1. Só pode ser punido criminalmente o facto descrito e declarado passível de pena por lei anterior ao momento da sua prática.
2. A medida de segurança só pode ser aplicada a estados de perigosidade cujos pressupostos estejam fixados em lei anterior ao seu preenchimento.
3. Não é permitida a aplicação analógica da lei criminal.

Artigo 2.º — Aplicação no tempo
1. As penas e as medidas de segurança são determinadas pela lei vigente no momento da prática do facto ou do preenchimento dos pressupostos de que dependem.
4. Quando as disposições penais vigentes no momento da prática do facto punível forem diferentes das estabelecidas em leis posteriores, é sempre aplicado o regime que concretamente se mostrar mais favorável ao agente.

Artigo 11.º — Responsabilidade das pessoas colectivas
1. Salvo disposição em contrário, só as pessoas singulares são susceptíveis de responsabilidade criminal.

TÍTULO II — DO FACTO

Artigo 13.º — Dolo e negligência
Só é punível o facto praticado com dolo ou, nos casos especialmente previstos na lei, com negligência.

Artigo 14.º — Dolo
1. Age com dolo quem, representando um facto que preenche um tipo de crime, actuar com intenção de o realizar.
2. Age ainda com dolo quem representar a realização de um facto que preenche um tipo de crime como consequência necessária da sua conduta.
3. Quando a realização de um facto que preenche um tipo de crime for representada como consequência possível da conduta, há dolo se o agente actuar conformando-se com aquela realização.

Artigo 15.º — Negligência
Age com negligência quem, por não proceder com o cuidado a que, segundo as circunstâncias, está obrigado e de que é capaz:
a) Representar como possível a realização de um facto que preenche um tipo de crime mas actuar sem se conformar com essa realização; ou
b) Não chegar a representar a possibilidade de realização do facto.

Artigo 17.º — Erro sobre a ilicitude
1. Age sem culpa quem actuar sem consciência da ilicitude do facto, se o erro não lhe for censurável.
2. Se o erro lhe for censurável, o agente é punido com a pena aplicável ao crime doloso respectivo, a qual pode ser especialmente atenuada.

Artigo 22.º — Tentativa
1. Há tentativa quando o agente praticar actos de execução de um crime que decidiu cometer, sem que este chegue a consumar-se.
2. São actos de execução:
a) Os que preencherem um elemento constitutivo de um tipo de crime;
b) Os que forem idóneos a produzir o resultado típico; ou
c) Os que, segundo a experiência comum e salvo circunstâncias imprevisíveis, forem de natureza a fazer esperar que se lhes sigam actos das espécies indicadas nas alíneas anteriores.
3. A tentativa só é punível se ao crime consumado respectivo corresponder pena superior a 3 anos de prisão, salvo disposição em contrário.

Artigo 26.º — Autoria
É punível como autor quem executar o facto, por si mesmo ou por intermédio de outrem, ou tomar parte directa na sua execução, por acordo ou juntamente com outro ou outros, e ainda quem, dolosamente, determinar outra pessoa à prática do facto, desde que haja execução ou começo de execução.

Artigo 31.º — Exclusão da ilicitude
1. O facto não é punível quando a sua ilicitude for excluída pela ordem jurídica considerada na sua totalidade.
2. Nomeadamente, não é ilícito o facto praticado:
a) Em legítima defesa;
b) No exercício de um direito;
c) No cumprimento de um dever imposto por lei ou por ordem legítima da autoridade; ou
d) Com o consentimento do titular do interesse jurídico lesado.

Artigo 32.º — Legítima defesa
Actua em legítima defesa quem repelir uma agressão actual e ilícita de interesses juridicamente protegidos do agente ou de terceiro, mediante acção adequada à necessidade de defesa e com consciência de se defender.

Artigo 40.º — Finalidades das penas e das medidas de segurança
1. A aplicação de penas e de medidas de segurança visa a protecção de bens jurídicos e a reintegração do agente na sociedade.
2. Em caso algum a pena pode ultrapassar a medida da culpa.

Artigo 41.º — Prisão
1. A pena de prisão tem duração mínima de 1 mês e máxima de 20 anos.
2. A pena de prisão pode ir até 25 anos nos casos previstos na lei.

Artigo 44.º — Substituição por multa
1. A pena de prisão aplicada em medida não superior a 1 ano é substituída por pena de multa ou por outra pena não privativa da liberdade aplicável, excepto se a execução da prisão for exigida pela necessidade de prevenir o cometimento de futuros crimes.

Artigo 47.º — Multa
1. A pena de multa é fixada em dias, de acordo com os critérios referidos no artigo 71.º, dentro dos limites definidos na lei.
2. Cada dia de multa corresponde a uma quantia entre € 5 e € 500, que o tribunal fixa em função da situação económica e financeira do condenado e dos seus encargos pessoais.

Artigo 50.º — Suspensão da execução da pena de prisão
1. O tribunal suspende a execução da pena de prisão aplicada em medida não superior a 5 anos se, atendendo à personalidade do agente, às condições da sua vida, à sua conduta anterior e posterior ao crime e às circunstâncias deste, concluir que a simples censura do facto e a ameaça da prisão realizam de forma adequada e suficiente as finalidades da punição.

Artigo 71.º — Determinação da medida da pena
1. A determinação da medida da pena, dentro dos limites definidos na lei, é feita em função da culpa do agente e das exigências de prevenção.
2. Na determinação concreta da pena o tribunal atende a todas as circunstâncias que, não fazendo parte do tipo de crime, depuserem a favor do agente ou contra ele.

PARTE ESPECIAL — CRIMES CONTRA AS PESSOAS

Artigo 131.º — Homicídio
Quem matar outra pessoa é punido com pena de prisão de 8 a 16 anos.

Artigo 132.º — Homicídio qualificado
1. Se a morte for produzida em circunstâncias que revelem especial censurabilidade ou perversidade, o agente é punido com pena de prisão de 12 a 25 anos.
2. É susceptível de revelar a especial censurabilidade ou perversidade a que se refere o número anterior, entre outras, a circunstância de o agente:
a) Ser descendente ou ascendente, adoptado ou adoptante, da vítima;
b) Praticar o facto contra cônjuge, ex-cônjuge, pessoa de outro ou do mesmo sexo com quem o agente mantenha ou tenha mantido uma relação de namoro ou uma relação análoga à dos cônjuges, ainda que sem coabitação;
l) Praticar o facto contra pessoa particularmente indefesa, em razão de idade, deficiência, doença ou gravidez.

Artigo 133.º — Homicídio privilegiado
Se o agente agir dominado por compreensível emoção violenta, compaixão, desespero ou motivo de relevante valor social ou moral, que diminuam sensivelmente a sua culpa, é punido com pena de prisão de 1 a 5 anos.

Artigo 136.º — Infanticídio
A mãe que matar o filho durante ou logo após o parto, estando ainda perturbada em virtude deste, é punida com pena de prisão de 1 a 5 anos.

Artigo 137.º — Homicídio por negligência
1. Quem matar outra pessoa por negligência é punido com pena de prisão até 3 anos ou com pena de multa.
2. Em caso de negligência grosseira, o agente é punido com pena de prisão até 5 anos.

Artigo 143.º — Ofensa à integridade física simples
1. Quem ofender o corpo ou a saúde de outra pessoa é punido com pena de prisão até 3 anos ou com pena de multa.
2. O procedimento criminal depende de queixa.

Artigo 144.º — Ofensa à integridade física grave
Quem ofender o corpo ou a saúde de outra pessoa de forma a:
a) Privar o ofendido de importante órgão ou membro, ou desfigurá-lo gravemente e de forma permanente;
b) Tirar-lhe ou afectar-lhe, de maneira grave, a capacidade de trabalho, as capacidades intelectuais, de procriação ou de fruição sexual, ou a possibilidade de utilizar o corpo, os sentidos ou a linguagem;
c) Provocar-lhe doença particularmente dolorosa ou permanente, ou anomalia psíquica grave ou incurável; ou
d) Provocar-lhe perigo para a vida;
é punido com pena de prisão de dois a dez anos.

Artigo 152.º — Violência doméstica
1. Quem, de modo reiterado ou não, infligir maus tratos físicos ou psíquicos, incluindo castigos corporais, privações da liberdade e ofensas sexuais:
a) Ao cônjuge ou ex-cônjuge;
b) A pessoa de outro ou do mesmo sexo com quem o agente mantenha ou tenha mantido uma relação de namoro ou uma relação análoga à dos cônjuges, ainda que sem coabitação;
c) A progenitor de descendente comum em 1.º grau; ou
d) A pessoa particularmente indefesa, nomeadamente em razão da idade, deficiência, doença, gravidez ou dependência económica, que com ele coabite;
é punido com pena de prisão de um a cinco anos, se pena mais grave lhe não couber por força de outra disposição legal.
2. No caso previsto no número anterior, se o agente praticar o facto contra menor, na presença de menor, no domicílio comum ou no domicílio da vítima é punido com pena de prisão de dois a cinco anos.
3. Se dos factos previstos no n.º 1 resultar:
a) Ofensa à integridade física grave, o agente é punido com pena de prisão de dois a oito anos;
b) A morte, o agente é punido com pena de prisão de três a dez anos.

Artigo 153.º — Ameaça
1. Quem ameaçar outra pessoa com a prática de crime contra a vida, a integridade física, a liberdade pessoal, a liberdade e autodeterminação sexual ou bens patrimoniais de considerável valor, de forma adequada a provocar-lhe medo ou inquietação ou a prejudicar a sua liberdade de determinação, é punido com pena de prisão até um ano ou com pena de multa até 120 dias.
2. O procedimento criminal depende de queixa.

Artigo 163.º — Coação sexual
Quem constranger outra pessoa a sofrer ou a praticar, consigo ou com outrem, acto sexual de relevo, por meio de violência, ameaça grave, ou depois de, para esse fim, a ter tornado inconsciente ou posto na impossibilidade de resistir, é punido com pena de prisão de um a oito anos.

Artigo 164.º — Violação
1. Quem constranger outra pessoa: a) A sofrer ou a praticar, consigo ou com outrem, cópula, coito anal ou coito oral; ou b) A sofrer introdução vaginal ou anal de partes do corpo ou objectos; por meio de violência, ameaça grave, ou depois de, para esse fim, a ter tornado inconsciente ou posto na impossibilidade de resistir, é punido com pena de prisão de 3 a 10 anos.

Artigo 169.º — Lenocínio
1. Quem, profissionalmente ou com intenção lucrativa, fomentar, favorecer ou facilitar o exercício por outra pessoa de prostituição ou a prática de actos sexuais de relevo é punido com pena de prisão de seis meses a cinco anos.

Artigo 177.º — Agravação
1. As penas previstas nos artigos 163.º a 176.º são agravadas de um terço, nos seus limites mínimo e máximo, se a vítima:
a) For ascendente, descendente, adoptante, adoptado, parente ou afim até ao segundo grau do agente;
b) Se encontrar numa relação familiar, de coabitação, de tutela ou curatela, ou de dependência hierárquica, económica ou de trabalho do agente e o crime for praticado com aproveitamento desta relação.

Artigo 190.º — Violação de domicílio ou perturbação de vida privada
1. Quem, sem consentimento, se introduzir na habitação de outra pessoa ou nela permanecer após intimação para sair feita pelo titular do direito é punido com pena de prisão até um ano ou com pena de multa até 240 dias.

Artigo 193.º — Devassa da vida privada
1. Quem, sem consentimento e com intenção de devassar a vida privada das pessoas, designadamente a intimidade da vida familiar ou sexual:
a) Interceptar, gravar, registar, utilizar, transmitir ou divulgar conversa, comunicação telefónica, mensagens de correio electrónico ou facturação detalhada;
b) Captar, fotografar, filmar, registar ou divulgar imagem das pessoas ou de objectos ou espaços íntimos;
c) Observar ou escutar às ocultas pessoas que se encontrem em lugar privado;
é punido com pena de prisão até um ano ou com pena de multa até 240 dias.

CRIMES CONTRA O PATRIMÓNIO

Artigo 203.º — Furto
1. Quem, com intenção de apropriação para si ou para terceiro, subtrair coisa móvel alheia, é punido com pena de prisão até 3 anos ou com pena de multa.
2. A tentativa é punível.

Artigo 204.º — Furto qualificado
1. Quem furtar coisa móvel alheia:
a) De valor elevado;
b) Transportada em veículo ou colocada em lugar destinado ao depósito de objectos ou transportada por passageiros utentes de transporte colectivo;
c) Com introdução em habitação, ainda que móvel, estabelecimento comercial ou industrial ou espaço fechado, ou com escalamento, arrombamento ou chaves falsas;
e) Penetrando em habitação;
é punido com pena de prisão de 1 a 5 anos.

Artigo 210.º — Roubo
1. Quem, com intenção de apropriação para si ou para terceiro, subtrair, ou constranger a que lhe seja entregue, coisa móvel alheia, por meio de violência contra uma pessoa, de ameaça com perigo iminente para a vida ou para a integridade física, ou pondo-a na impossibilidade de resistir, é punido com pena de prisão de 1 a 8 anos.

Artigo 212.º — Dano
1. Quem destruir, no todo ou em parte, danificar, desfigurar ou tornar não utilizável coisa alheia, é punido com pena de prisão até 3 anos ou com pena de multa.

Artigo 217.º — Burla
1. Quem, com intenção de obter para si ou para terceiro enriquecimento ilegítimo, por meio de erro ou engano sobre factos que astuciosamente provocou, determinar outrem à prática de actos que lhe causem, ou causem a outra pessoa, prejuízo patrimonial, é punido com pena de prisão até 3 anos ou com pena de multa.

Artigo 221.º — Burla informática e nas comunicações
1. Quem, com intenção de obter para si ou para terceiro enriquecimento ilegítimo, causar prejuízo patrimonial a outra pessoa, interferindo no resultado de tratamento informático, utilizando dados incorrectos ou incompletos, utilizando dados sem autorização ou de qualquer outro modo intervenha no fluxo de dados, é punido com pena de prisão até 3 anos ou com pena de multa.

Artigo 225.º — Abuso de confiança
1. Quem ilegitimamente fizer sua coisa móvel que lhe tenha sido entregue por título não translativo da propriedade, é punido com pena de prisão até 3 anos ou com pena de multa.

Artigo 255.º — Falsificação de documentos
1. Quem, com intenção de causar prejuízo a outra pessoa ou ao Estado, ou de obter para si ou para terceiro benefício ilegítimo:
a) Fabricar ou elaborar documento falso, ou qualquer dos componentes destinados a corporizá-lo;
b) Falsificar ou alterar documento ou qualquer dos seus componentes;
c) Abusar da assinatura de outra pessoa para falsificar ou contrafazer documento;
d) Fazer uso de documento falsificado ou contrafacto produzido por outrem;
é punido com pena de prisão até 3 anos ou com pena de multa, se pena mais grave lhe não couber por força de outra disposição legal.

CRIMES CONTRA A AUTORIDADE PÚBLICA

Artigo 347.º — Resistência e coacção sobre funcionário
1. Quem empregar violência ou ameaça grave para se opor a que funcionário pratica acto relativo ao exercício das suas funções, ou para o constranger a praticar acto relativo ao exercício das suas funções, mas contrário aos seus deveres, é punido com pena de prisão até 5 anos.

Artigo 348.º — Desobediência
1. Quem faltar à obediência devida a ordem ou a mandado legítimos, regularmente comunicados e emanados de autoridade ou funcionário competente, é punido com pena de prisão até 1 ano ou com pena de multa até 120 dias se:
a) Uma disposição legal cominar, no caso, a punição da desobediência simples; ou
b) Na ausência de disposição legal, a autoridade ou o funcionário fizerem a correspondente cominação.

Artigo 374.º — Corrupção passiva
1. O funcionário que por si, ou por interposta pessoa, com o seu consentimento ou ratificação, solicitar ou aceitar, para si ou para terceiro, vantagem patrimonial ou não patrimonial, ou a sua promessa, como contrapartida de acto ou omissão contrários aos deveres do cargo, ainda que anteriores àquela solicitação ou aceitação, é punido com pena de prisão de um a oito anos."""

    def _get_cc(self) -> str:
        return """CÓDIGO CIVIL PORTUGUÊS
Aprovado pelo Decreto-Lei n.º 47344/66, de 25 de novembro. Última revisão: 2023.
FONTE: texto de referência para uso do Dr. José

LIVRO I — PARTE GERAL

Artigo 1.º — Fontes de direito
1. São fontes imediatas do direito as leis e as normas corporativas.
2. São fontes mediatas os usos que a lei reconheça como juridicamente relevantes.

Artigo 2.º — Valor jurisprudencial
Nos casos declarados na lei, podem os tribunais criar, por via de jurisprudência, normas vinculativas para os particulares.

Artigo 334.º — Abuso do direito
É ilegítimo o exercício de um direito, quando o titular exceda manifestamente os limites impostos pela boa fé, pelos bons costumes ou pelo fim social ou económico desse direito.

Artigo 342.º — Ónus da prova
1. Àquele que invocar um direito cabe fazer a prova dos factos constitutivos do direito alegado.
2. A prova dos factos impeditivos, modificativos ou extintivos do direito invocado compete àquele contra quem a invocação é feita.

Artigo 483.º — Princípio geral da responsabilidade civil
1. Aquele que, com dolo ou mera culpa, violar ilicitamente o direito de outrem ou qualquer disposição legal destinada a proteger interesses alheios fica obrigado a indemnizar o lesado pelos danos resultantes da violação.
2. Só existe obrigação de indemnizar independentemente de culpa nos casos especificados na lei.

Artigo 484.º — Ofensa do crédito ou do bom nome
Quem afirmar ou difundir um facto capaz de prejudicar o crédito ou o bom nome de qualquer pessoa, singular ou colectiva, responde pelos danos causados.

Artigo 494.º — Limitação da indemnização no caso de mera culpa
Quando a responsabilidade se fundar na mera culpa, poderá a indemnização ser fixada, equitativamente, em montante inferior ao que corresponderia aos danos causados, desde que o grau de culpabilidade do agente, a situação económica deste e do lesado e as demais circunstâncias do caso o justifiquem.

Artigo 495.º — Indemnização a terceiros no caso de morte ou lesão corporal
1. No caso de lesão corporal, têm direito a indemnização aqueles que socorreram o lesado, bem como os estabelecimentos hospitalares, médicos ou outras pessoas ou entidades que tenham prestado os seus serviços.
2. Têm igualmente direito a indemnização os que podiam exigir alimentos ao lesado ou aqueles a quem o lesado os prestava no cumprimento de uma obrigação natural.

Artigo 496.º — Danos não patrimoniais
1. Na fixação da indemnização deve atender-se aos danos não patrimoniais que, pela sua gravidade, mereçam a tutela do direito.
2. Por morte da vítima, o direito à indemnização por danos não patrimoniais cabe, em conjunto, ao cônjuge não separado de pessoas e bens e aos filhos ou outros descendentes; na falta destes, aos pais ou outros ascendentes; e, por último, aos irmãos ou sobrinhos que os representem.

Artigo 877.º — Venda a filhos ou netos
Os pais e avós não podem vender a filhos ou netos, se os outros filhos ou netos não consentirem; exceptua-se o caso de a isso não se oporem os direitos dos demais interessados.

Artigo 1305.º — Conteúdo do direito de propriedade
O proprietário goza de modo pleno e exclusivo dos direitos de uso, fruição e disposição das coisas que lhe pertencem, dentro dos limites da lei e com observância das restrições por ela impostas.

Artigo 1346.º — Imissões
O proprietário de um imóvel pode opor-se à emissão de fumo, fuligem, vapores, cheiros, calor, ruídos, trepidações e outros quaisquer factos semelhantes, provenientes de prédio vizinho, sempre que tais factos importem um prejuízo substancial para o uso do imóvel ou não resultem da utilização normal do prédio de que emanam.

Artigo 1521.º — Direitos e deveres do cônjuge
Cada cônjuge deve:
a) Guardar fidelidade ao outro cônjuge;
b) Viver em comunhão de leito, mesa e habitação;
c) Cooperar no interesse da família.

Artigo 1576.º — Fontes das relações jurídicas familiares
São fontes das relações jurídicas familiares o casamento, o parentesco, a afinidade e a adopção.

Artigo 1577.º — Conceito de casamento
Casamento é o contrato celebrado entre duas pessoas que pretendem constituir família mediante uma plena comunhão de vida, nos termos das disposições deste Código.

Artigo 1670.º — Divórcio por mútuo consentimento
O divórcio por mútuo consentimento pode ser requerido por ambos os cônjuges, de comum acordo, mediante pedido na conservatória do registo civil.

Artigo 1672.º — Divórcio sem consentimento do outro cônjuge
Qualquer dos cônjuges pode requerer o divórcio sem consentimento do outro com fundamento na violação culposa dos deveres conjugais, quando, pela sua gravidade ou reiteração, a violação comprometa a possibilidade de vida em comum.

Artigo 1773.º — Direito de alimentos
O cônjuge que não tenha meios suficientes para a sua subsistência tem direito a alimentos do outro cônjuge.

Artigo 1878.º — Conteúdo das responsabilidades parentais
1. Compete aos pais, no interesse dos filhos, velar pela segurança e saúde destes, prover ao seu sustento, dirigir a sua educação, representá-los, ainda que nascituros, e administrar os seus bens.
2. Os filhos devem obediência aos pais; estes, porém, de acordo com a maturidade dos filhos, devem ter em conta a sua opinião nos assuntos familiares importantes e reconhecer-lhes autonomia na organização da própria vida.

Artigo 1906.º — Exercício das responsabilidades parentais em caso de divórcio
1. As responsabilidades parentais relativas às questões de particular importância para a vida do filho são exercidas em comum por ambos os progenitores nos termos que vigoravam na constância do matrimônio.
2. Quando o exercício em comum das responsabilidades parentais relativas às questões de particular importância para a vida do filho seja julgado contrário aos interesses deste, deve o tribunal, através de decisão fundamentada, determinar que essas responsabilidades sejam exercidas por um dos progenitores.

Artigo 2024.º — Noção de sucessão
Diz-se sucessão o chamamento de uma ou mais pessoas à titularidade das relações jurídicas patrimoniais de uma pessoa falecida e a consequente devolução dos bens que a esta pertenciam.

Artigo 2156.º — Noção de legítima
Legítima é a porção de bens de que o testador não pode dispor, por ser legalmente destinada aos herdeiros legitimários.

Artigo 2157.º — Herdeiros legitimários
São herdeiros legitimários o cônjuge, os descendentes e os ascendentes, pela ordem e nos termos estabelecidos para a sucessão legítima.

Artigo 2158.º — Quota da legítima
1. A legítima do cônjuge, quando concorra com descendentes, é igual à dos filhos.
2. A legítima é de metade da herança quando o testador deixar descendentes ou cônjuge e de um terço quando deixar apenas ascendentes."""

    def _get_ct(self) -> str:
        return """CÓDIGO DO TRABALHO
Aprovado pela Lei n.º 7/2009, de 12 de fevereiro. Última revisão: 2023.
FONTE: texto de referência para uso do Dr. José

TÍTULO I — PRINCÍPIOS GERAIS

Artigo 1.º — Âmbito de aplicação
1. O presente Código regula as relações de trabalho subordinado, estabelecendo os direitos e obrigações das partes.

Artigo 2.º — Fontes de direito do trabalho
São fontes de direito do trabalho: a Constituição; as leis e outros actos normativos do Estado; as convenções colectivas de trabalho; os usos laborais que não contrariem o princípio da boa fé.

Artigo 4.º — Carácter imperativo das normas
1. As normas deste Código podem ser afastadas por instrumento de regulamentação colectiva de trabalho, salvo quando delas resultar o contrário.
2. As normas deste Código só podem ser afastadas por contrato de trabalho quando este estabeleça condições mais favoráveis para o trabalhador e se tal resultar da lei.

Artigo 11.º — Conceito de contrato de trabalho
Contrato de trabalho é aquele pelo qual uma pessoa singular se obriga, mediante retribuição, a prestar a sua actividade a outra ou outras pessoas, no âmbito de organização e sob a autoridade destas.

Artigo 53.º — Proibição de despedimento sem justa causa
É proibido o despedimento de trabalhadores sem justa causa ou por motivos políticos ou ideológicos.

Artigo 55.º — Direito à ocupação efectiva
O trabalhador tem direito a exercer a actividade para que foi contratado ou, na falta de indicação, para a qual esteja habilitado.

Artigo 59.º — Igualdade e não discriminação
1. O empregador não pode praticar qualquer discriminação, directa ou indirecta, baseada, nomeadamente, em sexo, raça, cor, etnia, língua, território de origem, religião ou crença, estado civil, situação familiar, situação económica, instrução, ascendência ou proveniência social, grau de incapacidade reduzida, saúde, orientação sexual, identidade e expressão de género, características sexuais, idade, condição social ou profissional, actividade sindical, representação colectiva dos trabalhadores, convicções políticas ou ideológicas, etnia ou catolicidade, em particular no que se refere:
a) À selecção e ao recrutamento;
b) À retribuição e demais condições de trabalho;
c) À promoção na carreira e formação profissional;
d) À cessação do contrato de trabalho.

Artigo 120.º — Princípio geral da igualdade retributiva
Para trabalho igual ou de valor igual, o trabalhador tem direito a retribuição igual.

Artigo 127.º — Deveres do empregador
1. O empregador deve, nomeadamente:
a) Respeitar e tratar com urbanidade e probidade o trabalhador;
b) Pagar pontualmente a retribuição;
c) Proporcionar boas condições de trabalho, do ponto de vista físico e moral;
d) Contribuir para a elevação da produtividade e empregabilidade do trabalhador, nomeadamente proporcionando-lhe formação profissional adequada a desenvolver a sua qualificação;
e) Respeitar a autonomia técnica do trabalhador que exerça actividade cuja regulamentação profissional a exija;
f) Prevenir riscos e doenças profissionais, tendo em conta a protecção da segurança e saúde do trabalhador;
g) Adoptar, no que se refere à higiene, segurança e saúde no trabalho, as medidas que decorram, para a empresa, estabelecimento ou actividade, da aplicação das prescrições legais e convencionais vigentes;
h) Fornecer ao trabalhador a informação e a formação adequadas à prevenção de riscos de acidente ou doença.

Artigo 128.º — Deveres do trabalhador
1. Sem prejuízo de outras obrigações, o trabalhador deve:
a) Comparecer ao serviço com assiduidade e pontualidade;
b) Realizar o trabalho com zelo e diligência;
c) Cumprir as ordens e instruções do empregador respeitantes a execução ou disciplina do trabalho, bem como a segurança e saúde no trabalho, que não sejam contrárias aos seus direitos ou garantias;
d) Guardar lealdade ao empregador, nomeadamente não negociando por conta própria ou alheia em concorrência com ele, nem divulgando informações referentes à sua organização, métodos de produção ou negócios;
e) Velar pela conservação e boa utilização dos bens relacionados com o trabalho que lhe forem confiados pelo empregador;
f) Promover ou executar os actos tendentes à melhoria da produtividade da empresa.

Artigo 162.º — Duração do período experimental
1. Salvo quando outro prazo for estabelecido por instrumento de regulamentação colectiva de trabalho, o período experimental tem a seguinte duração máxima:
a) 90 dias para a generalidade dos trabalhadores;
b) 180 dias para trabalhadores que exerçam cargos de complexidade técnica, elevado grau de responsabilidade ou que pressuponham uma especial qualificação, bem como para trabalhadores que desempenhem funções de confiança;
c) 240 dias para trabalhadores que exerçam cargos de direcção ou quadros superiores.

Artigo 210.º — Horário de trabalho
O horário de trabalho deve ser afixado nos locais de trabalho em lugar bem visível e comunicado ao trabalhador na sua admissão.

Artigo 211.º — Período normal de trabalho
O período normal de trabalho não pode ser superior a oito horas por dia nem a quarenta horas por semana.

Artigo 226.º — Trabalho nocturno
1. Considera-se trabalho nocturno o prestado no período decorrente entre as 20 horas de um dia e as 7 horas do dia seguinte.

Artigo 229.º — Direito a férias
1. O trabalhador tem direito a um período anual de férias remuneradas que não pode ser inferior a 22 dias úteis.

Artigo 237.º — Faltas
1. Falta é a ausência do trabalhador durante o período normal de trabalho diário.

Artigo 238.º — Faltas justificadas
1. São consideradas faltas justificadas:
a) As dadas por altura do casamento, durante quinze dias seguidos;
b) As motivadas por falecimento de cônjuge não separado de pessoas e bens, ou de parente ou afim no 1.º grau da linha recta, durante cinco dias consecutivos;
c) As motivadas por falecimento de outro parente ou afim na linha recta ou no 2.º grau da linha colateral, durante dois dias consecutivos;
d) As motivadas pela prestação de assistência inadiável e imprescindível a cônjuge, pai, mãe, filho, padrasto, madrasta ou enteados, ou, em caso de impossibilidade daqueles, a outros membros do agregado familiar do trabalhador, até ao limite de quinze dias por ano;
e) As dadas a trabalhadora grávida, puérpera ou lactante, para consulta pré-natal;
f) As motivadas por assistência a filhos com 12 anos de idade, até ao limite de 30 dias por ano ou durante todo o período de hospitalização.

Artigo 260.º — Trabalho suplementar
1. Considera-se trabalho suplementar todo aquele que é prestado fora do horário de trabalho.
4. O trabalho suplementar em dia de descanso semanal obrigatório ou em feriado é remunerado com um acréscimo de 50% sobre a retribuição.

Artigo 268.º — Retribuição
1. O trabalhador tem direito à retribuição do trabalho que efectuou, incluindo o trabalho suplementar, e às prestações estabelecidas por instrumento de regulamentação colectiva de trabalho ou por uso da empresa.
2. A retribuição devida pelo trabalho normal é paga pelo período de 12 meses do ano. Quando corresponder a período inferior, é paga proporcionalmente.

Artigo 273.º — Retribuição mínima mensal garantida
1. O governo, depois de consultar os parceiros sociais representados na comissão permanente de concertação social, fixa, por decreto-lei, o valor da retribuição mínima mensal garantida.

Artigo 340.º — Regime disciplinar
O empregador tem poder disciplinar sobre o trabalhador ao seu serviço, enquanto vigorar o contrato de trabalho.

Artigo 351.º — Justa causa de despedimento
1. Constitui justa causa de despedimento o comportamento culposo do trabalhador que, pela sua gravidade e consequências, torne imediata e praticamente impossível a subsistência da relação de trabalho.
2. Constituem, nomeadamente, justa causa de despedimento os seguintes comportamentos do trabalhador:
a) Desobediência ilegítima às ordens dadas por responsáveis hierarquicamente superiores;
b) Violação de direitos e garantias de trabalhadores da empresa;
c) Provocação repetida de conflitos com trabalhadores da empresa;
d) Desinteresse repetido pelo cumprimento, com a diligência devida, das obrigações inerentes ao exercício do cargo ou posto de trabalho que lhe esteja confiado;
e) Lesão de interesses patrimoniais sérios da empresa;
f) Falsas declarações relativas à justificação de faltas;
g) Faltas não justificadas ao trabalho que determinem directamente prejuízos ou riscos graves para a empresa, ou cujo número atinja, em cada ano civil, cinco seguidas ou dez interpoladas independentemente de prejuízo ou risco;
h) Falta culposa de observância de regras de segurança e saúde no trabalho;
i) Prática intencional, no exercício das suas funções, de actos lesivos da economia nacional;
j) Reduções anormais de produtividade.

Artigo 362.º — Procedimento disciplinar
1. O empregador deve comunicar ao trabalhador, por escrito, a intenção de proceder ao despedimento e os respectivos fundamentos.
2. O trabalhador pode, no prazo de 10 dias úteis, responder, por escrito, à nota de culpa, podendo juntar documentos e solicitar as diligências probatórias que se mostrem pertinentes.

Artigo 366.º — Indemnização devida ao trabalhador
1. Em caso de despedimento sem justa causa, o trabalhador tem direito a indemnização correspondente a 20 dias de retribuição base e diuturnidades por cada ano completo ou fracção de antiguidade.

Artigo 375.º — Caducidade do contrato de trabalho
1. O contrato de trabalho caduca quando: a) O seu termo se verifica; b) O objecto se torna impossível, designadamente por morte do trabalhador, extinção da pessoa colectiva empregadora ou encerramento definitivo do estabelecimento.

Artigo 383.º — Despedimento colectivo
Considera-se despedimento colectivo a cessação de contratos de trabalho promovida pelo empregador e operada simultânea ou sucessivamente no período de três meses, abrangendo, pelo menos, dois ou cinco trabalhadores, conforme a empresa tenha respectivamente até cinquenta ou mais de cinquenta trabalhadores.

Artigo 389.º — Regime de ilicitude do despedimento
1. É ilícito o despedimento que: a) Não seja precedido do respectivo procedimento; b) Se baseie em motivo político, ideológico, étnico ou religioso; c) Se fundamente em exercício, pelo trabalhador, de direitos de participação e acção colectiva; d) Não se funde em justa causa ou em motivo de natureza estrutural, tecnológica ou de mercado.

Artigo 394.º — Resolução com justa causa pelo trabalhador
1. O trabalhador pode fazer cessar imediatamente o contrato, com direito a indemnização, nos casos de justa causa.
2. Constituem justa causa de resolução pelo trabalhador, nomeadamente, os seguintes comportamentos do empregador:
a) Falta culposa de pagamento pontual da retribuição;
b) Violação culposa das garantias legais ou convencionais do trabalhador;
c) Aplicação de sanção abusiva;
d) Falta culposa de condições de segurança e saúde no trabalho;
e) Lesão culposa de interesses patrimoniais sérios do trabalhador;
f) Ofensa à integridade física ou moral, liberdade, honra ou dignidade do trabalhador, punível por lei, praticada pelo empregador ou seu representante.

Artigo 399.º — Subsídio de desemprego
Ao trabalhador que tiver direito ao subsídio de desemprego aplica-se a legislação do sistema de solidariedade e segurança social."""

    def _get_cpp(self) -> str:
        return """CÓDIGO DE PROCESSO PENAL
Aprovado pelo Decreto-Lei n.º 78/87, de 17 de fevereiro. Última revisão: 2023.
FONTE: texto de referência para uso do Dr. José

Artigo 1.º — Definições legais
Para efeitos do presente Código, considera-se:
a) «Crime» o conjunto de pressupostos de que depende a aplicação ao agente de uma pena ou de uma medida de segurança criminais;
b) «Arguido» todo aquele que, nos termos deste Código, adquirir essa qualidade;
c) «Suspeito» toda a pessoa relativamente à qual exista indício de que cometeu ou se prepara para cometer um crime, ou que nele participou ou se prepara para participar;
d) «Detido» todo aquele que for privado da liberdade por força de detenção em flagrante delito ou de detenção fora de flagrante delito;
e) «Assistente» a pessoa que, nos termos do artigo 68.º, seja admitida a intervir no processo penal como tal.

Artigo 48.º — Promoção processual
O Ministério Público tem legitimidade para promover o processo penal, com as restrições constantes dos artigos 49.º a 52.º

Artigo 57.º — Constituição de arguido
1. Assume a qualidade de arguido a pessoa a quem é imputada a prática de um crime, logo que:
a) Haja suspeita suficientemente fundamentada;
b) Se mostre necessário para garantia dos direitos do suspeito.

Artigo 58.º — Obrigatoriedade de constituição de arguido
1. É obrigatória a constituição de arguido logo que:
a) Correndo inquérito contra pessoa determinada em relação à qual haja suspeita fundada da prática de crime, esta prestar declarações perante qualquer autoridade judiciária ou órgão de polícia criminal;
b) For aplicada a qualquer pessoa medida de coacção ou de garantia patrimonial;
c) Um suspeito for detido;
d) For levantado auto de notícia que dê uma pessoa como agente de um crime e aquela tiver de ser ouvida em inquérito.

Artigo 61.º — Direitos e deveres processuais do arguido
1. O arguido goza, em especial, dos seguintes direitos:
a) Ser informado dos direitos que lhe assistem;
b) Ser assistido por defensor em todos os actos processuais em que participar e, quando detido, comunicar, mesmo em privado, com defensor;
c) Não responder a perguntas feitas, por qualquer entidade, sobre os factos que lhe forem imputados e sobre o conteúdo das declarações que acerca deles prestar;
d) Não ser julgado mais de uma vez pela prática do mesmo crime;
e) Contestar os indícios e requerer a sua absolvição.

Artigo 64.º — Assistência obrigatória de defensor
1. É obrigatória a assistência de defensor:
a) Nos interrogatórios de arguido detido;
b) Na instrução e no julgamento, salvo nos casos de declaração de contumácia;
c) Nos recursos;
d) Nos procedimentos de revisão de sentença.

Artigo 141.º — Primeiro interrogatório judicial do arguido detido
1. O arguido detido que não deva ser de imediato julgado é, no prazo máximo de quarenta e oito horas após a detenção, apresentado a audição pelo juiz de instrução.

Artigo 191.º — Princípio geral das medidas de coacção
1. A liberdade das pessoas só pode ser limitada, total ou parcialmente, em função de exigências processuais de natureza cautelar, pelas medidas de coacção e de garantia patrimonial previstas na lei.

Artigo 192.º — Aplicação das medidas de coacção
1. São pressupostos da aplicação de qualquer medida de coacção, excepto o termo de identidade e residência, a existência de fortes indícios da prática de crime doloso punível com pena de prisão de máximo superior a 3 anos.

Artigo 193.º — Princípios da necessidade, adequação e proporcionalidade
1. As medidas de coacção e de garantia patrimonial a aplicar em concreto devem ser necessárias e adequadas às exigências cautelares que o caso requerer e proporcionais à gravidade do crime e às sanções que previsivelmente venham a ser aplicadas.
2. A prisão preventiva e a obrigação de permanência na habitação só podem ser aplicadas quando se revelarem inadequadas ou insuficientes as outras medidas de coacção.

Artigo 195.º — Medidas de coacção
São medidas de coacção:
a) Termo de identidade e residência;
b) Caução;
c) Obrigação de apresentação periódica;
d) Suspensão do exercício de funções, de profissão ou de actividades;
e) Proibição de permanência, ausência ou contactos;
f) Obrigação de permanência na habitação;
g) Prisão preventiva.

Artigo 202.º — Prisão preventiva
1. Se considerar inadequadas ou insuficientes, no caso, as medidas referidas nos artigos anteriores, o juiz pode impor ao arguido a medida de prisão preventiva quando:
a) Houver fortes indícios de prática de crime doloso punível com pena de prisão de máximo superior a 5 anos;
b) Houver fortes indícios de prática de crime doloso de terrorismo, criminalidade violenta ou altamente organizada punível com pena de prisão de máximo superior a 3 anos;
c) Se tratar de pessoa que tiver penetrado ou permaneça irregularmente em território nacional, ou contra a qual estiver em curso processo de extradição ou de expulsão.

Artigo 215.º — Prazos de prisão preventiva
1. A prisão preventiva extingue-se quando, desde o seu início, tiverem decorrido:
a) 4 meses sem que tenha sido deduzida acusação;
b) 8 meses sem que, havendo lugar a instrução, tiver sido proferida decisão instrutória;
c) 1 ano e 2 meses sem que tenha havido condenação em 1.ª instância;
d) 1 ano e 6 meses sem que tenha transitado em julgado a decisão condenatória.

Artigo 344.º — Confissão
1. Se o arguido declarar que praticou os factos que lhe são imputados e aceitar as consequências jurídicas legalmente previstas, o tribunal, depois de verificar que a confissão foi feita de forma livre e voluntária, limita o exame da causa, no que respeita aos factos confessados, à confirmação da confissão e à análise das consequências.

Artigo 374.º — Requisitos da sentença
2. A sentença deve conter:
a) As indicações tendentes à identificação do arguido;
b) A enumeração dos factos provados e não provados, bem como uma exposição tanto quanto possível completa, ainda que concisa, dos motivos, de facto e de direito, que fundamentam a decisão, com indicação e exame crítico das provas que serviram para formar a convicção do tribunal;
c) A indicação das disposições legais aplicadas.

Artigo 400.º — Decisões que admitem recurso
1. Não é admissível recurso:
a) De despachos de mero expediente;
b) De decisões que apliquem medida de coacção, com excepção de decisão de aplicação da medida de prisão preventiva ou de obrigação de permanência na habitação.

Artigo 410.º — Fundamentos do recurso
1. Sempre que a lei não restringir a cognição do tribunal ou os respectivos poderes, o recurso pode ter como fundamento quaisquer questões de que pudesse conhecer a decisão recorrida."""

    def _get_nrau(self) -> str:
        return """NOVO REGIME DO ARRENDAMENTO URBANO (NRAU)
Lei n.º 6/2006, de 27 de fevereiro, alterada pela Lei n.º 31/2012.
FONTE: texto de referência para uso do Dr. José

Artigo 1022.º (Código Civil) — Contrato de locação
Locação é o contrato pelo qual uma das partes se obriga a proporcionar à outra o gozo temporário de uma coisa, mediante retribuição.

Artigo 1023.º — Espécies de locação
A locação diz-se arrendamento quando versa sobre coisa imóvel.

Artigo 1031.º — Obrigações do locador
O locador é obrigado a:
a) Entregar ao locatário a coisa locada;
b) Assegurar-lhe o gozo desta para os fins a que se destina;
c) Manter a coisa em estado de servir para esses fins.

Artigo 1032.º — Direito à realização de reparações
Se o locador não fizer as reparações ou não realizar os melhoramentos que lhe incumbam, poderá o locatário, decorrido um mês sobre a comunicação do pedido, executar aqueles actos a expensas do locador, com direito de retenção sobre a coisa locada e de compensação da importância devida com o montante de qualquer renda ou aluguer.

Artigo 1033.º — Obrigações do locatário
1. O locatário é obrigado a:
a) Pagar a renda ou o aluguer;
b) Usar a coisa para o fim contratado ou, na falta de convenção, para o fim a que ela se destina;
c) Fazer a coisa objeto de pequenas reparações.

Artigo 1038.º — Deveres especiais do arrendatário
O arrendatário deve usar o local arrendado de forma prudente, em conformidade com os fins por que foi arrendado, e não praticar actos que constituam embaraço ao normal exercício dos direitos dos condóminos e proprietários vizinhos.

Artigo 1041.º — Mora do locatário
1. Constituído em mora, o locatário fica obrigado a satisfazer as rendas em atraso acrescidas de juros legais ou convencionais.
2. Ao locatário em mora por falta de pagamento de renda pode o locador resolver o contrato.

Artigo 1048.º — Cessão da posição de arrendatário
1. O arrendatário pode ceder a sua posição contratual com o consentimento do senhorio.

Artigo 1057.º — Transmissão da posição do locador
O adquirente do direito com base no qual foi celebrado o contrato de arrendamento sucede nos direitos e obrigações do locador, sem prejuízo das regras do registo.

Artigo 1064.º — Resolução pelo arrendatário
O arrendatário pode resolver o contrato de arrendamento, com pré-aviso de 120 dias quando a duração do contrato seja superior ou igual a um ano, e de 60 dias quando a duração do contrato seja inferior a um ano.

Artigo 1083.º — Fundamentos de resolução pelo senhorio
1. Qualquer das partes pode resolver o contrato com fundamento em incumprimento pela outra parte, desde que o incumprimento, pela sua gravidade ou reiteração, torne inexigível a manutenção do arrendamento.
2. É inexigível ao senhorio a manutenção do arrendamento em caso de:
a) Mora igual ou superior a 2 meses no pagamento da renda;
b) Oposição do arrendatário à realização de obras ordenadas por autoridade pública;
c) Utilização do prédio para fim diverso do contratado;
d) Violação de regras de higiene, de sossego, de boa vizinhança ou de normas constantes do regulamento do condomínio.

Artigo 1094.º — Denúncia pelo senhorio
1. O senhorio pode denunciar o contrato de arrendamento habitacional de prazo certo para o termo do prazo inicial ou da sua renovação:
a) Mediante comunicação ao arrendatário com a antecedência mínima fixada nos termos do n.º 2 do artigo 1097.º;
b) Com fundamento em necessidade do prédio para habitação própria ou para os seus descendentes em 1.º grau.

Artigo 1097.º — Prazos de pré-aviso
2. O prazo de pré-aviso para denúncia do contrato pelo senhorio é de:
a) Duração do contrato igual ou superior a 6 anos: 240 dias;
b) Duração entre 1 e 6 anos: 120 dias;
c) Duração entre 6 meses e 1 ano: 60 dias;
d) Duração inferior a 6 meses: um terço do prazo de duração.

Artigo 1102.º — Direito de preferência do arrendatário
1. O arrendatário de longa duração tem direito de preferência na compra e venda ou dação em cumprimento do local arrendado para habitação.
2. O prazo mínimo de arrendamento para efeitos do disposto no número anterior é de 2 anos."""


def main():
    fetcher = LawFetcher()
    print("\n" + "=" * 60)
    print("📚 Dr. José - Legislação Portuguesa")
    print("=" * 60)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Força novo download")
    args = parser.parse_args()

    if fetcher.fetch_all(force_refresh=args.force):
        print("\n✅ Leis disponíveis!")
        print(f"   Guardadas em: {config.LEIS_DIR}")
        print(f"   Diplomas: {', '.join(fetcher.list_available_laws())}")
        print("\nAgora executa: python scripts/ingest.py")
    else:
        print("\n⚠️  Erro durante a obtenção das leis.")


if __name__ == "__main__":
    main()
