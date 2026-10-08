LEGIS LECTIONES — FOUR P2 BANKS + METADATA

Executable file: run_p2.py
Run at the ROOT of the GitHub Codespaces repository:

    python legis_p2_patch/run_p2.py
    node --check labour-law/p2-quiz.js
    node --check labour-law/engagement.js
    node --check labour-law/support-popup.js
    node --check functions/api/engagement.js
    git diff --check
    git status --short
    git diff --stat

ATTENTION: the Google Apps Script integration uses a fixed sheet map ABAS.
BEFORE publishing the banks, add 4 lines inside the const ABAS object:
    "contribuicao-assistencial": "Contrib_Assistencial",
    "liberdade-sindical": "Liberdade_Sindical",
    "organizacao-sindical": "Organizacao_Sindical",
    "suspensao-interrupcao-contrato": "Suspensao_Interrupcao"
The four sheets have already been created in the spreadsheet connected by ChatGPT.

After reviewing the changes:
    git add labour-law/ functions/api/engagement.js
    git commit -m "Add P2 labour banks and fix collective agreement metadata"
    git push origin main

The script checks anchors before writing and does not create duplicate files on repeated runs. It does not modify the five consolidated JSONs except for the metadata of the first bank. It does not alter D1 nor secrets.

New files: 4 HTML + 4 JSON + p2-quiz.js + p2-quiz.css
Modified files: labour-law/index.html, metadata in convencao-acordo-coletivo.json, engagement.js, support-popup.js, mais-curtidas.html and functions/api/engagement.js.
