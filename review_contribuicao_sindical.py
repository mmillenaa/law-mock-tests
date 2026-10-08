#!/usr/bin/env python3
"""Revisao editorial segura de contribuicao-sindical.json (Legis Lectiones).

- Troca perguntas sobre o 'material' por perguntas sobre conceitos de direito.
- Substitui integralmente CS032 por situacao de aplicacao dos arts. 578 e 579 da CLT.
- Preserva ids, tipos, numero de questoes, gabaritos de todas as demais questoes.
- Nao altera outros bancos, sistemas de engajamento nem scripts HTML.
- Idempotente. Use --check para simular sem gravar.
"""
import argparse
import json
from pathlib import Path

FILE = Path('labour-law/contribuicao-sindical.json')

PROMPTS = {
 'CS002': 'Por que a denominação histórica “imposto sindical” era tecnicamente questionada na classificação dessa arrecadação?',
 'CS005': 'A assembleia geral de um sindicato fixa uma cobrança destinada exclusivamente ao custeio do sistema confederativo. Que contribuição é essa?',
 'CS006': 'Após uma negociação coletiva, o sindicato institui em instrumento coletivo uma cobrança para cobrir despesas da negociação. Qual é essa modalidade de contribuição?',
 'CS008': 'Qual alternativa distingue corretamente as fontes de instituição das contribuições sindical e confederativa?',
 'CS009': 'Antes da Reforma Trabalhista de 2017, quais características fundamentavam a classificação da contribuição sindical como tributo?',
 'CS010': 'No regime anterior a 2017, uma pessoa dizia: “não autorizei, então não existe vínculo jurídico de cobrança”. À luz da disciplina então vigente, essa afirmação era:',
 'CS011': 'No regime anterior à Reforma, por que a contribuição sindical, apesar de sua natureza tributária, era diferenciada de um imposto em sentido técnico?',
 'CS014': 'No regime anterior à Reforma de 2017, em qual espécie tributária se enquadrava a contribuição sindical?',
 'CS015': 'Antes da Reforma de 2017, quem estava sujeito à cobrança compulsória da contribuição sindical?',
 'CS016': 'Por que a cobrança sindical compulsória de não filiados gerou objeções fundamentadas na liberdade sindical?',
 'CS020': 'No modelo histórico de arrecadação sindical, qual ato exemplificava a atividade administrativa vinculada?',
 'CS021': 'Na sistemática histórica de cobrança judicial da contribuição sindical, qual procedimento era utilizado para constituir o título de dívida?',
 'CS023': 'Qual possível efeito institucional era associado à garantia de receitas provenientes da contribuição sindical compulsória?',
 'CS024': 'Por que alguns sindicatos de maior porte poderiam dispensar ou devolver valores recebidos a título de contribuição sindical?',
 'CS025': 'Qual mudança a Reforma Trabalhista de 2017 introduziu no recolhimento da contribuição sindical?',
 'CS026': 'Na interpretação doutrinária que relaciona a natureza tributária à compulsoriedade, que efeito a Reforma de 2017 teve sobre a classificação da contribuição sindical?',
 'CS027': 'Uma empresa desconta contribuição sindical do salário sem autorização expressa do empregado, alegando que ele integra a categoria. À luz da legislação posterior à Reforma de 2017, a justificativa é:',
 'CS028': 'A exigência de autorização prévia e expressa para o recolhimento da contribuição sindical alcança:',
 'CS029': 'A Lei 13.467/2017 estabeleceu vacatio legis de 120 dias. A partir de sua entrada em vigor, qual regra passou a orientar o recolhimento da contribuição sindical?',
 'CS039': 'No regime tributário anterior a 2017, alterações de alíquota, base de cálculo ou criação de novos contribuintes dependiam de {{blank}}, e não de simples deliberação sindical.',
 'CS040': 'Na sistemática histórica de cobrança judicial, o Ministério do Trabalho inscrevia a contribuição sindical como título de {{blank}}, mediante certidão.',
 'CS044': 'Entre os exemplos tradicionais de serviços custeados pela contribuição sindical estavam assistência jurídica, médica, social e {{blank}} de férias.',
 'CS052': 'Sobre a contribuição sindical após a Reforma Trabalhista de 2017:',
 'CS053': 'Sobre a entrada em vigor da Reforma Trabalhista de 2017:',
 'CS061': 'Relacione cada decisão à fonte normativa ou ao sujeito cuja autorização é necessária.',
}

