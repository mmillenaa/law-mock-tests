#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Legis Lectiones — instalador controlado do banco de Aviso Prévio (09/10/2026).

Execute NA RAIZ de um Codespace do repositorio mmillenaa/legis-lectiones:
  python3 instalar_revisao_aviso_previo.py --check   # simula, NAO altera
  python3 instalar_revisao_aviso_previo.py --apply   # instala com backup
  python3 instalar_revisao_aviso_previo.py --verify  # confirma a instalacao

O arquivo inclui o JSON revisado. Nao requer bibliotecas externas, downloads ou Codex.
Altera EXCLUSIVAMENTE:
  labour-law/aviso-previo.json
  labour-law/aviso-previo.html (somente chave do progresso)
  README.md (somente dois numeros)
Nao altera questoes de outros bancos, scripts compartilhados, APIs ou deploy.
"""
import argparse
import base64
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

# Arquivo JSON revisado 2.1 embutido neste instalador; sem dependencia de outro upload.
DATA_BASE64_ZLIB = """
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
/UpinJi4yRBD7byfYeXhdz/7P/R8H0s=
"""
DATA_SHA256 = "3e7b710871326cb2072eaf596c5e5fe6ce19903df58a0320c76c61beb5170f27"
BASELINE_GIT_BLOB_SHA1 = 'd11f07858765ab3fe7096741a229764b607fb09d'
SOURCE_VERSION = '1.1'
TARGET_VERSION = '2.1-revisado-2026-10'
OLD_STORAGE = "'law-mock-tests:labour:aviso-previo:v2'"
NEW_STORAGE = "'law-mock-tests:labour:aviso-previo:v3'"
FILES = ('labour-law/aviso-previo.json', 'labour-law/aviso-previo.html', 'README.md')
BANK_NAMES = (
    'convencao-acordo-coletivo', 'contribuicao-sindical',
    'contribuicao-confederativa', 'mensalidade-sindical',
    'contribuicao-assistencial', 'liberdade-sindical',
    'organizacao-sindical', 'aviso-previo',
    'suspensao-interrupcao-contrato',
)
EXPECTED_OTHER_COUNTS = {
    'convencao-acordo-coletivo': 87,
    'contribuicao-sindical': 62,
    'contribuicao-confederativa': 60,
    'mensalidade-sindical': 55,
    'contribuicao-assistencial': 22,
    'liberdade-sindical': 13,
    'organizacao-sindical': 36,
    'suspensao-interrupcao-contrato': 22,
}

class GuardError(Exception):
    pass

def git_output(*args):
    try:
        p = subprocess.run(['git', *args], capture_output=True, text=True, check=True)
        return p.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as e:
        raise GuardError(f'Nao foi possivel executar git {" ".join(args)}: {e}')

def git_blob_sha(content):
    return hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()

def embedded_json():
    try:
        packed = base64.b64decode(''.join(DATA_BASE64_ZLIB.split()), validate=True)
        raw = zlib.decompress(packed)
    except Exception as e:
        raise GuardError(f'Pacote do JSON incorporado esta danificado: {e}')
    if hashlib.sha256(raw).hexdigest() != DATA_SHA256:
        raise GuardError('Verificacao SHA256 falhou: o JSON incorporado foi alterado!')
    try:
        data=json.loads(raw)
    except ValueError as e:
        raise GuardError(f'JSON incorporado invalido: {e}')
    validate_bank(data)
    return raw, data

def validate_bank(bank):
    if not isinstance(bank,dict) or not isinstance(bank.get('questions'),list):
        raise GuardError('Banco invalido: faltam questions e metadados')
    questions=bank['questions']
    if len(questions)!=71 or bank.get('meta',{}).get('version')!=TARGET_VERSION:
        raise GuardError('Banco nao tem a versao esperada de 71 questoes')
    ids=[q.get('id') for q in questions]
    if len(set(ids))!=71:
        raise GuardError('IDs ausentes/duplicados')
    counts=collections.Counter(q.get('type') for q in questions)
    if counts != {'mcq':51,'fill':11,'tf':4,'drag':5}:
        raise GuardError(f'Formatos inesperados: {dict(counts)}')
    meta=bank['meta']
    if meta.get('totalActivities')!=71 or meta.get('typeCounts')!=dict(counts):
        raise GuardError('Metadados e numero real de atividades divergem')
    for q in questions:
        qid=q['id']
        if not isinstance(q.get('prompt'),str) or not q['prompt'].strip():
            raise GuardError(f'{qid}: enunciado vazio')
        if not isinstance(q.get('explanation'),str) or not q['explanation'].strip():
            raise GuardError(f'{qid}: explicacao vazia')
        if not isinstance(q.get('section'),str) or not q['section']:
            raise GuardError(f'{qid}: secao vazia')
        t=q['type']
        if t=='mcq':
            opts=q.get('options')
            idx=q.get('answer')
            if not isinstance(opts,list) or len(opts)!=4 or any(not isinstance(o,str) or not o.strip() for o in opts) or len(set(opts))!=4:
                raise GuardError(f'{qid}: alternativas invalidas')
            if type(idx) is not int or not 0<=idx<4:
                raise GuardError(f'{qid}: gabarito invalido')
        elif t=='fill':
            a=q.get('answers')
            if not isinstance(a,list) or len(a)!=q['prompt'].count('{{blank}}') or not a:
                raise GuardError(f'{qid}: lacunas e respostas nao correspondem')
            if any(not isinstance(x,list) or not x or any(not isinstance(y,str) or not y.strip() for y in x) for x in a):
                raise GuardError(f'{qid}: respostas de lacunas nao reconheciveis pelo motor')
        elif t=='tf':
            st=q.get('statements')
            if not isinstance(st,list) or len(st)<2 or any(type(s.get('answer')) is not bool or not s.get('text') for s in st):
                raise GuardError(f'{qid}: verdadeiro/falso invalido')
        elif t=='drag':
            zones=q.get('zones')
            cards=q.get('cards')
            if not isinstance(zones,list) or not isinstance(cards,list) or not zones or not cards:
                raise GuardError(f'{qid}: arrastar sem zonas/cartoes')
            zone_ids={z.get('id') for z in zones}
            if len(zone_ids)!=len(zones) or any(c.get('zone') not in zone_ids for c in cards):
                raise GuardError(f'{qid}: cartao ligado a zona inexistente')


def read_utf8(p):
    try:
        return p.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise GuardError(f'Arquivo nao encontrado: {p}')
    except UnicodeError:
        raise GuardError(f'Arquivo nao esta em UTF-8: {p}')

def transform_html(content):
    if content.count(OLD_STORAGE)==1 and NEW_STORAGE not in content:
        return content.replace(OLD_STORAGE, NEW_STORAGE, 1)
    if content.count(NEW_STORAGE)==1 and OLD_STORAGE not in content:
        return content
    raise GuardError('Chave do progresso no HTML nao corresponde a v2 ou v3. Recusado.')

def transform_readme(content):
    old_row='| **08** | Aviso prévio | 67 |'
    new_row='| **08** | Aviso prévio | 71 |'
    old_total='| **Total** | **9 study modules** | **424** |'
    new_total='| **Total** | **9 study modules** | **428** |'
    if content.count(old_row)==1 and content.count(old_total)==1 and new_row not in content and new_total not in content:
        return content.replace(old_row,new_row,1).replace(old_total,new_total,1)
    if content.count(new_row)==1 and content.count(new_total)==1 and old_row not in content and old_total not in content:
        return content
    raise GuardError('Tabela README divergiu dos valores esperados 67/424 ou 71/428. Recusado.')

def validate_other_banks(root):
    values={}
    for name in BANK_NAMES:
        p=root/'labour-law'/f'{name}.json'
        try:
            data=json.loads(read_utf8(p))
        except ValueError as e:
            raise GuardError(f'Outro banco JSON invalido ({p}): {e}')
        questions=data.get('questions')
        if not isinstance(questions,list):
            raise GuardError(f'Banco sem lista de questoes: {p}')
        values[name]=len(questions)
    for name, expected in EXPECTED_OTHER_COUNTS.items():
        if values[name]!=expected:
            raise GuardError(f'{name}: encontrou {values[name]} questoes (esperadas {expected}); README pode estar desatualizado. Pare e confira.')
    if values['aviso-previo'] not in (67,71):
        raise GuardError('Aviso previo nao tem 67 nem 71 questoes. Recusado.')
    total=sum(values.values())
    if total not in (424,428):
        raise GuardError(f'Total de {total} nao esperado. Recusado.')
    return values, total

def assemble(root):
    raw,target=embedded_json()
    current_file=root/FILES[0]
    current_bytes=current_file.read_bytes()
    current=json.loads(current_bytes.decode('utf-8'))
    version=current.get('meta',{}).get('version')
    if current_bytes==raw:
        status='ja-revisado'
    elif version==SOURCE_VERSION and len(current.get('questions',[]))==67 and git_blob_sha(current_bytes)==BASELINE_GIT_BLOB_SHA1:
        status='original-verificado'
    else:
        raise GuardError('O JSON atual nao e o original auditado nem a versao final deste instalador. Nao sobrescrever: revise o diff e a branch.')
    html=read_utf8(root/FILES[1])
    readme=read_utf8(root/FILES[2])
    new_html=transform_html(html)
    new_readme=transform_readme(readme)
    values,total=validate_other_banks(root)
    if status=='original-verificado' and (total!=424 or values['aviso-previo']!=67):
        raise GuardError('Totais dos outros bancos nao correspondem ao README inicial 424.')
    if status=='ja-revisado' and (total!=428 or values['aviso-previo']!=71):
        raise GuardError('Totais dos outros bancos nao correspondem ao README final 428.')
    desired={
        FILES[0]:raw,
        FILES[1]:new_html.encode('utf-8'),
        FILES[2]:new_readme.encode('utf-8'),
    }
    dirty=[p for p,blob in desired.items() if (root/p).read_bytes()!=blob]
    if status=='original-verificado' and len(dirty)!=3:
        raise GuardError('Estado parcialmente atualizado (ou README/HTML ja migrado). Conferir manualmente antes de continuar.')
    if status=='ja-revisado' and dirty:
        raise GuardError('JSON revisado mas HTML/README ainda diferentes: estado parcial. Corrija antes de executar novamente.')
    return desired,dirty,status,values,total

def atomic_write(path, data):
    fd,tmp=tempfile.mkstemp(prefix='.aviso-tmp-',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        shutil.copymode(path,tmp)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def main():
    ap=argparse.ArgumentParser(description='Instalacao segura da revisao de Aviso Previo no Legis Lectiones')
    actions=ap.add_mutually_exclusive_group(required=True)
    actions.add_argument('--check',action='store_true',help='simula sem gravar')
    actions.add_argument('--apply',action='store_true',help='faz backup e atualiza 3 arquivos')
    actions.add_argument('--verify',action='store_true',help='confere se revisao ja esta integralmente aplicada')
    args=ap.parse_args()

    root=Path.cwd().resolve()
    if not (root/'.git').exists() and not (root/'.git').is_file():
        raise GuardError('Abra o terminal na raiz do repositorio (onde existe .git).')
    if not (root/'labour-law'/'aviso-previo.json').is_file():
        raise GuardError('Nao encontrou labour-law/aviso-previo.json. Voce esta na pasta correta?')
    branch=git_output('branch','--show-current')
    if not branch:
        raise GuardError('HEAD destacado; crie uma branch antes de modificar.')
    if args.apply and branch in ('main','master'):
        raise GuardError('Protecao: nao instale diretamente na main. Crie antes uma branch: git switch -c fix/aviso-previo-20261009')
    desired,dirty,status,values,total=assemble(root)
    print('Branch:',branch)
    print('Banco inicial:',status,'| Total atual:',total,'| Questões Aviso:',values['aviso-previo'])
    print('Alvos:', ', '.join(FILES))
    if args.verify:
        if dirty or status!='ja-revisado':
            raise GuardError('Banco nao instalado integralmente; rode --check e, numa branch, --apply.')
        print('OK — arquivos revisados, 71 questoes, total 428; JSON e integridade conferidos.')
        return
    if not dirty:
        print('OK — revisao ja esta aplicada. Nenhuma modificacao necessaria.')
        return
    if args.check:
        print('SIMULACAO: arquivos que seriam alterados:',', '.join(dirty))
        print('Banco: 67 -> 71 | README: 424 -> 428 | armazenamento: v2 -> v3')
        print('SIMULACAO concluida: NENHUM arquivo foi alterado.')
        return
    if args.apply:
        for p in FILES:
            diff = subprocess.run(['git','diff','--quiet','--',p],cwd=root)
            cached = subprocess.run(['git','diff','--cached','--quiet','--',p],cwd=root)
            if diff.returncode!=0 or cached.returncode!=0:
                raise GuardError(f'Ja existem alteracoes locais no arquivo {p}. Nao sobrescrever.')
    backup_dir=root/'.local-backups'/'aviso-previo-20261009'
    if backup_dir.exists():
        raise GuardError(f'Backup existente em {backup_dir}. Nao sobrescrever backups; verifique antes.')
    created_backups=[]
    backup_dir.mkdir(parents=True,exist_ok=False)
    try:
        for p in FILES:
            dest=backup_dir/p
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(root/p,dest)
            created_backups.append(p)
        changed=[]
        try:
            for p in FILES:
                atomic_write(root/p,desired[p])
                changed.append(p)
            _,remain,new_status,new_values,new_total=assemble(root)
            if remain or new_status!='ja-revisado' or new_total!=428:
                raise GuardError('Verificacao pos-gravacao falhou; restaurando originais.')
        except Exception:
            for p in changed:
                shutil.copy2(backup_dir/p,root/p)
            raise
    except Exception:
        # Conserva backup caso a operacao falhe. Nunca exclui os originais.
        raise
    print('INSTALACAO VALIDADA. Alterados:',', '.join(FILES))
    print('Backup:',backup_dir)
    print('Nao faca git add .local-backups nem git add -A!')
    print('Confira: git diff --check && git diff --stat && git diff -- README.md labour-law/aviso-previo.html')

if __name__=='__main__':
    try:
        main()
    except GuardError as e:
        print('BLOQUEADO COM SEGURANCA:',e,file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print('ERRO (operacao interrompida):',repr(e),file=sys.stderr)
        sys.exit(3)
