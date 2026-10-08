#!/usr/bin/env python3
"""Revisão jurídico-pedagógica controlada do banco de contribuição confederativa.

Executar na raiz do repositório Legis Lectiones:
  python revisar_contribuicao_confederativa.py --check
  python revisar_contribuicao_confederativa.py

Não altera outros bancos, feedback, som, Cloudflare nem engajamento.
"""
import argparse
import collections
import copy
import hashlib
import json
import random
import shutil
from pathlib import Path

DATA_PATH = Path("labour-law/contribuicao-confederativa.json")
HTML_PATH = Path("labour-law/contribuicao-confederativa.html")
BACKUP_PATH = Path(".review-backups/contribuicao-confederativa.antes-da-revisao.json")
VERSION = "3.0-revisado-2026-10"

# Seleção por objetivo formativo: 60 questões, com cobertura dos 9 eixos.
KEEP = [
    "Q001", "Q002", "Q003", "Q007", "Q008",
    "Q012", "Q013", "Q015", "Q016", "Q018", "Q019", "Q020", "Q021",
    "Q022", "Q023", "Q024", "Q028", "Q031", "Q033", "Q034",
    "Q035", "Q037", "Q038", "Q043", "Q044",
    "Q045", "Q047", "Q049", "Q050", "Q052", "Q054", "Q056", "Q057",
    "Q059", "Q060", "Q113",
    "Q061", "Q064", "Q065", "Q066", "Q067", "Q072", "Q074", "Q097",
    "Q076", "Q077", "Q078", "Q082", "Q084", "Q098",
    "Q085", "Q088", "Q091", "Q093", "Q095",
    "Q096", "Q099", "Q102", "Q104", "Q105",
]
assert len(KEEP) == len(set(KEEP)) == 60