EXPLANATIONS = {
 'CS001': 'A expressão atual designa a cobrança historicamente chamada de imposto sindical; a alteração do nome não criou automaticamente outro instituto.',
 'CS004': 'A finalidade geral abrange o custeio de atividades sindicais, inclusive assistência jurídica, médica e social, entre outras destinações legais.',
 'CS007': 'A mensalidade ou contribuição associativa decorre da condição de sócio do sindicato, isto é, da filiação.',
 'CS009': 'Na disciplina histórica, destacavam-se pecuniariedade, compulsoriedade, previsão legal, ausência de caráter sancionatório e cobrança administrativa vinculada.',
 'CS011': 'A vinculação da arrecadação ao custeio de interesses sindicais fundamentava a classificação histórica como contribuição, e não como imposto em sentido técnico.',
 'CS012': 'A taxa pressupõe serviço estatal específico e divisível; serviços oferecidos pelo sindicato não se confundem com prestação estatal.',
 'CS014': 'Na classificação anterior a 2017, tratava-se de contribuição de interesse das categorias profissionais ou econômicas, integrante do gênero tributo.',
 'CS015': 'No regime histórico compulsório, a filiação não era requisito para a cobrança: associados e não filiados podiam ser alcançados.',
 'CS016': 'Obrigar não filiados a financiar uma entidade sindical suscita tensão com a liberdade de filiar-se, não se filiar e desfiliar-se, objeto de crítica da OIT.',
 'CS018': 'No regime tributário anterior, mudanças de alíquota, base de cálculo e sujeitos passivos estavam submetidas ao princípio da legalidade.',
 'CS019': 'A contribuição sindical era instituída em lei, diferentemente da contribuição confederativa, cuja fixação cabe à assembleia geral.',
 'CS020': 'O lançamento pelo fiscal do trabalho exemplificava, na sistemática histórica, a atividade administrativa vinculada.',
 'CS021': 'O procedimento histórico envolvia inscrição como título de dívida e emissão de certidão com identificação do contribuinte, do débito e da entidade favorecida.',
 'CS022': 'A sistemática histórica previa privilégios de cobrança semelhantes aos da Fazenda Pública, sem atribuição de foro especial.',
 'CS023': 'A garantia de receita compulsória poderia reduzir o incentivo à busca de novos associados e ao fortalecimento do vínculo de representação.',
 'CS024': 'Entidades com outras receitas suficientes podiam dispensar essa fonte de custeio ou devolver valores recebidos.',
 'CS026': 'A interpretação doutrinária adotada associa a perda da natureza tributária ao fim da compulsoriedade na disciplina da Lei 13.467/2017.',
 'CS027': 'A Lei 13.467/2017 condicionou o desconto da contribuição sindical à autorização prévia e expressa; a mera integração à categoria não basta.',
 'CS028': 'A exigência de autorização expressa foi prevista para as categorias de contribuintes alcançadas pela disciplina legal, incluindo empregados, empregadores, autônomos e avulsos.',
 'CS030': 'Com a entrada em vigor da Reforma, não subsistia cobrança compulsória proporcional referente a 2018 na hipótese apresentada: o recolhimento dependia de autorização.',
 'CS031': 'As modalidades devem ser diferenciadas pela fonte de instituição, pela finalidade e pelo vínculo com a filiação sindical.',
 'CS037': 'A taxa pressupõe serviço estatal específico e divisível, o que não caracteriza as atividades custeadas pela contribuição sindical.',
 'CS040': 'A certidão individualizava o débito e integrava a sistemática histórica de cobrança judicial da contribuição sindical.',
 'CS041': 'O recolhimento da contribuição sindical passou a depender de autorização prévia e expressa após a Reforma Trabalhista de 2017.',
 'CS042': 'A Lei 13.467/2017 entrou em vigor após 120 dias da publicação, marco da alteração das regras de recolhimento.',
 'CS043': 'No regime histórico compulsório, a cobrança podia alcançar filiados e não filiados, independentemente de adesão ao sindicato.',
 'CS044': 'Entre as atividades tradicionalmente custeadas estavam assistência jurídica, médica e social, além de colônias de férias.',
 'CS045': 'A arrecadação destinada a interesses das categorias profissionais e econômicas fundamentou a mudança da denominação histórica “imposto sindical”.',
 'CS047': 'A compulsoriedade e a previsão legal caracterizavam a contribuição sindical histórica; a cobrança não configurava sanção por ato ilícito.',
 'CS050': 'A crítica à cobrança compulsória de não filiados coexistia com a interpretação constitucional que admitia a contribuição instituída em lei no modelo anterior à Reforma.',
 'CS052': 'A Reforma de 2017 substituiu a compulsoriedade pela necessidade de autorização prévia e expressa para o recolhimento.',
 'CS053': 'A mudança legislativa passou a produzir efeitos após o período de 120 dias; com a nova disciplina, o recolhimento ficou condicionado à autorização.',
 'CS056': 'Pecuniariedade, compulsoriedade, previsão legal e atividade administrativa vinculada integravam a caracterização tributária histórica; a cobrança não era penalidade.',
 'CS057': 'Destinação específica, inexistência de serviço estatal divisível e ausência de obra pública fundamentavam a distinção entre as espécies tributárias examinadas.',
 'CS059': 'A mudança central em 2017 foi a substituição da cobrança compulsória pelo recolhimento condicionado à autorização prévia e expressa.',
 'CS062': 'A autorização é requisito para o recolhimento da contribuição sindical no regime posterior a 2017, não bastando o pertencimento à categoria.',
}

