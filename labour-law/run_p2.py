#!/usr/bin/env python3
"""Run P2 de forma conservadora no repositório Legis Lectiones.

Executar na raiz do repositório, com a pasta deste pacote ao lado.
Verifica todas as âncoras antes de escrever um arquivo sequer.
"""
from pathlib import Path
from collections import Counter
import json, re, sys

ROOT=Path.cwd()
PKG=Path(__file__).resolve().parent
SLUGS=[
 ('contribuicao-assistencial','Contribuição Assistencial','Custos negociais, natureza, direito de oposição e prescrição.',5),
 ('liberdade-sindical','Liberdade sindical','Liberdade individual e coletiva, convenções da OIT e garantias.',6),
 ('organizacao-sindical','Organização sindical','Unicidade, categorias, enquadramento, órgãos e funções.',7),
 ('suspensao-interrupcao-contrato','Suspensão e Interrupção do Contrato','Hipóteses e efeitos da suspensão e da interrupção contratual.',9),
]
OTHER=['convencao-acordo-coletivo','contribuicao-sindical','contribuicao-confederativa','mensalidade-sindical','aviso-previo']
FILEMAP={
 'labour-law/index.html': None,
 'labour-law/convencao-acordo-coletivo.json': None,
 'labour-law/engagement.js': None,
 'labour-law/support-popup.js': None,
 'labour-law/mais-curtidas.html': None,
 'functions/api/engagement.js': None,
}
for slug,_,_,_ in SLUGS:
 FILEMAP[f'labour-law/{slug}.html']='package'
 FILEMAP[f'labour-law/{slug}.json']='package'
FILEMAP['labour-law/p2-quiz.js']='package'
FILEMAP['labour-law/p2-quiz.css']='package'


def once(text,old,new,label):
 n=text.count(old)
 if n!=1:
  raise RuntimeError(f'{label}: âncora esperada uma vez, encontrada {n}. Nenhum arquivo alterado.')
 return text.replace(old,new,1)

def after(text,anchor,insertion,label):
 return once(text,anchor,anchor+insertion,label)

# Preflight de local e versões
if not (ROOT/'.git').exists():
 sys.exit('ERRO: execute na raiz do repositório, onde existe .git.')
for p in FILEMAP:
 if FILEMAP[p] is None and not (ROOT/p).is_file():
  sys.exit('ERRO: arquivo existente não encontrado: '+p)
 if FILEMAP[p]=='package' and not (PKG/p).is_file():
  sys.exit('ERRO: arquivo do pacote não encontrado: '+str(PKG/p))

planned={p:(ROOT/p).read_text(encoding='utf8') for p in FILEMAP if FILEMAP[p] is None}

# 1. Corrige somente os valores dentro de meta (sem reformatar as 87 questões).
p='labour-law/convencao-acordo-coletivo.json'
s=planned[p]
obj=json.loads(s)
counts=Counter(q['type'] for q in obj['questions'])
assert obj['questions'] and len(obj['questions'])==len({q['id'] for q in obj['questions']})
meta,tail=s.split('"questions"',1)
meta,n= re.subn(r'"totalActivities"\s*:\s*\d+',f'"totalActivities": {len(obj["questions"])}',meta,count=1)
if n!=1:raise RuntimeError('metadata: totalActivities não encontrado.')
meta,n=re.subn(r'"typeCounts"\s*:\s*\{[^}]*\}', '"typeCounts": { '+', '.join(f'"{k}": {counts[k]}' for k in ('mcq','fill','tf','drag'))+' }',meta,count=1)
if n!=1:raise RuntimeError('metadata: typeCounts não encontrado.')
planned[p]=meta+'"questions"'+tail
assert json.loads(planned[p])['meta']['totalActivities']==len(obj['questions'])

