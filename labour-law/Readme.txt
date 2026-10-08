LEGIS LECTIONES — QUATRO BANCOS DA P2 + METADADOS

Arquivo executável: run_p2.py
Execute na RAIZ do repositório do GitHub Codespaces:

    python legis_p2_patch/run_p2.py
    node --check labour-law/p2-quiz.js
    node --check labour-law/engagement.js
    node --check labour-law/support-popup.js
    node --check functions/api/engagement.js
    git diff --check
    git status --short
    git diff --stat

ATENÇÃO: a integração do Google Apps Script possui um mapa fixo ABAS.
ANTES de publicar os bancos, adicione 4 linhas dentro do objeto const ABAS:
    "contribuicao-assistencial": "Contrib_Assistencial",
    "liberdade-sindical": "Liberdade_Sindical",
    "organizacao-sindical": "Organizacao_Sindical",
    "suspensao-interrupcao-contrato": "Suspensao_Interrupcao"
As quatro abas já foram criadas na planilha conectada pelo ChatGPT.

Depois de rever as alterações:
    git add labour-law/ functions/api/engagement.js
    git commit -m "Add P2 labour banks and fix collective agreement metadata"
    git push origin main

O script verifica âncoras antes de escrever e não cria arquivos duplicados
em execuções repetidas. Não altera os cinco JSONs consolidados além do
metadado do primeiro banco. Não altera D1 nem segredos.

Arquivos novos: 4 HTML + 4 JSON + p2-quiz.js + p2-quiz.css
Arquivos modificados: labour-law/index.html, metadados de
convencao-acordo-coletivo.json, engagement.js, support-popup.js,
mais-curtidas.html e functions/api/engagement.js.