# Os patches são por ID, nunca por índice da lista.
# Distratores são redigidos antes do embaralhamento, com gabarito no índice 0.
PATCH = {
    "Q001": {
        "prompt": "Por que a denominação “taxa confederativa” é tecnicamente imprecisa?",
        "options": [
            "Porque sugere a taxa como espécie tributária, embora a contribuição confederativa tenha natureza não tributária.",
            "Porque confunde a contribuição confederativa com a contribuição assistencial prevista em instrumento coletivo.",
            "Porque a expressão faria da federação a única destinatária da arrecadação.",
            "Porque substituiria a deliberação assemblear por uma decisão exclusiva da confederação."
        ],
        "explanation": "A palavra 'taxa', em sentido técnico-tributário, designa espécie de tributo. A contribuição confederativa prevista no art. 8º, IV, da Constituição não é uma taxa tributária. A classificação depende de seu regime jurídico, e não do rótulo.",
    },
    "Q002": {
        "prompt": "Qual finalidade caracteriza a contribuição confederativa?",
        "explanation": "Sua finalidade constitucional é o custeio do sistema confederativo da representação sindical (art. 8º, IV, da Constituição), distinto do financiamento da negociação coletiva próprio da contribuição assistencial.",
    },
    "Q003": {
        "prompt": "Quais entidades integram o sistema confederativo sindical?",
        "explanation": "O sistema confederativo organiza-se em sindicato, federação e confederação. Centrais sindicais e conselhos profissionais não se confundem com essa estrutura.",
    },
    "Q007": {
        "explanation": "O art. 8º, IV, da Constituição refere-se ao custeio do sistema confederativo, integrado por sindicatos, federações e confederações.",
    },
    "Q008": {
        "prompt": "Julgue as afirmações sobre a natureza e a finalidade da contribuição confederativa.",
        "statements": [
            {"text": "A contribuição confederativa tem por finalidade o custeio do sistema confederativo sindical.", "answer": True},
            {"text": "A contribuição confederativa é uma taxa tributária instituída pela assembleia geral.", "answer": False},
            {"text": "O sistema confederativo é formado por sindicatos, federações e confederações.", "answer": True},
            {"text": "A contribuição confederativa pode ser exigida de empregados não filiados apenas porque integram a categoria.", "answer": False},
        ],
        "explanation": "O art. 8º, IV, define a finalidade; a Súmula Vinculante 40 limita a exigibilidade aos filiados. A assembleia não institui tributos.",
    },
    "Q012": {
        "prompt": "Uma convenção coletiva estabelece contribuição destinada a custear a negociação realizada pelo sindicato. Qual é a modalidade?",
        "explanation": "A contribuição assistencial se relaciona ao financiamento da atuação negocial e assistencial. Pelo Tema 935 do STF, pode ser prevista em acordo ou convenção coletiva inclusive para não filiados, desde que assegurado o direito de oposição.",
    },
    "Q013": {
        "prompt": "Por que a contribuição confederativa e a assistencial não são a mesma modalidade?",
        "options": [
            "Porque possuem finalidades e regimes de exigibilidade distintos, ainda que ambas possam existir no sistema sindical.",
            "Porque a confederativa substitui automaticamente a assistencial quando aprovada em assembleia.",
            "Porque a assistencial depende sempre da filiação, enquanto a confederativa pode ser cobrada de toda a categoria.",
            "Porque a assistencial é espécie tributária e a confederativa é mensalidade associativa.",
        ],
        "explanation": "A confederativa custeia a estrutura confederativa e só é exigível de filiados (SV 40); a assistencial financia a atuação sindical e pode alcançar não filiados, desde que respeitado o direito de oposição (Tema 935). A coexistência não dispensa os requisitos de cada uma.",
    },
    "Q015": {
        "prompt": "Ao comparar a contribuição sindical legal e a confederativa, qual afirmação respeita a mudança ocorrida em 2017?",
        "options": [
            "A sindical tinha cobrança compulsória antes da Reforma e passou a depender de autorização prévia e expressa; a confederativa é não tributária e exigível dos filiados.",
            "A Reforma de 2017 transformou a contribuição confederativa de tributo obrigatório em cobrança voluntária.",
            "A sindical permaneceu compulsória para não filiados, enquanto a confederativa passou a ter natureza tributária.",
            "As duas modalidades foram extintas pela Reforma, restando apenas a mensalidade associativa.",
        ],
        "explanation": "Não se deve transferir à confederativa a mudança ocorrida na contribuição sindical. Antes de 2017, a sindical era legalmente compulsória e recebia tratamento tributário; após a Lei 13.467/2017 passou a exigir autorização prévia e expressa. A confederativa conserva natureza não tributária e a limitação da SV 40.",
    },
    "Q016": {
        "prompt": "Qual diferença separa a mensalidade associativa da contribuição confederativa?",
        "explanation": "A mensalidade decorre do vínculo associativo e das regras estatutárias; a confederativa tem fundamento no art. 8º, IV, da Constituição, fixação assemblear e destinação ao sistema confederativo.",
    },
    "Q018": {
        "prompt": "A contribuição {{blank}} está ligada à negociação coletiva e à atuação sindical; a contribuição {{blank}} custeia a estrutura de sindicatos, federações e confederações.",
        "explanation": "Assistencial: atuação sindical e negociação coletiva, conforme o Tema 935. Confederativa: custeio do sistema confederativo, exigível apenas de filiados segundo a SV 40.",
    },
    "Q019": {
        "prompt": "No modelo anterior à Reforma Trabalhista de 2017, a contribuição sindical compulsória era classificada como de natureza {{blank}}; já a contribuição confederativa tem natureza {{blank}}.",
        "answers": ["tributária", "privada"],
        "explanation": "A qualificação tributária da sindical refere-se ao regime histórico de compulsoriedade. A Reforma de 2017 condicionou sua cobrança à autorização prévia e expressa. A contribuição confederativa não se confunde com a sindical e não tem natureza tributária.",
    },
    "Q020": {
        "prompt": "Julgue as distinções entre quatro modalidades de contribuição sindical.",
        "statements": [
            {"text": "A mensalidade associativa decorre do vínculo de filiação e das regras internas da entidade.", "answer": True},
            {"text": "A contribuição confederativa pode ser exigida de qualquer integrante da categoria, mesmo não filiado.", "answer": False},
            {"text": "Após 2017, o pagamento da contribuição sindical legal exige autorização prévia e expressa.", "answer": True},
            {"text": "No Tema 935, o STF condiciona a contribuição assistencial de não filiados ao direito de oposição.", "answer": True},
        ],
        "explanation": "As quatro modalidades têm fundamentos diferentes. SV 40: confederativa limitada aos filiados; Lei 13.467/2017: sindical dependente de autorização; Tema 935: assistencial com direito de oposição; mensalidade: filiação.",
    },
    "Q021": {
        "prompt": "Relacione cada cobrança ao seu fundamento ou finalidade.",
        "cards": [
            {"id": "c1", "text": "Custeio do sistema confederativo; exigível dos filiados (SV 40).", "zone": "conf"},
            {"id": "c2", "text": "Atuação sindical e negociação coletiva; Tema 935 e direito de oposição.", "zone": "assist"},
            {"id": "c3", "text": "Vínculo associativo e regras estatutárias.", "zone": "mens"},
            {"id": "c4", "text": "Previsão legal; após 2017, autorização prévia e expressa.", "zone": "sind"},
        ],
        "explanation": "Uma modalidade não adquire o regime jurídico de outra simplesmente por receber o mesmo nome genérico de 'contribuição'.",
    },
    "Q022": {
        "prompt": "Qual é a natureza jurídica da contribuição confederativa?",
        "options": [
            "Não tributária: decorre de deliberação sindical e só é exigível dos filiados ao sindicato respectivo.",
            "Tributária: decorre de lançamento obrigatório realizado pela administração fiscal.",
            "Tributária: sua natureza mudou apenas com a Reforma Trabalhista de 2017.",
            "Previdenciária: sua arrecadação integra o orçamento da seguridade social.",
        ],
        "explanation": "A contribuição confederativa prevista no art. 8º, IV, da CF é não tributária. A filiação delimita a exigibilidade (SV 40). Isso não significa que cada associado possa ignorar individualmente uma deliberação válida da entidade.",
    },
    "Q023": {
        "prompt": "Qual elemento impede que a assembleia sindical transforme a contribuição confederativa em tributo?",
        "options": [
            "A assembleia não detém competência tributária para instituir uma exação estatal compulsória.",
            "A assembleia pode instituir tributos, mas não definir a base de cálculo.",
            "A natureza tributária depende apenas da periodicidade anual da cobrança.",
            "A natureza tributária depende exclusivamente do nome escolhido para a contribuição.",
        ],
        "explanation": "A assembleia sindical exerce autonomia associativa, mas não competência tributária. A contribuição confederativa tem fundamento constitucional próprio e natureza não tributária.",
    },
    "Q024": {
        "prompt": "Por que a autonomia sindical não equivale à competência para instituir tributos?",
        "options": [
            "Porque a autonomia autoriza decisões associativas dentro da ordem jurídica, mas não confere competência tributária estatal.",
            "Porque somente as federações sindicais podem instituir tributos para suas categorias.",
            "Porque a competência tributária sindical depende de aprovação prévia do Ministério do Trabalho.",
            "Porque a autonomia sindical permite cobrar tributos apenas dos empregados filiados.",
        ],
        "explanation": "A autonomia sindical permite autorregulação associativa, observados a Constituição e os estatutos; não se confunde com a competência tributária atribuída constitucionalmente aos entes políticos.",
    },
    "Q028": {
        "prompt": "O uso da palavra “contribuição” basta para classificar uma cobrança como tributo?",
        "options": [
            "Não. É necessário examinar o fundamento jurídico e a natureza da obrigação, não apenas sua denominação.",
            "Sim. Todas as contribuições previstas no texto constitucional são tributos.",
            "Sim, desde que o recolhimento ocorra em periodicidade anual.",
            "Não. Tributos nunca podem conter a palavra 'contribuição' em sua denominação.",
        ],
        "explanation": "A palavra 'contribuição' aparece em institutos de naturezas diferentes. A confederativa é não tributária, diferentemente do tratamento histórico dado à contribuição sindical compulsória.",
    },
    "Q031": {
        "prompt": "O sindicato possui {{blank}} para deliberar sobre seus interesses associativos, mas não tem {{blank}} tributária para instituir tributos.",
        "answers": ["autonomia", "competência"],
        "explanation": "A competência tributária é atribuída pela Constituição aos entes políticos, não à assembleia sindical.",
    },
    "Q033": {
        "prompt": "Julgue as consequências da natureza não tributária da contribuição confederativa.",
        "statements": [
            {"text": "A contribuição confederativa é tributo compulsório criado por deliberação assemblear.", "answer": False},
            {"text": "A deliberação assemblear pode vincular os associados, observadas as regras aplicáveis.", "answer": True},
            {"text": "O simples inadimplemento da contribuição confederativa gera inscrição automática em dívida ativa tributária.", "answer": False},
            {"text": "A não filiação impede a exigibilidade da contribuição confederativa ao integrante da categoria.", "answer": True},
        ],
        "explanation": "Natureza não tributária não significa inexistência de obrigações associativas: o limite da exigibilidade é a filiação, conforme a Súmula Vinculante 40.",
    },
    "Q034": {
        "prompt": "Classifique os elementos segundo o regime jurídico correspondente.",
        "explanation": "A contribuição confederativa não decorre de lançamento tributário nem ingressa, por sua simples inadimplência, no regime da execução fiscal. Sua fixação está associada à autonomia sindical e ao custeio confederativo.",
    },
    "Q035": {
        "prompt": "Qual é o objeto principal da contribuição confederativa?",
        "explanation": "O art. 8º, IV, da Constituição destina a contribuição confederativa ao custeio do sistema confederativo da representação sindical.",
    },
    "Q037": {
        "prompt": "Qual órgão fixa ordinariamente a contribuição confederativa?",
        "options": [
            "A assembleia geral da entidade sindical, nos termos do art. 8º, IV, da Constituição.",
            "A autoridade administrativa fiscal, mediante lançamento.",
            "O empregador, por decisão unilateral sobre a folha de pagamento.",
            "O juízo trabalhista, como providência obrigatória em todo dissídio coletivo.",
        ],
        "explanation": "O art. 8º, IV, atribui a fixação à assembleia geral. Isso não se confunde com lançamento tributário ou imposição unilateral do empregador.",
    },
    "Q038": {
        "prompt": "Uma central sindical integra automaticamente o sistema confederativo para fins de custeio da contribuição?",
        "options": [
            "Não. Centrais sindicais não são os graus de organização previstos na estrutura sindicato–federação–confederação.",
            "Sim. Toda central sindical ocupa o mesmo grau que uma confederação.",
            "Sim. A assembleia pode converter livremente uma central em entidade confederativa.",
            "Não. Apenas porque as centrais são órgãos integrantes da administração tributária.",
        ],
        "explanation": "O sistema confederativo do art. 8º, IV, não equivale a qualquer reunião de entidades de representação trabalhista; centrais sindicais não são confederações.",
    },
    "Q043": {
        "prompt": "Julgue as afirmações sobre a destinação da contribuição confederativa.",
        "statements": [
            {"text": "O sistema confederativo compreende sindicatos, federações e confederações.", "answer": True},
            {"text": "Centrais sindicais fazem parte, necessariamente, dos três graus do sistema confederativo.", "answer": False},
            {"text": "Conselhos de fiscalização profissional não são entidades do sistema confederativo sindical.", "answer": True},
            {"text": "A contribuição confederativa tem finalidade de custeio da representação sindical confederativa.", "answer": True},
        ],
        "explanation": "A finalidade constitucional é específica: financiar o sistema sindical confederativo, não toda forma de entidade profissional.",
    },
    "Q044": {
        "prompt": "Classifique quais entidades integram o sistema confederativo sindical.",
        "explanation": "Integram a estrutura os sindicatos, as federações e as confederações. Centrais sindicais, associações civis e conselhos profissionais não se confundem com seus graus de organização.",
    },
    "Q045": {
        "prompt": "Qual instância fixa, em regra, a contribuição confederativa?",
        "explanation": "O art. 8º, IV, da Constituição atribui a fixação à assembleia geral.",
    },
    "Q047": {
        "prompt": "Um instrumento coletivo pode substituir, por si só, a deliberação assemblear exigida para fixar a contribuição confederativa?",
        "options": [
            "Não. A fixação da confederativa segue o art. 8º, IV, e depende da deliberação assemblear pertinente.",
            "Sim. Qualquer convenção coletiva substitui a assembleia independentemente da modalidade da contribuição.",
            "Sim. Basta que o acordo coletivo fixe um valor para todos os trabalhadores não filiados.",
            "Não, porque a contribuição confederativa só pode nascer de lançamento fiscal.",
        ],
        "explanation": "A fonte constitucional da fixação da contribuição confederativa é a deliberação assemblear; não se deve confundi-la com as condições de instituição da assistencial em instrumento coletivo.",
    },
    "Q049": {
        "prompt": "Uma assembleia fixa contribuição confederativa manifestamente abusiva. Qual é a consequência possível?",
        "options": [
            "A deliberação pode ser questionada judicialmente, pois a autonomia sindical não afasta o controle de abusividade.",
            "O valor será sempre válido porque decisões assembleares são insuscetíveis de controle judicial.",
            "O valor transforma-se automaticamente em tributo e deve ser lançado pelo Fisco.",
            "O valor só pode ser questionado por quem não pertence ao sindicato.",
        ],
        "explanation": "Autonomia sindical não significa imunidade ao controle judicial de abuso, especialmente quando a cobrança desconsidera seus fins e os direitos envolvidos.",
    },
    "Q050": {
        "prompt": "Qual critério deve orientar a fixação do valor da contribuição confederativa?",
        "options": [
            "Proporcionalidade e razoabilidade em relação ao custeio do sistema confederativo.",
            "Livre fixação sem qualquer relação com a finalidade de custeio.",
            "Aplicação automática da alíquota histórica da contribuição sindical legal.",
            "Cobrança uniforme de não filiados para compensar a ausência de mensalidade.",
        ],
        "explanation": "O valor deve guardar relação justificável com a finalidade constitucional de custeio, sujeitando-se ao controle de abusividade; não há alíquota tributária nacional da confederativa.",
    },
    "Q052": {
        "prompt": "Uma assembleia com baixa participação aprova valor elevado de contribuição confederativa para os associados. Qual questão jurídica merece atenção?",
        "options": [
            "A legitimidade e a regularidade da deliberação associativa, além da razoabilidade do valor.",
            "A transformação automática da contribuição em imposto federal.",
            "O direito de exigir a contribuição de não filiados pelo simples resultado da votação.",
            "A competência exclusiva da central sindical para homologar a cobrança.",
        ],
        "explanation": "A participação e a regularidade assemblear merecem exame, assim como o eventual abuso no valor. Isso não autoriza, por si, a cobrança de pessoas não filiadas.",
    },
    "Q054": {
        "prompt": "A contribuição confederativa aprovada hoje pode ser exigida por períodos anteriores à própria fixação?",
        "options": [
            "Como regra, não. A deliberação não deve criar retroativamente obrigações associativas relativas a períodos anteriores.",
            "Sim. A assembleia pode retroagir livremente porque não há anterioridade tributária.",
            "Sim. A retroação independe do estatuto e da ciência dos associados.",
            "Não. A contribuição só pode começar a ser cobrada após a anterioridade tributária de noventa dias.",
        ],
        "explanation": "A não incidência da anterioridade tributária não equivale a liberdade irrestrita para criar cobranças retroativas. Devem ser observados a validade da deliberação e os direitos associativos.",
    },
    "Q056": {
        "prompt": "A contribuição confederativa é fixada pela {{blank}} geral da entidade sindical, nos termos da Constituição.",
        "explanation": "O art. 8º, IV, da Constituição prevê a fixação pela assembleia geral.",
    },
    "Q057": {
        "prompt": "A fixação do valor deve observar a {{blank}} e guardar relação com a finalidade de custeio do sistema confederativo.",
        "answers": ["razoabilidade"],
        "explanation": "O valor não deve ser arbitrário nem desproporcional ao fim de custeio confederativo.",
    },
    "Q059": {
        "prompt": "Julgue as regras sobre fixação e controle do valor da contribuição confederativa.",
        "statements": [
            {"text": "A assembleia pode deliberar pela não fixação da contribuição em determinado período.", "answer": True},
            {"text": "Federação e confederação podem instituir automaticamente o valor devido pelos filiados do sindicato, sem deliberação adequada.", "answer": False},
            {"text": "A convenção coletiva, por si só, substitui a assembleia para instituir a contribuição confederativa.", "answer": False},
            {"text": "Valores manifestamente abusivos podem ser submetidos a controle judicial.", "answer": True},
            {"text": "A natureza não tributária torna aplicável a anterioridade tributária de 90 dias.", "answer": False},
        ],
        "explanation": "A contribuição é fixada por deliberação sindical, sujeita aos limites jurídicos do custeio e ao controle de abusividade. Não se aplica automaticamente a anterioridade tributária.",
    },
    "Q060": {
        "prompt": "Classifique situações de fixação da contribuição confederativa.",
        "explanation": "A fixação deve decorrer da assembleia pertinente, manter relação com o custeio confederativo e respeitar os limites jurídicos da cobrança.",
    },
    "Q113": {
        "prompt": "O fato de uma contribuição ser paga periodicamente a transforma em mensalidade associativa?",
        "options": [
            "Não. A classificação depende do fundamento, da finalidade e do regime jurídico, não apenas da periodicidade.",
            "Sim. Toda cobrança periódica é mensalidade, ainda que financie a estrutura confederativa.",
            "Sim. A contribuição confederativa deixa de existir se houver recolhimentos recorrentes.",
            "Não. A contribuição confederativa e a mensalidade associativa têm idêntico fundamento jurídico.",
        ],
        "explanation": "A mensalidade decorre do vínculo associativo estatutário; a confederativa destina-se ao custeio do sistema confederativo e é fixada na forma do art. 8º, IV. A periodicidade isolada não resolve a classificação.",
    },
    "Q061": {
        "prompt": "Em quais tipos de categoria podem existir entidades sindicais organizadas para fins de representação confederativa?",
        "options": [
            "Categorias profissionais e econômicas, incluindo organizações específicas de trabalhadores autônomos conforme a estrutura sindical aplicável.",
            "Apenas categorias profissionais formadas por empregados com vínculo celetista.",
            "Exclusivamente categorias patronais organizadas em conselhos profissionais.",
            "Qualquer agrupamento informal de pessoas, independentemente de organização sindical.",
        ],
        "explanation": "A estrutura sindical abrange categorias profissionais e econômicas e pode alcançar organizações de trabalhadores autônomos. A existência de categoria não torna automaticamente todos os seus integrantes devedores da contribuição confederativa.",
    },
    "Q064": {
        "prompt": "De quem pode ser exigida a contribuição confederativa?",
        "options": [
            "Dos filiados ao sindicato respectivo, conforme a Súmula Vinculante 40 do STF.",
            "De toda a categoria, desde que a contribuição tenha sido aprovada por maioria simples em assembleia.",
            "De todos os beneficiados por negociação coletiva, desde que não apresentem oposição.",
            "Dos não filiados, desde que a entidade os notifique sobre a cobrança.",
        ],
        "explanation": "A Súmula Vinculante 40 do STF determina que a contribuição confederativa do art. 8º, IV, somente é exigível dos filiados ao sindicato respectivo. O regime de oposição dos não filiados é tema distinto, pertinente à contribuição assistencial.",
    },
    "Q065": {
        "prompt": "Qual garantia constitucional fundamenta a inexigibilidade da contribuição confederativa em relação ao não filiado?",
        "options": [
            "A liberdade de associação e sindicalização, que impede impor a um não filiado obrigação decorrente de deliberação interna da entidade.",
            "A imunidade tributária pessoal do trabalhador integrante da categoria.",
            "A proibição constitucional de todo custeio de entidades sindicais.",
            "A vedação de qualquer deliberação assemblear sobre questões patrimoniais.",
        ],
        "explanation": "Os arts. 5º, XX, e 8º, V, da Constituição protegem a liberdade associativa. A SV 40 traduz essa proteção para a contribuição confederativa.",
    },
    "Q066": {
        "prompt": "Uma assembleia fixa contribuição confederativa para toda a categoria, inclusive para quem nunca se filiou. Qual é o problema?",
        "options": [
            "A deliberação associativa não afasta a inexigibilidade da contribuição confederativa em relação aos não filiados (SV 40).",
            "A cobrança é válida porque a assembleia representa automaticamente todos os membros da categoria como associados.",
            "A cobrança só seria inválida se o não filiado apresentasse oposição dentro do prazo estabelecido pela assembleia.",
            "A cobrança se torna válida quando o sindicato a denomina contribuição assistencial sem alterar sua finalidade.",
        ],
        "explanation": "O fundamento não é apenas a ausência de participação na votação: a SV 40 limita a exigibilidade aos filiados. O direito de oposição do Tema 935 trata de modalidade diferente.",
    },
    "Q067": {
        "prompt": "Um associado votou contra a contribuição confederativa regularmente aprovada em assembleia. A discordância individual o dispensa automaticamente do pagamento?",
        "options": [
            "Não. A deliberação associativa válida pode vinculá-lo, sem prejuízo de questionamento de eventual irregularidade ou abusividade.",
            "Sim. Qualquer voto vencido equivale a oposição que extingue a obrigação.",
            "Sim. O Tema 935 reconhece oposição automática dos filiados à contribuição confederativa.",
            "Não. A contribuição é tributo estatal e independe das decisões da assembleia.",
        ],
        "explanation": "A relação associativa é distinta da obrigação imposta a não filiados. A discordância individual não basta, por si, para afastar deliberação válida, mas atos abusivos ou inválidos continuam sujeitos a controle.",
    },
    "Q072": {
        "prompt": "Nos termos da Súmula Vinculante 40 do STF, a contribuição confederativa só é exigível dos {{blank}} ao sindicato respectivo.",
        "answers": ["filiados"],
        "explanation": "O STF fixa expressamente a filiação como limite da exigibilidade da contribuição confederativa.",
    },
    "Q074": {
        "prompt": "Julgue as afirmações sobre filiação e exigibilidade da contribuição confederativa.",
        "statements": [
            {"text": "Uma deliberação assemblear válida pode vincular os integrantes associados à entidade.", "answer": True},
            {"text": "A Súmula Vinculante 40 limita a exigibilidade da contribuição confederativa aos filiados.", "answer": True},
            {"text": "O não filiado só se livra da contribuição confederativa se exercer direito de oposição.", "answer": False},
            {"text": "O direito de oposição do Tema 935 refere-se à contribuição assistencial, não à confederativa.", "answer": True},
        ],
        "explanation": "Não confunda filiação (SV 40, confederativa) com direito de oposição (Tema 935, assistencial).",
    },
    "Q097": {
        "prompt": "Uma assembleia sindical aprova cobrança confederativa para trabalhadores que não são filiados. Qual deve ser a conclusão?",
        "options": [
            "A cobrança confederativa é inexigível dos não filiados, ainda que a assembleia tenha aprovado seu valor.",
            "A cobrança é automaticamente válida se os não filiados tiverem se beneficiado de negociação coletiva.",
            "A cobrança passa a ser válida quando o trabalhador deixa transcorrer prazo de oposição.",
            "A cobrança é tributo porque a assembleia exerceu competência fiscal delegada.",
        ],
        "explanation": "A SV 40 restringe a confederativa aos filiados. A cobrança assistencial prevista em instrumento coletivo tem disciplina diferente, inclusive direito de oposição.",
    },
    "Q076": {
        "prompt": "Quanto ao desconto em folha de contribuição devida ao sindicato, o que estabelece o art. 545 da CLT?",
        "options": [
            "O empregador deve efetuar o desconto quando notificado pelo sindicato e houver autorização do empregado.",
            "A filiação dispensa, em qualquer hipótese, a autorização prevista no art. 545 da CLT.",
            "O sindicato pode impor desconto salarial de contribuição confederativa a não filiados.",
            "A assembleia pode substituir toda manifestação necessária para desconto na folha.",
        ],
        "explanation": "O art. 545 da CLT prevê autorização do empregado para o desconto em folha das contribuições devidas ao sindicato, após notificação. A análise da exigibilidade associativa é distinta da forma operacional de desconto.",
    },
    "Q077": {
        "prompt": "Sem a autorização do empregado exigida para o desconto em folha, qual é a conduta adequada do empregador?",
        "options": [
            "Não efetuar o desconto da contribuição em folha, distinguindo essa operação de eventual obrigação associativa válida.",
            "Descontar automaticamente qualquer valor aprovado em assembleia, sem verificar a situação do empregado.",
            "Converter a contribuição confederativa em contribuição sindical compulsória.",
            "Exigir do não filiado que apresente oposição ao desconto em dez dias.",
        ],
        "explanation": "Nos termos do art. 545 da CLT, o empregador depende de autorização do empregado para efetuar o desconto. A ausência de desconto não resolve, por si, a existência de eventual obrigação entre sindicato e associado.",
    },
    "Q078": {
        "prompt": "A previsão de desconto em folha no art. 8º, IV, permite impor contribuição confederativa ao não filiado?",
        "options": [
            "Não. A previsão constitucional deve ser lida com a liberdade sindical e a Súmula Vinculante 40.",
            "Sim. A Constituição dispensa a filiação para cobrança de toda contribuição sindical.",
            "Sim. Basta o empregador reconhecer o sindicato como representante da categoria.",
            "Não. Porque contribuições confederativas só podem ser pagas diretamente à União.",
        ],
        "explanation": "O art. 8º, IV, trata da fixação e do desconto para custeio confederativo, mas não elimina o limite de exigibilidade aos filiados estabelecido pela SV 40.",
    },
    "Q082": {
        "prompt": "Nos termos do art. 545 da CLT, o desconto em folha de contribuições devidas ao sindicato depende de autorização do {{blank}}.",
        "answers": ["empregado"],
        "explanation": "A autorização prevista no art. 545 refere-se à operação de desconto na folha de pagamento do empregado.",
    },
    "Q084": {
        "prompt": "Associe cada situação à consequência para o desconto em folha da contribuição confederativa.",
        "cards": [
            {"id": "c1", "text": "Empregado filiado, com autorização para o desconto.", "zone": "desconta"},
            {"id": "c2", "text": "Trabalhador não filiado, com valor aprovado apenas em assembleia.", "zone": "nao"},
            {"id": "c3", "text": "Empregado filiado que não autorizou o desconto em folha.", "zone": "nao"},
            {"id": "c4", "text": "Trabalhador não filiado ao sindicato respectivo.", "zone": "nao"},
        ],
        "explanation": "A SV 40 afasta a exigibilidade confederativa em relação aos não filiados. O art. 545 da CLT disciplina a autorização para o desconto em folha.",
    },
    "Q098": {
        "prompt": "Um associado é alcançado por contribuição confederativa validamente aprovada, mas não autorizou seu desconto em folha. O que deve ser distinguido?",
        "options": [
            "A eventual obrigação associativa e a autorização do empregado para que o empregador desconte em folha.",
            "A filiação associativa e o pagamento de tributos municipais.",
            "O desconto salarial e uma execução fiscal compulsória promovida pelo sindicato.",
            "A contribuição confederativa e o direito de oposição do não filiado previsto no Tema 935.",
        ],
        "explanation": "A relação jurídica associativa e o procedimento de desconto em folha não são idênticos. O art. 545 da CLT estabelece requisito para o desconto salarial.",
    },
    "Q085": {
        "prompt": "Na posição doutrinária de aplicação do prazo geral do art. 205 do Código Civil à cobrança da contribuição confederativa, qual prazo é indicado?",
        "options": [
            "Dez anos, quando não houver prazo específico aplicável à pretensão concreta.",
            "Cinco anos, automaticamente por aplicação do art. 174 do Código Tributário Nacional.",
            "Dois anos, obrigatoriamente contados da desfiliação do associado.",
            "Prazo imprescritível porque a contribuição tem previsão constitucional.",
        ],
        "explanation": "A exposição doutrinária utiliza o prazo geral de dez anos do art. 205 do Código Civil, na falta de prazo específico. Isso não autoriza afirmar que toda cobrança confederativa prescreve invariavelmente em dez anos: o prazo depende da qualificação e da pretensão concreta.",
    },
    "Q088": {
        "prompt": "A natureza não tributária confere ao sindicato privilégios fazendários na cobrança judicial da contribuição confederativa?",
        "options": [
            "Não. A mera cobrança confederativa não tem os privilégios de constituição e execução de crédito tributário.",
            "Sim. Toda obrigação prevista na Constituição constitui crédito tributário.",
            "Sim. A assembleia substitui o lançamento tributário e produz certidão de dívida ativa.",
            "Não. Isso impediria o sindicato de buscar cobrança pela via judicial adequada.",
        ],
        "explanation": "A natureza não tributária afasta a ideia de inscrição em dívida ativa tributária e de execução fiscal como consequência automática; isso não significa impossibilidade de cobrança civil/trabalhista cabível.",
    },
    "Q091": {
        "prompt": "Segundo o art. 114, III, da Constituição, qual é a regra geral de competência para ações entre sindicato e trabalhador ou empregador relacionadas à representação sindical?",
        "options": [
            "Competência da Justiça do Trabalho, sem prejuízo de regimes especiais, como controvérsias envolvendo servidores estatutários.",
            "Competência exclusiva da Justiça Federal porque todas as entidades sindicais são autarquias.",
            "Competência automática da Justiça Comum em qualquer controvérsia sindical posterior à Reforma de 2017.",
            "Competência exclusiva do STF por envolver contribuição prevista na Constituição.",
        ],
        "explanation": "O art. 114, III, da Constituição, após a EC 45/2004, inclui ações sobre representação sindical entre sindicatos e trabalhadores ou empregadores na Justiça do Trabalho. O enquadramento de situações específicas exige atenção, como no regime jurídico-estatutário.",
    },
    "Q093": {
        "prompt": "A contribuição confederativa não paga não se inscreve automaticamente em dívida ativa tributária, pois o crédito tem natureza {{blank}}.",
        "answers": ["privada"],
        "explanation": "Natureza privada e não tributária afastam o regime automático de constituição e execução do crédito tributário.",
    },
    "Q095": {
        "prompt": "Classifique as consequências da natureza não tributária da contribuição confederativa.",
        "cards": [
            {"id": "c1", "text": "Cobrança pela via judicial adequada, conforme a pretensão.", "zone": "sim"},
            {"id": "c2", "text": "Inscrição automática em dívida ativa tributária.", "zone": "nao"},
            {"id": "c3", "text": "Controle judicial de eventual abusividade.", "zone": "sim"},
            {"id": "c4", "text": "Privilégios da Fazenda Pública por mera inadimplência.", "zone": "nao"},
            {"id": "c5", "text": "Execução fiscal tributária como consequência automática.", "zone": "nao"},
        ],
        "explanation": "O crédito não tributário pode ser exigido pela via processual cabível, mas a inadimplência não lhe confere os privilégios típicos do crédito fiscal.",
    },
    "Q096": {
        "prompt": "Um sindicato arrecada contribuição confederativa e não demonstra qualquer destinação ao custeio da estrutura confederativa. Qual questão deve ser examinada?",
        "options": [
            "A compatibilidade entre a arrecadação, a finalidade confederativa e a transparência da destinação dos recursos.",
            "A conversão automática de toda arrecadação em imposto federal por ausência de repasse.",
            "A possibilidade de cobrar não filiados para compensar o valor não destinado às federações.",
            "A dispensa de qualquer controle, pois o uso da arrecadação depende exclusivamente de decisão unilateral do dirigente.",
        ],
        "explanation": "A finalidade do art. 8º, IV, é o custeio do sistema confederativo. A análise concreta de destinação deve considerar a deliberação válida e a organização de repasses, sem presumir regras quantitativas de distribuição não demonstradas.",
    },
    "Q099": {
        "prompt": "Uma contribuição prevista em instrumento coletivo destina-se especificamente ao custeio da negociação coletiva. Qual modalidade está em foco?",
        "explanation": "A finalidade negocial remete à contribuição assistencial. O Tema 935 admite sua instituição em acordo ou convenção coletiva, inclusive para não filiados com direito de oposição.",
    },
    "Q102": {
        "prompt": "Qual alternativa resume corretamente a contribuição confederativa?",
        "options": [
            "Finalidade confederativa, fixação assemblear, natureza não tributária e exigibilidade limitada aos filiados.",
            "Finalidade previdenciária, lançamento fiscal e cobrança compulsória de toda a categoria.",
            "Finalidade estritamente negocial, instituição por convenção coletiva e direito de oposição do não filiado.",
            "Finalidade exclusivamente assistencial, arrecadação estatal e execução fiscal obrigatória.",
        ],
        "explanation": "A síntese juridicamente correta reúne art. 8º, IV, autonomia associativa, natureza não tributária e SV 40. A contribuição assistencial tem regime distinto (Tema 935).",
    },
    "Q104": {
        "prompt": "Faça a revisão jurídica final das contribuições sindicais.",
        "statements": [
            {"text": "A contribuição confederativa financia o sistema sindical confederativo.", "answer": True},
            {"text": "A contribuição confederativa é tributária porque a Constituição a menciona.", "answer": False},
            {"text": "A assembleia geral é a instância prevista no art. 8º, IV, para sua fixação.", "answer": True},
            {"text": "O direito de oposição do Tema 935 permite, por si, cobrar contribuição confederativa de não filiados.", "answer": False},
            {"text": "A Lei 13.467/2017 alterou a exigibilidade da contribuição sindical legal, não a natureza privada da confederativa.", "answer": True},
            {"text": "A contribuição assistencial e a confederativa possuem a mesma finalidade.", "answer": False},
        ],
        "explanation": "A revisão diferencia a natureza e o alcance da confederativa, o regime sindical pós-2017 e a assistencial segundo o Tema 935.",
    },
    "Q105": {
        "prompt": "Relacione os aspectos centrais da contribuição confederativa.",
        "cards": [
            {"id": "c1", "text": "Custeio do sistema formado por sindicato, federação e confederação.", "zone": "final"},
            {"id": "c2", "text": "Deliberação da assembleia geral, conforme a Constituição.", "zone": "fix"},
            {"id": "c3", "text": "Natureza privada, sem qualificação tributária.", "zone": "nat"},
            {"id": "c4", "text": "Exigibilidade limitada aos filiados (Súmula Vinculante 40).", "zone": "suj"},
            {"id": "c5", "text": "Cobrança pela via cabível, sem privilégios tributários automáticos.", "zone": "cob"},
        ],
        "explanation": "Síntese dos fundamentos constitucionais e das consequências jurídicas da contribuição confederativa.",
    },
}