# 2. Index com P2 no lugar das imagens, não um arquivo de foto.
p='labour-law/index.html';s=planned[p]
s=once(s,'<span class="chip">68 activities</span>','<span class="chip">87 activities</span>','index: contador Convenção') if '<span class="chip">68 activities</span>' in s else s
if 'module--p2' not in s:
 style='''
    /* Próximos bancos da P2: espaço da ilustração substituído por selo tipográfico. */
    .module--p2 .visual{display:grid;place-items:center;min-height:330px;
      background:radial-gradient(circle at 73% 36%,rgba(174,145,255,.20),transparent 46%),
        radial-gradient(circle at 46% 78%,rgba(230,191,120,.095),transparent 41%),#0b1727;}
    .module--p2 .visual .p2-stamp{position:relative;z-index:3;display:grid;place-items:center;
      width:min(75%,300px);min-height:185px;text-align:center;border:1px solid rgba(230,191,120,.24);
      border-radius:16px;color:#e7c689;background:rgba(5,11,20,.36);box-shadow:0 24px 56px rgba(0,0,0,.27)}
    .p2-stamp strong{display:block;font:500 clamp(60px,8vw,99px)/1 'Playfair Display',serif;letter-spacing:-.06em}
    .p2-stamp small{display:block;color:#aeb7ca;font-size:11px;letter-spacing:.13em;text-transform:uppercase;margin-top:8px}
    @media(max-width:760px){.module--p2 .visual{min-height:225px}.p2-stamp strong{font-size:78px}}
'''
 s=once(s,'  </style>',style+'  </style>','index: CSS primeiro style')
 def card(slug,title,desc,num):
  return f'''    <!-- MODULE {num:02d} · CONTEÚDO DA P2 -->
    <a class="module module--p2" href="./{slug}.html">
      <div class="copy">
        <div class="num">Module {num:02d} · P2</div>
        <h2>{title}</h2>
        <div class="desc">{desc}</div>
        <div class="meta"><span class="chip">__COUNT_{slug}__ atividades</span><span class="chip">Múltipla escolha</span><span class="chip">Lacunas</span><span class="chip">V/F</span><span class="chip">Arrastar cartões</span></div>
        <div class="go">START REVIEW <span>→</span></div>
      </div>
      <div class="visual" aria-label="Conteúdo da P2"><div class="p2-stamp"><div><strong>P2</strong><small>Conteúdo da P2</small></div></div></div>
    </a>

'''
  # Note: f-string placeholders below are replaced with counts read directly from JSONs.
 p2_cards=[]
 for slug,title,desc,num in SLUGS:
  text=card(slug,title,desc,num)
  data=json.loads((PKG/'labour-law'/f'{slug}.json').read_text(encoding='utf8'))
  p2_cards.append((slug,text.replace(f'__COUNT_{slug}__',str(len(data['questions'])))))
 collective='\n'.join(text for slug,text in p2_cards[:3])+'\n'
 # Instala imediatamente antes do link do Aviso prévio.
 anchor='    <!-- MODULE 05 -->'
 s=once(s,anchor,collective+'    <!-- MODULE 08 -->','index: antes de aviso prévio')
 # Insere 4o módulo após cartão do Aviso, antes da lista de módulos encerrar.
 anchor='\n\n  </div>\n\n\n  <footer>'
 s=once(s,anchor,'\n'+p2_cards[3][1]+anchor,'index: final módulos')
 planned[p]=s

# 3. Registro central de bancos em engagement.js e no endpoint da API.
p='labour-law/engagement.js';s=planned[p]
if '"contribuicao-assistencial.html"' not in s:
 old='''    "aviso-previo.html":
      "aviso-previo"'''
 new='''    "aviso-previo.html":
      "aviso-previo",

    "contribuicao-assistencial.html":
      "contribuicao-assistencial",

    "liberdade-sindical.html":
      "liberdade-sindical",

    "organizacao-sindical.html":
      "organizacao-sindical",

    "suspensao-interrupcao-contrato.html":
      "suspensao-interrupcao-contrato"'''
 s=once(s,old,new,'engagement: bancos')
planned[p]=s

p='functions/api/engagement.js';s=planned[p]
if '"contribuicao-assistencial"' not in s.split('function json(',1)[0]:
 s=once(s,'  "aviso-previo"\n]);','''  "aviso-previo",
  "contribuicao-assistencial",
  "liberdade-sindical",
  "organizacao-sindical",
  "suspensao-interrupcao-contrato"
]);''','API: bancos permitidos')
planned[p]=s

