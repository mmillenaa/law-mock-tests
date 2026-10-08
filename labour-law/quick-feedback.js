/* Legis Lectiones · Quick feedback and per-card corrections.
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