# Há 60 itens preservados. Cada questão mantida passa por normalização
# dos marcadores do próprio material, com os casos críticos reescritos acima.
SUBSTITUTIONS = [
    ("segundo o material", "no regime jurídico estudado"),
    ("Segundo o material", "No regime jurídico estudado"),
    ("o material", "a disciplina jurídica"),
    ("O material", "A disciplina jurídica"),
    ("o texto", "a fundamentação"),
    ("O texto", "A fundamentação"),
    ("do material", "da disciplina examinada"),
    ("no material", "na disciplina examinada"),
    ("No material", "Na disciplina examinada"),
    ("do capítulo", "do tema"),
]

def revised_data(original):
    if original.get("meta", {}).get("version") == VERSION:
        return original, [], [], True
    if len(original.get("questions", [])) != 117:
        raise ValueError(
            "O banco de origem não tem 117 questões. Pare: houve uma mudança "
            "desde a auditoria e a revisão deve ser reconciliada."
        )
    questions = original["questions"]
    by_id = {q["id"]: q for q in questions}
    if len(by_id) != 117 or not set(KEEP).issubset(by_id):
        raise ValueError("IDs ausentes ou duplicados. Revisão interrompida.")
    wrong_types = [id for id in KEEP if by_id[id]["type"] not in ("mcq", "fill", "tf", "drag")]
    if wrong_types:
        raise ValueError(f"Tipos inesperados: {wrong_types}")

    revised = copy.deepcopy(original)
    kept = []
    changed = []
    for question_id in KEEP:
        q = copy.deepcopy(by_id[question_id])
        if question_id in PATCH:
            for key, value in PATCH[question_id].items():
                q[key] = copy.deepcopy(value)
            changed.append(question_id)
        for field in ("prompt", "explanation"):
            val = q.get(field, "")
            for before, after in SUBSTITUTIONS:
                val = val.replace(before, after)
            q[field] = val
        kept.append(q)

    # Com 37 múltiplas escolhas antes todas na alternativa A, redistribuímos
    # sem alterar qual alternativa é semanticamente correta.
    mcqs = [q for q in kept if q["type"] == "mcq"]
    positions = [i % 4 for i in range(len(mcqs))]
    random.Random(20261008).shuffle(positions)
    for q, target in zip(mcqs, positions):
        options = q["options"]
        if len(options) != 4:
            raise ValueError(f"{q['id']}: esperado quatro alternativas")
        correct = options[q["answer"]]
        others = [o for i, o in enumerate(options) if i != q["answer"]]
        random.Random(int(hashlib.sha256(q["id"].encode()).hexdigest()[:8], 16)).shuffle(others)
        others.insert(target, correct)
        q["options"] = others
        q["answer"] = target

    counts = collections.Counter(q["type"] for q in kept)
    assert counts == {"mcq": 37, "fill": 9, "tf": 7, "drag": 7}, counts

    for q in kept:
        if not q["prompt"].strip() or not q.get("explanation", "").strip():
            raise ValueError(f"{q['id']}: enunciado/explicação vazios")
        if q["type"] == "mcq":
            if len(q["options"]) != 4 or len(set(q["options"])) != 4:
                raise ValueError(f"{q['id']}: alternativas duplicadas/ausentes")
            if not 0 <= q["answer"] < 4:
                raise ValueError(f"{q['id']}: índice incorreto")
        elif q["type"] == "fill":
            if q["prompt"].count("{{blank}}") != len(q["answers"]):
                raise ValueError(f"{q['id']}: número de lacunas incorreto")
            if any(not isinstance(a, str) or not a for a in q["answers"]):
                raise ValueError(f"{q['id']}: resposta de lacuna inválida")
        elif q["type"] == "tf":
            if not q["statements"] or any(type(s["answer"]) is not bool for s in q["statements"]):
                raise ValueError(f"{q['id']}: verdadeiro/falso inválido")
        elif q["type"] == "drag":
            zones = {z["id"] for z in q["zones"]}
            if any(c["zone"] not in zones for c in q["cards"]):
                raise ValueError(f"{q['id']}: cartão sem zona válida")
    if len({q["id"] for q in kept}) != 60:
        raise ValueError("ID duplicado no banco revisado.")

    revised["questions"] = kept
    revised["meta"].update({
        "title": "Contribuição confederativa",
        "discipline": "Direito do Trabalho",
        "language": "pt-BR",
        "version": VERSION,
        "sourceNote": (
            "Banco originalmente elaborado com base no material de estudo; "
            "revisto juridicamente à luz do art. 8º, IV, da CF, da Súmula "
            "Vinculante 40, dos arts. 545 e 578 da CLT e do Tema 935 do STF. "
            "Enunciados históricos são contextualizados."
        ),
        "totalActivities": len(kept),
        "typeCounts": dict(counts),
        "design": "Legis Lectiones — Direito do Trabalho",
        "reviewStrategy": (
            "60 atividades sem duplicações literais; casos práticos, classificação "
            "jurídica e distinção temporal entre confederativa, sindical e assistencial. "
            "Alternativas de múltipla escolha em posições balanceadas."
        ),
    })
    revised["meta"].pop("attemptRule", None)
    deleted = [q["id"] for q in questions if q["id"] not in set(KEEP)]
    return revised, deleted, changed, False


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="simula e valida; não altera arquivos")
    args = parser.parse_args()

    if not DATA_PATH.is_file() or not HTML_PATH.is_file():
        raise SystemExit("Execute na raiz do repositório: faltam arquivos em labour-law/.")
    original_text = DATA_PATH.read_text(encoding="utf-8")
    original = json.loads(original_text)
    result, deleted, changed, already = revised_data(original)
    if already:
        print("Banco já revisado; nenhuma alteração necessária.")
        return
    html = HTML_PATH.read_text(encoding="utf-8")
    old_storage = "'law-mock-tests:labour:confederative-contribution:v1'"
    new_storage = "'legis-lectiones:labour:confederative-contribution:v3'"
    if old_storage in html:
        new_html = html.replace(old_storage, new_storage, 1)
    elif new_storage in html:
        new_html = html
    else:
        raise SystemExit(
            "Não encontrei a chave localStorage conhecida no HTML. "
            "Nenhuma alteração feita: adapte a migração antes de prosseguir."
        )

    # Garantia de compatibilidade com os contadores da interface.
    typ = result["meta"]["typeCounts"]
    assert len(result["questions"]) == result["meta"]["totalActivities"] == sum(typ.values()) == 60
    assert len(deleted) == 57 and len(changed) >= 45
    if args.check:
        print("SIMULAÇÃO — nada foi gravado.")
    else:
        BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not BACKUP_PATH.exists():
            shutil.copy2(DATA_PATH, BACKUP_PATH)
        DATA_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if html != new_html:
            HTML_PATH.write_text(new_html, encoding="utf-8")
        print(f"Backup local: {BACKUP_PATH} (não faça git add nele)")
    print(f"Atividades: {len(original['questions'])} -> {len(result['questions'])}")
    print(f"Distribuição: {dict(typ)}")
    print(f"Questões reescritas: {len(changed)}")
    print("Excluídas:", ", ".join(deleted))
    print("Gabarito das múltiplas escolhas redistribuído:", dict(collections.Counter(
        q["answer"] for q in result["questions"] if q["type"] == "mcq"
    )))
    print("Nova chave localStorage: v3, pois as tentativas com 117 itens não são compatíveis com 60.")


if __name__ == "__main__":
    run()