# Ajustes de afirmativas que testavam a memoria do texto, e nao a disciplina juridica.
STATEMENTS = {
 'CS046': {1: 'A contribuição assistencial está ligada ao custeio das despesas de negociações coletivas.'},
 'CS051': {1: 'O sindicato não podia alterar por deliberação própria a base de cálculo e as alíquotas da contribuição sindical histórica.'},
 'CS045': {
     0: 'A expressão “contribuição sindical” sucedeu a denominação histórica “imposto sindical”, sem criar, por si só, instituto completamente distinto.',
     1: 'A arrecadação da contribuição sindical histórica era livremente destinada a quaisquer despesas do Estado.',
     2: 'A destinação vinculada a interesses sindicais ajuda a explicar a classificação histórica como contribuição.'
 },
 'CS047': {3: 'A contribuição sindical histórica tinha natureza de sanção por ato ilícito.'},
 'CS048': {3: 'Antes da Reforma de 2017, a contribuição sindical era classificada como contribuição de interesse das categorias profissionais ou econômicas.'},
 'CS049': {
     0: 'Na sistemática histórica, a cobrança judicial envolvia inscrição pelo Ministério do Trabalho como título de dívida.',
     3: 'A cobrança histórica previa privilégios semelhantes aos da Fazenda Pública, sem foro especial.'
 },
 'CS050': {
     0: 'A OIT formulou críticas à cobrança compulsória de contribuições sindicais de pessoas não filiadas.',
     2: 'Antes da Reforma, a liberdade de filiação sindical impedia, por si só, qualquer contribuição sindical instituída em lei.'
 },
 'CS052': {
     2: 'A contribuição sindical passou a ser facultativa.',
     3: 'A exigência de autorização prévia e expressa também alcança empregadores, autônomos e trabalhadores avulsos.'
 },
 'CS054': {
     0: 'O custeio sindical contemplava atividades como assistência jurídica, médica e odontológica, cooperativas, creches e colônias de férias.',
     2: 'Uma receita compulsória assegurada pode reduzir o incentivo à busca de novos associados.',
     3: 'Alguns sindicatos de maior porte podiam dispensar ou devolver valores da contribuição sindical por possuírem outras receitas.'
 },
 'CS053': {
     1: 'Após a entrada em vigor da Reforma, era admissível exigir compulsoriamente parcela proporcional referente a 2018.',
     2: 'Em 2018, o recolhimento da contribuição sindical dependia de autorização.'
 },
}

