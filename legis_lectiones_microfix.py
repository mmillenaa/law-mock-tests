#!/usr/bin/env python3
"""Legis Lectiones: controlled UI polish for nine labour-law quiz banks.

Run at repository root: python legis_lectiones_microfix.py
Never changes question JSON, D1, engagement.js, or Cloudflare configuration.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path.cwd()
BASE = ROOT / 'labour-law'
OLD = (
    'convencao-acordo-coletivo',
    'contribuicao-sindical',
    'contribuicao-confederativa',
    'mensalidade-sindical',
    'aviso-previo',
)
NEW = (
    'contribuicao-assistencial',
    'liberdade-sindical',
    'organizacao-sindical',
    'suspensao-interrupcao-contrato',
)
ALL = OLD + NEW

QUICK_FEEDBACK = r'''/* Legis Lectiones · Quick feedback and per-card corrections.
 * Complements the existing question engines without changing their scoring rules.
 */
(() => {
  'use strict';
  const card = document.getElementById('quizCard');
  const check = document.getElementById('checkBtn');
  const feedback = document.getElementById('feedback');
  if (!card || !check || !feedback) return;
  feedback.setAttribute('role', 'status');
  feedback.setAttribute('aria-live', 'polite');
  const slug = document.body.dataset.bank || location.pathname.split('/').pop().replace(/\.html$/i, '');
  let bankPromise;

  const styles = document.createElement('style');
  styles.textContent = `
    #quizCard[data-question-type="mcq"] #checkBtn,
    #quizCard[data-question-type="tf"] #checkBtn,
    #quizCard[data-question-type="drag"] #checkBtn,
    #quizCard.ll-feedback-shown #checkBtn,
    #quizCard #lockBadge {display:none !important}
    #quizCard .drag-card.ll-answer-wrong,
    #quizCard .option.ll-answer-wrong,
    #quizCard .tf-row.ll-answer-wrong {
      border: 2px solid #ff7b91 !important;
      background: rgba(255, 80, 110, .19) !important;
      color: #ffe3e8 !important;
      opacity: 1 !important;
    }
    #quizCard .drag-card.ll-answer-correct,
    #quizCard .option.ll-answer-correct,
    #quizCard .tf-row.ll-answer-correct {
      border: 2px solid #63d8a3 !important;
      background: rgba(99, 216, 163, .12) !important;
      opacity: 1 !important;
    }
    #quizCard .ll-correction {
      display:block; margin-top:5px; font-size:11px; font-weight:700;
      line-height:1.5; color:#ffe3e8;
    }
  `;
  document.head.appendChild(styles);

  function complete(type) {
    if (type === 'mcq') return !!card.querySelector('input[type="radio"]:checked');
    if (type === 'tf') {
      const rows = [...card.querySelectorAll('.tf-row')];
      return rows.length > 0 && rows.every(row => !!row.querySelector('.tf-btn.on'));
    }
    if (type === 'drag') {
      return card.querySelectorAll('.drag-card').length > 0 &&
        !card.querySelector('.drag-pool .drag-card');
    }
    if (type === 'fill') {
      const inputs = [...card.querySelectorAll('.fill-input')];
      return inputs.length > 0 && inputs.every(input => input.value.trim() !== '');
    }
    return false;
  }

  function scheduleSubmit(type) {
    const questionId = card.dataset.questionId;
    queueMicrotask(() => {
      if (card.dataset.questionId !== questionId ||
        card.dataset.questionType !== type ||
        feedback.classList.contains('show') || !complete(type)) return;
      // Trigger the native engine's validator, lock, score and feedback.
      if (!check.disabled) check.click();
    });
  }

  document.addEventListener('change', event => {
    if (card.contains(event.target) && event.target.matches('input[type="radio"]')) {
      scheduleSubmit('mcq');
    }
  }, true);
  document.addEventListener('click', event => {
    if (!card.contains(event.target)) return;
    if (event.target.closest('.tf-btn')) scheduleSubmit('tf');
    else if (event.target.closest('.drop-zone, .drag-pool') &&
      !event.target.closest('.drag-card')) scheduleSubmit('drag');
  }, true);
  document.addEventListener('drop', event => {
    if (card.contains(event.target) && event.target.closest('.drop-zone, .drag-pool')) {
      scheduleSubmit('drag');
    }
  }, true);
  document.addEventListener('keydown', event => {
    if (event.key !== 'Enter' || !card.contains(event.target) ||
      !event.target.matches('.fill-input')) return;
    if (complete('fill') && !feedback.classList.contains('show') && !check.disabled) {
      event.preventDefault();
      check.click();
    }
  });

  function questionData() {
    if (!bankPromise) {
      bankPromise = fetch(new URL('./' + slug + '.json', location.href))
        .then(response => {
          if (!response.ok) throw Error('Question bank HTTP ' + response.status);
          return response.json();
        })
        .catch(err => { console.warn('Quick feedback:', err); return null; });
    }
    return bankPromise;
  }

  function clean(value) { return String(value ?? '').trim(); }
  function locateCard(definitions, element) {
    const id = element.dataset.cardId;
    if (id !== undefined) {
      return definitions.find(def => String(def.id) === id);
    }
    const index = element.dataset.cardIndex ?? element.dataset.index;
    if (index !== undefined) return definitions[Number(index)];
    const same = definitions.filter(def => clean(def.text) === clean(element.textContent));
    return same.length === 1 ? same[0] : undefined;
  }

  function markDrag(question) {
    card.querySelectorAll('.drag-card').forEach(element => {
      if (element.classList.contains('ll-answer-wrong') ||
        element.classList.contains('ll-answer-correct')) return;
      const definition = locateCard(question.cards, element);
      if (!definition) return;
      const location = element.closest('.drop-zone');
      const name = clean(location?.querySelector('.zone-title')?.textContent);
      const zone = location ? question.zones.find(z =>
        z.id === location.dataset.zone || clean(z.label) === name) : undefined;
      const correct = !!zone && zone.id === definition.zone;
      element.classList.add(correct ? 'll-answer-correct' : 'll-answer-wrong');
      if (!correct) {
        const expected = question.zones.find(z => z.id === definition.zone);
        if (expected) {
          const explanation = document.createElement('span');
          explanation.className = 'll-correction';
          explanation.textContent = 'Destino correto: ' + expected.label;
          element.appendChild(explanation);
        }
      }
    });
  }

  function markMcq(question) {
    [...card.querySelectorAll('.option')].forEach((element, index) => {
      if (index === question.answer) element.classList.add('ll-answer-correct');
      else if (element.querySelector('input[type="radio"]:checked'))
        element.classList.add('ll-answer-wrong');
    });
  }

  function markTf(question) {
    [...card.querySelectorAll('.tf-row')].forEach((element, index) => {
      const answer = question.statements?.[index]?.answer;
      const selected = element.querySelector('.tf-btn.on');
      if (typeof answer !== 'boolean' || !selected) return;
      const chosen = selected.textContent.trim().toUpperCase() === 'V';
      element.classList.add(chosen === answer ? 'll-answer-correct' : 'll-answer-wrong');
    });
  }

  function refresh() {
    const finished = feedback.classList.contains('show');
    card.classList.toggle('ll-feedback-shown', finished);
    if (!finished) {
      if (check.textContent !== 'Conferir resposta') check.textContent = 'Conferir resposta';
      return;
    }
    const questionId = card.dataset.questionId;
    questionData().then(data => {
      if (!data || !feedback.classList.contains('show') ||
          card.dataset.questionId !== questionId) return;
      const question = data.questions?.find(q => String(q.id) === questionId);
      if (!question) return;
      if (question.type === 'drag') markDrag(question);
      if (question.type === 'mcq') markMcq(question);
      if (question.type === 'tf') markTf(question);
    });
  }
  const observer = new MutationObserver(refresh);
  observer.observe(feedback, {attributes:true, attributeFilter:['class']});
  refresh();
})();
'''


def once_replace(content, old, new, name):
    if old in content:
        count = content.count(old)
        if count != 1:
            raise ValueError(f'{name}: expected one occurrence of {old!r}, found {count}')
        return content.replace(old, new, 1)
    if new in content:
        return content
    raise ValueError(f'{name}: expected marker not found: {old[:100]!r}')


def write_changes(changes):
    for path, new in changes.items():
        path.write_text(new, encoding='utf-8')
        print(f'  ✓ {path.relative_to(ROOT)}')


def main():
    if not (BASE / 'p2-quiz.js').is_file() or not (BASE / 'index.html').is_file():
        raise SystemExit('Run this script from the repository root (folder with labour-law/).')

    target_paths = {BASE / f'{slug}.html' for slug in ALL} | {
        BASE / 'p2-quiz.js', BASE / 'index.html'
    }
    if not all(p.is_file() for p in target_paths):
        missing = [str(p) for p in target_paths if not p.is_file()]
        raise SystemExit('Missing required files: ' + ', '.join(missing))

    changes = {}
    sfx_html = (
        '  <audio id="sfxCorrect" preload="auto" src="../civil-procedure/correct.mp3"></audio>\n'
        '  <audio id="sfxWrong" preload="auto" src="../civil-procedure/wrong.mp3"></audio>\n'
    )
    helper_tag = '<script src="./quick-feedback.js" defer></script>'

    for slug in ALL:
        path = BASE / f'{slug}.html'
        s = path.read_text(encoding='utf-8')
        if slug in OLD:
            s = s.replace('Law Mock Tests', 'Legis Lectiones')
            s = s.replace('Labour Law', 'Direito do Trabalho')
            s = s.replace(
                'Resposta travada após conferir — erro é erro e conta no resultado final.',
                'O feedback aparece ao responder; os erros também entram no resultado final.'
            )
            s = s.replace(
                'Resposta travada após conferir — erro conta no resultado final.',
                'O feedback aparece ao responder; os erros também entram no resultado final.'
            )
            s = s.replace(
                '<span class="lock-badge" id="lockBadge">Resposta travada</span>',
                '<span class="lock-badge" id="lockBadge" aria-hidden="true"></span>'
            )
            s = s.replace('Conferir e bloquear', 'Conferir resposta')
            s = s.replace('Resposta bloqueada', 'Resposta registrada')
            # Old pages had GitHub raw URLs pointing to the renamed repository.
            s = s.replace('https://raw.githubusercontent.com/mmillenaa/law-mock-tests/main/civil-procedure/correct.mp3', '../civil-procedure/correct.mp3')
            s = s.replace('https://raw.githubusercontent.com/mmillenaa/law-mock-tests/main/civil-procedure/wrong.mp3', '../civil-procedure/wrong.mp3')
        else:
            if 'id="sfxCorrect"' not in s:
                s = once_replace(s, '</body>', sfx_html + '</body>', slug)
            elif 'id="sfxWrong"' not in s:
                raise ValueError(f'{slug}: only one of the audio players is present')
            s = s.replace('Conferir e bloquear', 'Conferir resposta')

        if helper_tag not in s:
            s = once_replace(s, '</head>', '  ' + helper_tag + '\n</head>', slug)
        changes[path] = s

    # Sound playback occurs from the engine's actual scoring event.
    path = BASE / 'p2-quiz.js'
    s = path.read_text(encoding='utf-8')
    marker = '  function feedback(item){'
    sound_helper = '''  function playAnswerSound(ok){
    const audio = document.getElementById(ok ? 'sfxCorrect' : 'sfxWrong');
    if (!audio) return;
    try { audio.currentTime = 0; audio.play().catch(() => {}); }
    catch (error) { console.warn('Audio unavailable:', error); }
  }
'''
    if 'function playAnswerSound(ok)' not in s:
        s = once_replace(s, marker, sound_helper + marker, 'p2-quiz.js: sound helper')
    s = once_replace(
        s,
        'status[item.id]=evaluate(item);selected=null;save();render();',
        'status[item.id]=evaluate(item);playAnswerSound(status[item.id]);selected=null;save();render();',
        'p2-quiz.js: evaluation and sound'
    )
    s = once_replace(
        s,
        "const box=el('div','drop-zone');box.append(el('div','zone-title',zone.label));",
        "const box=el('div','drop-zone');box.dataset.zone=zone.id;box.append(el('div','zone-title',zone.label));",
        'p2-quiz.js: zone IDs'
    )
    s = once_replace(
        s,
        "btn.type='button';btn.draggable=!locked(item);btn.disabled=locked(item);",
        "btn.type='button';btn.dataset.cardIndex=String(i);btn.draggable=!locked(item);btn.disabled=locked(item);",
        'p2-quiz.js: card indices'
    )
    changes[path] = s

    # Module index, not the Aviso Prévio quiz itself, owns this number.
    path = BASE / 'index.html'
    s = path.read_text(encoding='utf-8')
    s = s.replace('<html lang="en">', '<html lang="pt-BR">', 1)
    pattern = r'(<a\s+class="module module--notice"\s+href="\./aviso-previo\.html"[\s\S]*?<div class="num">\s*)Module 05'
    updated, n = re.subn(pattern, r'\g<1>Module 08', s, count=1)
    if n == 0:
        if not re.search(pattern.replace('Module 05', 'Module 08'), s):
            # The current template can place href before class; require explicit confirmation.
            raise ValueError('index.html: could not identify Module 05 inside Aviso Prévio card')
    changes[path] = updated

    helper = BASE / 'quick-feedback.js'
    if helper.exists():
        present = helper.read_text(encoding='utf-8')
        if present != QUICK_FEEDBACK:
            raise ValueError('quick-feedback.js exists with different content; refusing to overwrite')
    else:
        changes[helper] = QUICK_FEEDBACK

    # Validate entire patch before touching any file.
    for slug in ALL:
        s = changes[BASE / f'{slug}.html']
        assert s.count(helper_tag) == 1, f'{slug}: quick feedback import missing/duplicated'
        assert s.count('static.cloudflareinsights.com/beacon.min.js') <= 1, f'{slug}: Cloudflare duplicated'
        if slug in NEW:
            assert s.count('id="sfxCorrect"') == 1 and s.count('id="sfxWrong"') == 1
        if slug in OLD:
            assert 'Law Mock Tests' not in s and 'Labour Law' not in s
        assert s.count('</head>') == 1 and s.count('</body>') == 1
    assert 'Module 08' in changes[BASE / 'index.html']

    actual = {path: content for path, content in changes.items()
              if not path.exists() or path.read_text(encoding='utf-8') != content}
    if not actual:
        print('✓ Everything is already installed; no changes needed.')
        return
    print(f'Applying validated changes to {len(actual)} files:')
    write_changes(actual)
    print('\nQuestion JSON files, engagement API, D1 and Cloudflare configuration were untouched.')
    subprocess.run(['git', 'diff', '--check'], check=True)
    print('\nReview: git diff --stat && git status --short')
    print('Publish after review:')
    print('  git add labour-law/*.html labour-law/p2-quiz.js labour-law/quick-feedback.js')
    print('  git commit -m "Polish labour-law feedback, audio, cards and branding"')
    print('  git push origin main')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, AssertionError) as error:
        print('SAFE STOP: ' + str(error), file=sys.stderr)
        sys.exit(1)
