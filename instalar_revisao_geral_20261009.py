#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legis Lectiones: atualização integrada (aviso, revisão sindical e som global).

Execute na raiz do repositório, em BRANCH DE TRABALHO:
    python3 instalar_revisao_geral_20261009.py --check
    python3 instalar_revisao_geral_20261009.py --apply
    python3 instalar_revisao_geral_20261009.py --verify

Requer o instalador já versionado instalar_revisao_aviso_previo.py, mas não o executa:
reaproveita seus dados auditados e faz UMA transação com backup e rollback.
Não usa npm, pip, rede, credenciais, Cloudflare ou git push.
"""
from __future__ import annotations
import argparse
import collections
import copy
import difflib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

REPO = 'mmillenaa/legis-lectiones'
BACKUP_DIR = '.local-backups/revisao-integrada-20261009'
SOUND_PATH = 'audio-preferences.js'
REVISION = '20261009'
SECTION = '0. Revisão de prova — natureza, filiação e prazos'

# Questões com gabarito explícito: preservam TODOS os IDs existentes.
NEW_ITEMS = {
 'convencao-acordo-coletivo': [
  dict(id='REV20261009_INTERVALO', section=SECTION, type='mcq',
       prompt='Segundo o art. 611-A, III, da CLT, a convenção ou o acordo coletivo pode reduzir o intervalo intrajornada de quem trabalha mais de seis horas, observado o mínimo de:',
       options=['20 minutos.', '1 hora e 30 minutos.', '30 minutos.', '2 horas.'], answer=2,
       explanation='O art. 611-A, III, da CLT admite negociação coletiva sobre o intervalo intrajornada, respeitado o mínimo de 30 minutos para jornadas superiores a 6 horas. A regra geral do art. 71 é de, no mínimo, uma hora; não confundir as hipóteses.',
       reviewGroup='prova-2026-intervalo')
 ],
 'contribuicao-sindical': [
  dict(id='REV20261009_SINDICAL_ATUAL', section=SECTION, type='mcq',
       prompt='Após a Reforma Trabalhista de 2017, qual formulação melhor descreve a contribuição sindical, inclusive quanto à filiação e à natureza jurídica na posição de Sérgio Pinto Martins?',
       options=[
        'Permanece tributo compulsório de todos os trabalhadores, filiados ou não.',
        'É facultativa, exige autorização prévia e expressa, não decorre automaticamente da filiação; segundo o autor, perdeu a natureza tributária pela ausência de compulsoriedade.',
        'É mensalidade associativa obrigatória somente para quem se filiou.',
        'Pode ser instituída contra não filiados apenas por deliberação assemblear, sem autorização individual.'
       ], answer=1,
       explanation='Os arts. 578 e 579 da CLT condicionam a contribuição sindical à autorização prévia e expressa. Sérgio Pinto Martins associa o fim da compulsoriedade à perda da natureza tributária. Facultatividade é característica da cobrança; natureza jurídica é pergunta distinta. Filiação, isoladamente, não equivale à autorização específica.',
       reviewGroup='prova-2026-sindical-atual'),
  dict(id='REV20261009_SINDICAL_HISTORICO', section=SECTION, type='mcq',
       prompt='No regime anterior à Reforma Trabalhista de 2017, a contribuição sindical obrigatória era tradicionalmente classificada quanto à sua natureza como:',
       options=['Privada associativa.', 'Tributária.', 'Doação facultativa.', 'Mensalidade sindical exclusiva dos associados.'], answer=1,
       explanation='Na disciplina compulsória anterior a 2017, a contribuição sindical era tratada como contribuição tributária de interesse de categoria profissional ou econômica. A partir de 2017 sua cobrança passou a depender de autorização prévia e expressa; não transportar a classificação histórica sem indicar o período.',
       reviewGroup='prova-2026-sindical-historico')
 ],
 'contribuicao-confederativa': [
  dict(id='REV20261009_CONFEDERATIVA', section=SECTION, type='mcq',
       prompt='Qual é a natureza jurídica e quem pode ser obrigado ao pagamento da contribuição confederativa prevista no art. 8º, IV, da Constituição?',
       options=[
        'Tributária; todos os integrantes da categoria, independentemente de filiação.',
        'Tributária; apenas os sindicatos podem recolhê-la.',
        'Não tributária; todos os trabalhadores, se a norma coletiva garantir direito de oposição.',
        'Não tributária e associativa; somente os filiados ao sindicato respectivo, conforme a Súmula Vinculante 40.'
       ], answer=3,
       explanation='A contribuição confederativa não é tributo, decorre da deliberação associativa e só pode ser exigida dos filiados (SV 40 do STF). A hipótese de não filiados com direito de oposição é da contribuição assistencial, não da confederativa.',
       reviewGroup='prova-2026-confederativa')
 ],
 'mensalidade-sindical': [
  dict(id='REV20261009_MENSALIDADE', section=SECTION, type='mcq',
       prompt='A mensalidade (contribuição associativa) sindical tem qual natureza e depende de filiação?',
       options=[
        'Natureza privada associativa; decorre da filiação e do estatuto e não se exige de quem apenas pertence à categoria sem se filiar.',
        'Natureza tributária; é devida por filiados e não filiados.',
        'Natureza de contribuição assistencial; dispensa filiação se existir direito de oposição.',
        'Natureza fiscal; depende apenas da folha de pagamento.'
       ], answer=0,
       explanation='A mensalidade é prestação associativa de natureza privada, vinculada à filiação e às regras estatutárias. Não se confunde com a sindical legal, com a assistencial prevista em instrumento coletivo nem com a confederativa.',
       reviewGroup='prova-2026-mensalidade')
 ],
 'contribuicao-assistencial': [
  dict(id='REV20261009_ASSISTENCIAL', section=SECTION, type='mcq',
       prompt='Quanto à contribuição assistencial prevista em acordo ou convenção coletiva, qual é a natureza da cobrança e quais trabalhadores podem ser alcançados pelo regime do Tema 935 do STF?',
       options=[
        'Tributária; somente filiados, sem direito de oposição.',
        'Tributária; toda a categoria, por lançamento fiscal.',
        'Não tributária; filiados e não filiados podem ser alcançados, assegurado aos não filiados o direito de oposição.',
        'Mensalidade associativa; exclusivamente filiados, com valor fixado na carteira de trabalho.'
       ], answer=2,
       explanation='A contribuição assistencial tem fonte negocial coletiva e natureza não tributária. No Tema 935, o STF admitiu cobrança também dos não filiados, desde que assegurado o direito de oposição. Em 2025, explicitou limites como vedação de cobrança retroativa no período em que o STF a considerava inconstitucional e razoabilidade do valor.',
       reviewGroup='prova-2026-assistencial')
 ]
}

LEGAL_INFO = {
 'contribuicao-sindical': {
  'naturezaAnteriorA2017':'tributária e compulsória (classificação histórica)',
  'naturezaAtualSegundoMartins':'não tributária após o fim da compulsoriedade; recolhimento facultativo',
  'filiacao':'não é pressuposto suficiente nem obrigatório; exige autorização prévia e expressa do contribuinte',
  'fundamento':'CLT, arts. 578 e 579; Lei 13.467/2017'
 },
 'contribuicao-confederativa': {
  'natureza':'privada/não tributária, associativa',
  'filiacao':'cobrança exigível somente de filiados ao sindicato respectivo',
  'fundamento':'Constituição art. 8º, IV; STF, Súmula Vinculante 40'
 },
 'mensalidade-sindical': {
  'natureza':'privada/associativa, não tributária',
  'filiacao':'sim; decorre da filiação voluntária e das regras do estatuto',
  'fundamento':'liberdade sindical e regras associativas'
 },
 'contribuicao-assistencial': {
  'natureza':'privada/negocial, não tributária',
  'filiacao':'não; pode alcançar não filiados desde que assegurado direito de oposição',
  'fundamento':'STF Tema 935 (ARE 1018459), esclarecimentos de novembro de 2025'
 }
}
BASE_COUNTS = {
 'convencao-acordo-coletivo':87,
 'contribuicao-sindical':62,
 'contribuicao-confederativa':60,
 'mensalidade-sindical':55,
 'contribuicao-assistencial':22,
 'liberdade-sindical':13,
 'organizacao-sindical':36,
 'aviso-previo':67,
 'suspensao-interrupcao-contrato':22,
}
NEW_COUNTS = {**BASE_COUNTS, 'aviso-previo':71}
for _slug,_items in NEW_ITEMS.items():NEW_COUNTS[_slug]+=len(_items)
assert sum(BASE_COUNTS.values())==424
assert sum(NEW_COUNTS.values())==434

KEYS = {
 'convencao-acordo-coletivo':("'law-mock-tests:labour:collective-bargaining:v2'","'law-mock-tests:labour:collective-bargaining:v3'"),
 'contribuicao-sindical':("'law-mock-tests:labour:union-contribution:v2'","'law-mock-tests:labour:union-contribution:v3'"),
 'contribuicao-confederativa':("'legis-lectiones:labour:confederative-contribution:v3'","'legis-lectiones:labour:confederative-contribution:v4'"),
 'mensalidade-sindical':("'law-mock-tests:labour:membership-fee:v1'","'law-mock-tests:labour:membership-fee:v2'"),
}

AUDIO_SOURCE = r'''/* Legis Lectiones — preferência global de efeitos sonoros, 2026-10-09.
   Mesma origem: localStorage persiste entre decks; storage propaga para outras abas.
   Afeta apenas AUDIO; não silencia vídeos ou recursos de acessibilidade. */
(() => {
  'use strict';
  if (window.LegisAudio) return;
  const KEY = 'legis-lectiones:sound-enabled:v1';
  const playing = new Set();
  let enabled = true;
  try { enabled = window.localStorage.getItem(KEY) !== 'false'; } catch (_) { /* Navegação restrita */ }

  const nativePlay = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function (...args) {
    if (this instanceof HTMLAudioElement) {
      if (!enabled) return Promise.resolve();
      playing.add(this);
      this.addEventListener('ended', () => playing.delete(this), {once:true});
    }
    return nativePlay.apply(this, args);
  };

  let button = null;
  function updateButton() {
    if (!button) return;
    button.textContent = enabled ? '🔊 Som ligado' : '🔇 Som desligado';
    button.setAttribute('aria-label', enabled ? 'Desativar efeitos sonoros em todos os simulados' : 'Ativar efeitos sonoros em todos os simulados');
    button.setAttribute('title', enabled ? 'Desativar sons (todos os decks)' : 'Ativar sons (todos os decks)');
    button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    button.dataset.soundEnabled = String(enabled);
  }
  function apply(enabledNext, save) {
    const previous = enabled;
    enabled = !!enabledNext;
    if (save) {
      try { window.localStorage.setItem(KEY, String(enabled)); } catch (_) { /* Navegação restrita */ }
    }
    if (!enabled) {
      for (const sound of playing) { try { sound.pause(); } catch (_) { /* ignorar */ } }
      playing.clear();
      document.querySelectorAll('audio').forEach(sound => { try { sound.pause(); } catch (_) { /* ignorar */ } });
    }
    updateButton();
    if (enabled !== previous) {
      window.dispatchEvent(new CustomEvent('legis-sound-change', {detail: {enabled}}));
    }
  }

  window.LegisAudio = Object.freeze({
    isEnabled: () => enabled,
    setEnabled: value => apply(value, true),
    storageKey: KEY
  });
  window.addEventListener('storage', event => {
    if (event.key !== KEY && event.key !== null) return;
    let preference = true;
    try { preference = window.localStorage.getItem(KEY) !== 'false'; } catch (_) { /* ignorar */ }
    apply(preference, false);
  });

  function installButton() {
    if (document.getElementById('legis-global-sound')) return;
    const style = document.createElement('style');
    style.textContent = `
      #legis-global-sound {
        position:fixed; top:max(12px, env(safe-area-inset-top)); right:12px;
        z-index:2147482000; display:flex; align-items:center; justify-content:center;
        gap:6px; min-height:40px; padding:7px 12px;
        background:rgba(14,22,39,.94); color:#f5f6fb; border:1px solid rgba(197,175,255,.50);
        border-radius:999px; box-shadow:0 6px 22px rgba(0,0,0,.30);
        font:600 12px/1.2 system-ui,-apple-system,'Segoe UI',sans-serif;
        cursor:pointer; -webkit-tap-highlight-color:transparent;
      }
      #legis-global-sound:hover {background:rgba(39,35,68,.96)}
      #legis-global-sound:focus-visible {outline:3px solid #d6c6ff; outline-offset:2px}
      #legis-global-sound[data-sound-enabled="false"] {opacity:.78}
      @media(max-width:520px) {#legis-global-sound {top:max(8px, env(safe-area-inset-top)); right:8px; font-size:11px; padding:7px 9px; min-height:36px}}
    `;
    document.head.appendChild(style);
    button = document.createElement('button');
    button.id = 'legis-global-sound';
    button.type = 'button';
    button.addEventListener('click', () => apply(!enabled, true));
    document.body.appendChild(button);
    updateButton();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', installButton, {once:true});
  else installButton();
})();
'''

class SafeStop(Exception):pass

def git(*args, root=None, check=True):
 p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True)
 if check and p.returncode!=0:raise SafeStop(f"git {' '.join(args)}: {p.stderr.strip() or p.stdout.strip()}")
 return p.stdout.strip() if check else p

def read(root, rel):
 p=root/rel
 if not p.is_file():raise SafeStop(f'Arquivo esperado ausente: {rel}')
 return p.read_bytes()

def txt(root, rel):return read(root,rel).decode('utf-8')

def load_base_installer(root):
 path=root/'instalar_revisao_aviso_previo.py'
 if not path.is_file():raise SafeStop('Faltando instalar_revisao_aviso_previo.py na raiz: atualize main primeiro.')
 spec=importlib.util.spec_from_file_location('aviso_base_20261009',path)
 mod=importlib.util.module_from_spec(spec)
 assert spec.loader
 spec.loader.exec_module(mod)
 expected={'labour-law/aviso-previo.json','labour-law/aviso-previo.html','README.md'}
 if set(mod.FILES)!=expected or mod.NEW_STORAGE!="'law-mock-tests:labour:aviso-previo:v3'":
  raise SafeStop('O instalador de aviso prévio do repositório difere da versão auditada. Pare.')
 return mod

def to_json(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def validate_question_bank(b, name):
 q=b['questions']; ids=set()
 for item in q:
  v=item.get('id')
  if not v or v in ids:raise SafeStop(f'{name}: IDs ausentes/duplicados ({v})')
  ids.add(v)
  t=item.get('type')
  if not isinstance(item.get('prompt'),str) or not item['prompt'].strip():raise SafeStop(f'{name}/{v}: enunciado vazio')
  if t=='mcq':
   o=item.get('options'); a=item.get('answer')
   if not isinstance(o,list) or len(o)!=4 or len(set(o))!=4 or type(a)!=int or not 0<=a<4:raise SafeStop(f'{name}/{v}: gabarito/opções inválidas')
  elif t=='fill':
   ans=item.get('answers'); n=item['prompt'].count('{{blank}}')
   if not isinstance(ans,list) or len(ans)!=n or any(not isinstance(z,list) or not z or any(not isinstance(s,str) or not s.strip() for s in z) for z in ans):raise SafeStop(f'{name}/{v}: lacunas inválidas')
  elif t=='tf':
   if not isinstance(item.get('statements'),list) or not item['statements'] or any(type(z.get('answer'))!=bool for z in item['statements']):raise SafeStop(f'{name}/{v}: V/F inválido')
  elif t=='drag':
   z=item.get('zones');c=item.get('cards');
   if not isinstance(z,list) or not isinstance(c,list) or not z or not c or any(x.get('zone') not in {w.get('id') for w in z} for x in c):raise SafeStop(f'{name}/{v}: associação inválida')
  else:raise SafeStop(f'{name}/{v}: formato desconhecido')
 counts=dict(collections.Counter(x['type'] for x in q))
 expected=b.get('meta',{}).get('typeCounts',{})
 if counts!={k:v for k,v in expected.items() if v}:raise SafeStop(f'{name}: meta.typeCounts diverge: {counts} vs {expected}')
 if b.get('meta',{}).get('totalActivities')!=len(q):raise SafeStop(f'{name}: meta.totalActivities incorreto')


def transform_bank(root, slug):
 rel=f'labour-law/{slug}.json'
 orig=json.loads(txt(root,rel))
 if len(orig.get('questions',[])) not in [BASE_COUNTS[slug],NEW_COUNTS[slug]]:
  raise SafeStop(f'{slug}: banco não corresponde às contagens previstas; nada será sobrescrito.')
 want={x['id'] for x in NEW_ITEMS[slug]}; exists={x.get('id') for x in orig['questions']}; found=want&exists
 if found and found!=want:raise SafeStop(f'{slug}: atualização parcial de questões, interrompido.')
 if found:
  if len(orig['questions'])!=NEW_COUNTS[slug] or [x['id'] for x in orig['questions'][:len(NEW_ITEMS[slug])]]!=[x['id'] for x in NEW_ITEMS[slug]]:
   raise SafeStop(f'{slug}: questões revisadas não estão no começo do banco.')
  for idx, q in enumerate(NEW_ITEMS[slug]):
   if orig['questions'][idx]!=q:raise SafeStop(f'{slug}: questão revisada {q["id"]} divergiu do arquivo auditado.')
  result=orig
 else:
  if len(orig['questions'])!=BASE_COUNTS[slug]:raise SafeStop(f'{slug}: contagem inicial inesperada.')
  result=copy.deepcopy(orig)
  result['questions']=copy.deepcopy(NEW_ITEMS[slug])+result['questions']
  meta=result['meta'];meta['totalActivities']=len(result['questions']); meta['typeCounts']=dict(collections.Counter(q['type'] for q in result['questions']))
  meta['version']=str(meta.get('version','1.0'))+'-rev20261009'
  meta['sourceNote']=(meta.get('sourceNote','').rstrip()+ ' Acrescidas questões iniciais sobre natureza, filiação, direito de oposição e/ou prazos, com delimitação histórica.').strip()
  if slug in LEGAL_INFO:meta['legalRegime']=copy.deepcopy(LEGAL_INFO[slug])
 validate_question_bank(result,slug)
 if len(result['questions'])!=NEW_COUNTS[slug]:raise SafeStop(f'{slug}: total final inesperado.')
 return to_json(result) if not found else read(root,rel)


def only_once(s, old, new, what):
 if new in s and old not in s:return s
 if s.count(old)!=1 or new in s:raise SafeStop(f'{what}: não encontrei exatamente uma referência original; não atualizar parcialmente.')
 return s.replace(old,new,1)


def transform_readme(s):
 expected={1:'convencao-acordo-coletivo',2:'contribuicao-sindical',3:'contribuicao-confederativa',4:'mensalidade-sindical',5:'contribuicao-assistencial',6:'liberdade-sindical',7:'organizacao-sindical',8:'aviso-previo',9:'suspensao-interrupcao-contrato'}
 for index, slug in expected.items():
  patt=re.compile(r'^(\|\s*\*\*'+f'{index:02d}'+r'\*\*\s*\|[^\n|]*\|\s*)(\d+)(\s*\|)',re.M)
  m=patt.search(s)
  if not m:raise SafeStop(f'README: linha {index:02d} não encontrada.')
  found=int(m.group(2));before=71 if slug=='aviso-previo' else BASE_COUNTS[slug]
  if slug=='aviso-previo':allowed={67,71}
  else:allowed={before,NEW_COUNTS[slug]}
  if found not in allowed:raise SafeStop(f'README: contagem inesperada em {slug}: {found}')
  s=s[:m.start(2)]+str(NEW_COUNTS[slug])+s[m.end(2):]
 total=re.search(r'^(\|\s*\*\*Total\*\*\s*\|[^\n|]*\|\s*\*\*)(\d+)(\*\*\s*\|)',s,re.M)
 if not total or int(total.group(2)) not in (424,428,434):raise SafeStop('README: total não encontrado ou inesperado.')
 s=s[:total.start(2)]+'434'+s[total.end(2):]
 return s


def transform_p2(s):
 old='const STORAGE = `legis-lectiones:labour:${slug}:v1`;'
 new='const STORAGE = `legis-lectiones:labour:${slug}:${document.body.dataset.progressVersion || "v1"}`;'
 return only_once(s,old,new,'p2-quiz.js')


def transform_celestial(s):
 if 'legis-sound-change' in s and 'LegisAudio.isEnabled()' in s:return s
 s=only_once(s,'  let winAudioElement = null;','  let winAudioElement = null;\n  let activeWebAudioWin = null;\n  window.addEventListener("legis-sound-change", (event) => {\n    if (event.detail && !event.detail.enabled && activeWebAudioWin) {\n      try { activeWebAudioWin.stop(); } catch (_) { /* ignora audio ja encerrado */ }\n      activeWebAudioWin = null;\n    }\n    if (event.detail && !event.detail.enabled && winAudioElement) {\n      try { winAudioElement.pause(); } catch (_) { /* ignora */ }\n    }\n  });','result-celestial.js winAudioElement')
 s=only_once(s,'  function armAudio() {\n','  function armAudio() {\n    if (window.LegisAudio && !window.LegisAudio.isEnabled()) return;\n','result-celestial.js armAudio')
 s=only_once(s,'    celebratedThisAttempt = true;','    celebratedThisAttempt = true;\n    if (window.LegisAudio && !window.LegisAudio.isEnabled()) return;','result-celestial.js playWinOnce')
 s=only_once(s,'        source.start(0);','        source.start(0);\n        activeWebAudioWin = source;\n        source.onended = () => { if (activeWebAudioWin === source) activeWebAudioWin = null; };','result-celestial.js source.start')
 return s


def transform_html(s, rel):
 if not s.lower().count('<head>')==1 or not s.lower().count('</head>')==1:raise SafeStop(f'{rel}: <head> fora do padrão; não injetar.')
 relsrc=('../' if '/' in rel else './')+SOUND_PATH
 marker=f'<script src="{relsrc}" defer></script>'
 if marker not in s:
  if 'audio-preferences.js' in s:raise SafeStop(f'{rel}: parece existir controle de som conflitante.')
  s=s.replace('<head>', '<head>\n  '+marker,1)
 # progress stored version changed to keep FIRST questions at first position
 stem=Path(rel).stem
 if rel.startswith('labour-law/') and stem in KEYS:
  old,new=KEYS[stem]
  s=only_once(s,old,new,f'{rel} progress')
 if rel=='labour-law/contribuicao-assistencial.html':
  s=only_once(s,'<body data-bank="contribuicao-assistencial">','<body data-bank="contribuicao-assistencial" data-progress-version="v2">',rel)
 return s


def all_pages(root):
 pages=[Path('index.html')]
 for group in ('labour-law','civil-procedure','philosophy-of-law'):
  pages += [p.relative_to(root) for p in sorted((root/group).glob('*.html'))]
 if len(pages)<20:raise SafeStop(f'Somente {len(pages)} páginas HTML detectadas; confira estrutura do repositório.')
 return [p.as_posix() for p in pages]


def expected_and_report(root, allow_installed=False):
 if not (root/'.git').exists():raise SafeStop('Execute na raiz do repositório Git.')
 remote=git('remote','get-url','origin',root=root)
 if not remote.rstrip('/').removesuffix('.git').endswith('mmillenaa/legis-lectiones'):
  raise SafeStop(f'Origin não aponta para {REPO}: {remote}')
 branch=git('branch','--show-current',root=root)
 if not branch or branch in ('main','master'):
  raise SafeStop('Proteção: trabalhe em branch fix/*, nunca diretamente em main.')
 existing_dirty=git('diff','--name-only','HEAD',root=root)
 if existing_dirty and not allow_installed:
  raise SafeStop('Há alterações em arquivos rastreados antes da instalação. Salve/reveja primeiro:\n'+existing_dirty)
 avis=load_base_installer(root)
 final={}
 current_aviso=read(root,'labour-law/aviso-previo.json')
 revised_blob, revised_bank = avis.embedded_json()
 already_installed = current_aviso==revised_blob and all(
  set(q['id'] for q in json.loads(txt(root,f'labour-law/{slug}.json'))['questions']).issuperset(
   {x['id'] for x in additions}) for slug,additions in NEW_ITEMS.items())
 if already_installed:
  aviso_state='ja-revisado'; total_before=434
  final['labour-law/aviso-previo.json']=current_aviso
  final['labour-law/aviso-previo.html']=read(root,'labour-law/aviso-previo.html')
  final['README.md']=read(root,'README.md')
  if avis.NEW_STORAGE not in final['labour-law/aviso-previo.html'].decode('utf-8'):
   raise SafeStop('Aviso revisado mas chave de progresso antiga.')
 else:
  avis_desired, _, aviso_state, counts_before, total_before = avis.assemble(root)
  for rel,blob in avis_desired.items():final[rel]=blob
 for slug in NEW_ITEMS: final[f'labour-law/{slug}.json']=transform_bank(root,slug)
 final['README.md']=transform_readme(final['README.md'].decode('utf-8')).encode('utf-8')
 final['labour-law/p2-quiz.js']=transform_p2(txt(root,'labour-law/p2-quiz.js')).encode('utf-8')
 final['labour-law/result-celestial.js']=transform_celestial(txt(root,'labour-law/result-celestial.js')).encode('utf-8')
 for rel in all_pages(root):
  base=final[rel].decode('utf-8') if rel in final else txt(root,rel)
  final[rel]=transform_html(base,rel).encode('utf-8')
 final[SOUND_PATH]=AUDIO_SOURCE.encode('utf-8')
 for slug in BASE_COUNTS:
  rel=f'labour-law/{slug}.json'
  value=final[rel] if rel in final else read(root,rel)
  data=json.loads(value)
  validate_question_bank(data,slug)
  if len(data['questions'])!=NEW_COUNTS[slug]:raise SafeStop(f'Contagem {slug}: {len(data["questions"])} != {NEW_COUNTS[slug]}')
 for slug in NEW_ITEMS:
  q=json.loads(final[f'labour-law/{slug}.json'])['questions']
  first=[x['id'] for x in NEW_ITEMS[slug]]
  if [x['id'] for x in q[:len(first)]]!=first:raise SafeStop(f'Questões iniciais não estão primeiro: {slug}')
 for slug in LEGAL_INFO:
  actual=json.loads(final[f'labour-law/{slug}.json'])['meta'].get('legalRegime')
  if actual!=LEGAL_INFO[slug]:raise SafeStop(f'Informações sobre natureza/filiação divergiram: {slug}')
 s=final['README.md'].decode('utf-8')
 if '| **Total** | **9 study modules** | **434** |' not in s:raise SafeStop('Total no README inesperado.')
 for rel in all_pages(root):
  src='../audio-preferences.js' if '/' in rel else './audio-preferences.js'
  if f'<script src="{src}" defer></script>' not in final[rel].decode('utf-8'):raise SafeStop(f'Controle de som ausente em {rel}')
 if len(final)!=len(set(final)):raise SafeStop('Caminho duplicado.')
 actual={rel:read(root,rel) if (root/rel).exists() else None for rel in final}
 changed=[rel for rel,blob in final.items() if actual[rel]!=blob]
 if allow_installed and existing_dirty:
  edited=set(existing_dirty.splitlines())
  outside=edited-set(final)
  if outside:raise SafeStop('Alterações locais não relacionadas à revisão: '+', '.join(sorted(outside)))
 return final, changed, branch, aviso_state, total_before


def write_atomic(path,blob):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.legis-temp-',dir=str(path.parent))
 try:
  with os.fdopen(fd,'wb') as f:
   f.write(blob);f.flush();os.fsync(f.fileno())
  if path.exists():shutil.copymode(path,tmp)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)


def main():
 parser=argparse.ArgumentParser(description='Atualização integrada revisada do Legis Lectiones')
 cmd=parser.add_mutually_exclusive_group(required=True)
 cmd.add_argument('--check',action='store_true',help='simula e lista mudanças; NÃO grava')
 cmd.add_argument('--apply',action='store_true',help='faz backup e aplica atomicamente, sem commit')
 cmd.add_argument('--verify',action='store_true',help='confere o estado após --apply')
 args=parser.parse_args()
 root=Path.cwd().resolve()
 final,changed,branch,aviso_state,total_before=expected_and_report(root, allow_installed=args.verify)
 print('Branch:',branch)
 print('Estado Aviso:',aviso_state,'| total atual:',total_before,'| total final esperado: 434')
 print('Bancos de contribuição: sindical 64, confederativa 61, mensalidade 56, assistencial 23')
 print('Negociação coletiva: 88 | Aviso prévio: 71 | demais sem alterações')
 print('Páginas HTML com controle de som:',len(all_pages(root)))
 print('Arquivos a alterar:',len(changed))
 for rel in sorted(changed): print('  ',rel)
 if args.verify:
  if changed:raise SafeStop('Verificação incompleta: alterações pendentes. Verifique backup, versões e arquivos.')
  print('VERIFICAÇÃO OK: 434 atividades, seis novas questões, áudio global e armazenamento versionado.');return
 if not changed:
  print('A atualização já está aplicada. Sem alterações.');return
 if args.check:
  print('SIMULAÇÃO APROVADA: nenhum arquivo foi modificado.');return
 # Enforce sound script isn't an unexpected preexisting untracked file
 for rel in changed:
  path=root/rel
  if not path.exists() and rel!=SOUND_PATH:raise SafeStop(f'Novo arquivo não autorizado: {rel}')
  if rel==SOUND_PATH and path.exists():raise SafeStop('audio-preferences.js já existe mas diverge; não sobrescrever.')
 backup=root/BACKUP_DIR
 if backup.exists():raise SafeStop(f'Backup {BACKUP_DIR} já existe; não sobrescrever.')
 backup.mkdir(parents=True)
 restored=[]
 try:
  for rel in changed:
   p=root/rel
   if p.exists():
    backup_target=backup/rel;backup_target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,backup_target)
  for rel in changed:
   write_atomic(root/rel,final[rel]);restored.append(rel)
  # Validate installation without comparing pre-update Git status (now modified, intentionally).
  for rel in changed:
   if read(root,rel)!=final[rel]:raise SafeStop(f'Falha na leitura após gravar: {rel}')
  for slug in BASE_COUNTS:
   data=json.loads(txt(root,f'labour-law/{slug}.json'))
   validate_question_bank(data,slug)
   if len(data['questions'])!=NEW_COUNTS[slug]:raise SafeStop(f'Validação pós-escrita falhou em {slug}')
  if '| **Total** | **9 study modules** | **434** |' not in txt(root,'README.md'):
   raise SafeStop('Validação pós-escrita falhou no README')
 except BaseException:
  for rel in reversed(restored):
   src=backup/rel; target=root/rel
   if src.exists():shutil.copy2(src,target)
   elif rel==SOUND_PATH and target.exists():target.unlink()
  print('Falha: arquivos restaurados com backup; nenhuma alteração foi commitada.',file=sys.stderr)
  raise
 print('INSTALAÇÃO CONCLUÍDA. Backup conservado em',BACKUP_DIR)
 print('Próximos comandos: git diff --check ; git diff --stat ; git status -sb')
 print('Observação: --verify exige a nova versão; rode agora para conferir.')

if __name__=='__main__':
 try:main()
 except SafeStop as e:print('BLOQUEADO COM SEGURANÇA:',e,file=sys.stderr);sys.exit(2)
 except Exception as e:print('ERRO: nada será ignorado:',repr(e),file=sys.stderr);sys.exit(3)