# 4. Popup e ranking, preservando layout anterior da xícara.
p='labour-law/support-popup.js';s=planned[p]
if '"liberdade-sindical.html"' not in s.split('function readSupportState',1)[0]:
 s=once(s,'    "mensalidade-sindical.html"\n  ]);','''    "mensalidade-sindical.html",
    "contribuicao-assistencial.html",
    "liberdade-sindical.html",
    "organizacao-sindical.html",
    "suspensao-interrupcao-contrato.html"
  ]);''','popup: bancos')
 # Corrige o reconhecimento de caminhos do Pages sem extensão .html.
 s=once(s,'''        LABOUR_REVIEW_PAGES.has(
          filename
        )''','''        (LABOUR_REVIEW_PAGES.has(filename) || LABOUR_REVIEW_PAGES.has(filename + ".html"))''','popup: URLs limpas')
planned[p]=s

p='labour-law/mais-curtidas.html';s=planned[p]
if '"contribuicao-assistencial"' not in s.split('function escapeHtml',1)[0]:
 s=once(s,'      "aviso-previo":\n        "Aviso prévio"','''      "aviso-previo":
        "Aviso prévio",

      "contribuicao-assistencial":
        "Contribuição Assistencial",

      "liberdade-sindical":
        "Liberdade sindical",

      "organizacao-sindical":
        "Organização sindical",

      "suspensao-interrupcao-contrato":
        "Suspensão e Interrupção do Contrato"''','ranking: bancos')
planned[p]=s

for slug,_,_,_ in SLUGS:
 for ext in ('html','json'):
  target=f'labour-law/{slug}.{ext}'
  planned[target]=(PKG/target).read_text(encoding='utf8')
for filename in ('p2-quiz.js','p2-quiz.css'):
 target='labour-law/'+filename
 planned[target]=(PKG/target).read_text(encoding='utf8')

# Validação ANTES de gravar, todas as quatro fontes e os 10 arquivos novos.
for slug,_,_,_ in SLUGS:
 data=json.loads(planned[f'labour-law/{slug}.json'])
 items=data['questions']
 if len(items)!=len({q['id'] for q in items}) or not items:raise RuntimeError('IDs duplicados: '+slug)
 if data['meta']['totalActivities']!=len(items):raise RuntimeError('totalActivities: '+slug)
 if any(data['meta']['typeCounts'][t]!=sum(q['type']==t for q in items) for t in ('mcq','fill','tf','drag')):
  raise RuntimeError('typeCounts: '+slug)
 for q in items:
  if not q['prompt'] or not q['explanation']:raise RuntimeError('Enunciado/explicação vazia em '+q['id'])
  if q['type']=='fill' and q['prompt'].count('{{blank}}')!=len(q['answers']):raise RuntimeError('Lacunas inconsistentes')
  if q['type']=='drag' and not all(c['zone'] in [z['id'] for z in q['zones']] for c in q['cards']):raise RuntimeError('Cartões inconsistentes')
  if q['type']=='mcq' and not (0<=q['answer']<len(q['options'])):raise RuntimeError('Gabarito incorreto')
for slug,_,_,_ in SLUGS:
 for path in ('labour-law/index.html','labour-law/engagement.js','functions/api/engagement.js','labour-law/support-popup.js','labour-law/mais-curtidas.html'):
  if slug not in planned[path]:raise RuntimeError('Banco ausente de integração: '+slug+' em '+path)

changes=[(p,body) for p,body in planned.items() if not (ROOT/p).exists() or (ROOT/p).read_text(encoding='utf8')!=body]
for p,_ in changes:
 (ROOT/p).parent.mkdir(parents=True,exist_ok=True)
for p,body in changes:
 (ROOT/p).write_text(body,encoding='utf8')
print(f'OK: {len(changes)} arquivo(s) gerados/atualizados com sucesso.')
print('Metadados de Convenção:',len(obj['questions']),dict(counts))
for slug,_,_,_ in SLUGS:
 print(slug, len(json.loads(planned[f'labour-law/{slug}.json'])['questions']))
print('Revise git diff --stat e node --check antes do commit.')