# Respostas continuam nos mesmos índices.
OPTIONS = {
    # Distratores mais próximos dos conceitos realmente estudados.
    'CS001': {
        1: 'A nova denominação eliminou, por si só, a cobrança de pessoas não filiadas ainda no regime pré-2017.',
        2: 'O novo nome passou a designar exclusivamente as mensalidades de quem era filiado ao sindicato.',
        3: 'A mudança do nome provocou automaticamente a perda de sua natureza tributária.'
    },
    'CS002': {
        0: 'Porque a cobrança já exigia autorização expressa mesmo na fase histórica compulsória.',
        2: 'Porque sua fonte sempre foi exclusivamente a deliberação assemblear, sem previsão legal.',
        3: 'Porque a receita não possuía destinação vinculada a interesses sindicais.'
    },
    'CS013': {
        1: 'A receita possuía destinação vinculada ao custeio sindical.',
        2: 'Não correspondia à remuneração de serviço estatal específico e divisível.',
        3: 'A cobrança histórica era prevista em lei e tinha caráter compulsório.'
    },
    'CS018': {2: 'Não. No regime tributário anterior, alterações de alíquota e base de cálculo dependiam de lei.'},
    'CS022': {
        0: 'O sindicato podia modificar alíquotas e bases de cálculo sem previsão legal.',
        2: 'A certidão dispensava a identificação da entidade beneficiária do crédito.',
        3: 'A concessão dos privilégios de cobrança dependia de aprovação assemblear anual.'
    },
    'CS024': {
        0: 'Porque essa arrecadação era legalmente reservada a sindicatos com déficit financeiro.',
        2: 'Porque toda a receita dessa contribuição era obrigatoriamente destinada ao Estado.',
        3: 'Porque a filiação dos trabalhadores impedia o recolhimento compulsório no regime histórico.'
    },
    'CS025': {
        0: 'A contribuição tornou-se exigível apenas de filiados, sem necessidade de autorização específica.',
        2: 'A contribuição sindical foi extinta e substituída exclusivamente pela contribuição confederativa.',
        3: 'A contribuição permaneceu compulsória sempre que aprovada em assembleia geral.'
    },
    'CS030': {2: 'Não. Após a entrada em vigor da Reforma, o recolhimento passou a depender de autorização, inclusive em 2018.'},
    'CS031': {
        1: 'Sindical: lei e custeio geral; confederativa: assembleia e sistema confederativo; assistencial: filiação; associativa: despesas de negociação.',
        2: 'Sindical: lei e custeio geral; confederativa: instrumento coletivo e sistema confederativo; assistencial: assembleia e negociação; associativa: filiação.',
        3: 'Sindical: assembleia e custeio geral; confederativa: lei e sistema confederativo; assistencial: instrumento coletivo e negociação; associativa: filiação.'
    },
}

CARD_TEXTS = {
    'CS059': {'CS059-c2': 'Natureza tributária no regime histórico anterior a 2017'},
}

# Apenas rótulos que falavam da leitura do material, sem modificar a classificacao correta.
ZONE_LABELS = {
 'CS062': {'nao': 'Incompatível com o regime pós-2017'},
}

REPLACEMENT_032 = {
    'section': '5. Reforma e autorização',
    'type': 'mcq',
    'prompt': ('Uma assembleia sindical aprova o desconto da contribuição sindical de todos os integrantes '
               'da categoria, mesmo daqueles que não autorizaram a cobrança. Após a Reforma de 2017, '
               'a deliberação da assembleia torna o desconto obrigatório?'),
    'options': [
        'Sim. A aprovação pela assembleia substitui a autorização individual para a contribuição sindical.',
        'Sim. Basta que a assembleia determine o valor e o prazo de recolhimento.',
        'Não. O desconto da contribuição sindical exige autorização prévia e expressa, que não é suprida pela deliberação assemblear.',
        'Não. A Reforma extinguiu a possibilidade de pagamento voluntário da contribuição sindical.',
    ],
    'answer': 2,
    'explanation': ('Os arts. 578 e 579 da CLT, na redação dada pela Lei 13.467/2017, condicionam '
                    'a contribuição sindical à autorização prévia e expressa. A deliberação da assembleia '
                    'não torna obrigatório esse desconto. Não confundir com a contribuição assistencial, '
                    'cuja disciplina jurídica é distinta.'),
    'focus': 'autorizacao-expressa',
    'reviewGroup': 'autorizacao',
    'id': 'CS032',
}


def build(path: Path):
    original = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(original.get('questions'), list) or len(original['questions']) != 62:
        raise ValueError('Esperadas exatamente 62 atividades. Nada foi alterado.')
    data = json.loads(json.dumps(original, ensure_ascii=False))
    questions = data['questions']
    by_id = {q['id']: q for q in questions}
    if len(by_id) != len(questions):
        raise ValueError('IDs duplicados encontrados.')
    original_answers = {q['id']: (q['type'], q.get('answer'), q.get('answers'),
                                 [(s['answer']) for s in q.get('statements', [])],
                                 [(c['id'], c['zone']) for c in q.get('cards', [])]) for q in questions}
    modified = set()
    for qid, prompt in PROMPTS.items():
        q = by_id[qid]
        if q['prompt'] != prompt:
            q['prompt'] = prompt
            modified.add(qid)
    for qid, explanation in EXPLANATIONS.items():
        q = by_id[qid]
        if q['explanation'] != explanation:
            q['explanation'] = explanation
            modified.add(qid)
    for qid, mapping in STATEMENTS.items():
        q = by_id[qid]
        for index, wording in mapping.items():
            if q['statements'][index]['text'] != wording:
                q['statements'][index]['text'] = wording
                modified.add(qid)
    for qid, mapping in OPTIONS.items():
        q = by_id[qid]
        for index, wording in mapping.items():
            if q['options'][index] != wording:
                q['options'][index] = wording
                modified.add(qid)
    for qid, mapping in CARD_TEXTS.items():
        q = by_id[qid]
        for card in q['cards']:
            if card['id'] in mapping and card['text'] != mapping[card['id']]:
                card['text'] = mapping[card['id']]
                modified.add(qid)
    for qid, mapping in ZONE_LABELS.items():
        q = by_id[qid]
        for zone in q['zones']:
            if zone['id'] in mapping and zone['label'] != mapping[zone['id']]:
                zone['label'] = mapping[zone['id']]
                modified.add(qid)

    if by_id['CS032'] != REPLACEMENT_032:
        # Conserva o lugar exato da CS032 na ordem original.
        ix = next(i for i, q in enumerate(questions) if q['id'] == 'CS032')
        questions[ix] = REPLACEMENT_032.copy()
        by_id['CS032'] = questions[ix]
        modified.add('CS032')

    data['meta']['sourceNote'] = ('Banco de revisão baseado nos temas trabalhados em Martins (2026 e 2024), '
                                 'com referência aos arts. 578 e 579 da CLT e à Reforma Trabalhista de 2017.')
    data['meta']['discipline'] = 'Direito do Trabalho'
    data['meta']['design'] = 'Legis Lectiones — dark navy glassmorphism, violet accent'
    data['meta']['version'] = '2.1'

    assert [q['id'] for q in data['questions']] == [q['id'] for q in original['questions']]
    assert len(data['questions']) == 62
    assert all(q['section'] != '6. Limites do material fornecido' for q in questions)
    assert all((q['type'], q.get('answer'), q.get('answers'),
                [(s['answer']) for s in q.get('statements', [])],
                [(c['id'], c['zone']) for c in q.get('cards', [])]) == original_answers[q['id']]
               for q in questions), 'Gabaritos ou tipos alterados inesperadamente.'
    assert all(q['prompt'].count('{{blank}}') == len(q['answers']) for q in questions if q['type'] == 'fill')
    assert sum(q['type'] == 'mcq' for q in questions) == 32
    assert sum(q['type'] == 'fill' for q in questions) == 12
    assert sum(q['type'] == 'tf' for q in questions) == 10
    assert sum(q['type'] == 'drag' for q in questions) == 8
    assert all(q['type'] != 'mcq' or q['answer'] < len(q['options']) for q in questions)
    return original, data, modified


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Valida o resultado, sem gravar no disco')
    args = parser.parse_args()
    if not FILE.is_file():
        parser.error(f'Arquivo não encontrado: {FILE}. Execute na raiz do repositório.')
    old, new, ids = build(FILE)
    if old == new:
        print('✓ O banco já está atualizado; nenhuma alteração necessária.')
        return
    print(f'✓ {len(new["questions"])} atividades preservadas (32 MCQ, 12 lacunas, 10 V/F, 8 cartões).')
    print('✓ Gabaritos, IDs, tipos e ordem preservados.')
    print('✓ CS032 substituída por questão jurídica aplicada.')
    print('✓ Itens com redação revisada:', ', '.join(sorted(ids)))
    if args.check:
        print('✓ Simulação concluída; nenhum arquivo modificado.')
        return
    FILE.write_text(json.dumps(new, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'✓ Alterações gravadas em {FILE}')


if __name__ == '__main__':
    main()
