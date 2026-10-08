/* Legis Lectiones — engine compartilhado dos quatro bancos P2. */
(() => {
  'use strict';
  const slug = document.body.dataset.bank;
  if (!/^[a-z0-9-]+$/.test(slug || '')) return;
  const STORAGE = `legis-lectiones:labour:${slug}:v1`;
  const $ = id => document.getElementById(id);
  const norm = value => String(value ?? '').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').trim().toLowerCase().replace(/\s+/g,' ');

  let bank = [], order = [], pos = 0, answers = {}, status = {};
  let selected = null;
  const types = {mcq:'Múltipla escolha',fill:'Completar lacunas',tf:'Verdadeiro / Falso',drag:'Arrastar cartões'};
  const current = () => bank[order[pos]];
  const locked = item => Object.hasOwn(status,item.id);

  function save(){
    localStorage.setItem(STORAGE,JSON.stringify({order,pos,answers,status}));
  }
  function restore(){
    try{
      const s = JSON.parse(localStorage.getItem(STORAGE));
      if (!s || !Array.isArray(s.order) || !s.order.length ||
        !s.order.every(i => Number.isInteger(i) && i >= 0 && i < bank.length) ||
        !Number.isInteger(s.pos) || s.pos < 0 || s.pos >= s.order.length ||
        typeof s.status !== 'object' || !s.status || typeof s.answers !== 'object' || !s.answers) return false;
      order=s.order;pos=s.pos;answers=s.answers;status=s.status;
      return true;
    } catch(e){return false;}
  }
  function progress(){
    const done=bank.filter(q=>locked(q)).length;
    $('counter').textContent = `Atividade ${pos+1} de ${order.length}`;
    $('progressText').textContent = `${Math.round(100*done/bank.length)}% do banco concluído`;
    $('progressBar').style.width=`${100*done/bank.length}%`;
    $('prevBtn').disabled=pos===0;
    $('nextBtn').disabled=pos===order.length-1;
  }
  function el(tag, className, text){
    const e=document.createElement(tag);
    if(className) e.className=className;
    if(text!==undefined) e.textContent=text;
    return e;
  }
  function renderMcq(item,host){
    const selectedAnswer=answers[item.id];
    const list=el('div','options');
    item.options.forEach((text,i)=>{
      const row=el('label','option'+(selectedAnswer===i?' selected':'')+(locked(item)?' locked':''));
      const radio=document.createElement('input');
      radio.type='radio';radio.name=`answer-${item.id}`;radio.value=String(i);
      radio.checked=selectedAnswer===i;radio.disabled=locked(item);
      radio.addEventListener('change',()=>{answers[item.id]=i;save();render();});
      row.append(radio,el('span','',text));list.appendChild(row);
    });
    host.appendChild(list);
  }
  function renderFill(item,host){
    const line=el('div','fill-line');
    const parts=item.prompt.split('{{blank}}');
    const filled=Array.isArray(answers[item.id])?answers[item.id]:[];
    parts.forEach((text,i)=>{
      line.append(document.createTextNode(text));
      if(i<parts.length-1){
        const inp=el('input','fill-input');inp.type='text';inp.value=filled[i]||'';
        inp.disabled=locked(item);inp.autocomplete='off';
        inp.setAttribute('aria-label',`Lacuna ${i+1}`);
        inp.addEventListener('input',()=>{
          const a=Array.isArray(answers[item.id])?[...answers[item.id]]:new Array(item.answers.length).fill('');
          a[i]=inp.value;answers[item.id]=a;save();
          $('checkBtn').disabled=!hasAnswer(item);
        });
        line.append(inp);
      }
    });
    $('prompt').textContent='Complete as lacunas:';
    host.append(line);
  }
  function renderTf(item,host){
    const list=el('div','tf-list');
    const selectedAnswers=Array.isArray(answers[item.id])?answers[item.id]:[];
    item.statements.forEach((s,i)=>{
      const row=el('div','tf-row');row.append(el('span','',s.text));
      const buttons=el('div','tf-actions');
      [['V',true],['F',false]].forEach(([label,v])=>{
        const btn=el('button','tf-btn'+(selectedAnswers[i]===v?' on':''),label);
        btn.type='button';btn.disabled=locked(item);
        btn.setAttribute('aria-pressed',String(selectedAnswers[i]===v));
        btn.addEventListener('click',()=>{
          const a=Array.isArray(answers[item.id])?[...answers[item.id]]:new Array(item.statements.length).fill(null);
          a[i]=v;answers[item.id]=a;save();render();
        });
        buttons.append(btn);
      });
      row.append(buttons);list.append(row);
    });host.append(list);
  }
  function renderDrag(item,host){
    const note=el('p','drag-note','Arraste os cartões ou toque em um cartão e depois no destino.');
    const layout=el('div','drag-layout');
    const pool=el('div','drag-pool');pool.append(el('div','zone-title','Cartões'));
    const zonesWrap=el('div','zones');
    const zoneEls=new Map();
    const placements=Array.isArray(answers[item.id])?answers[item.id]:new Array(item.cards.length).fill('');
    function move(i,zone){
      if(locked(item))return;
      const a=Array.isArray(answers[item.id])?[...answers[item.id]]:new Array(item.cards.length).fill('');
      a[i]=zone;answers[item.id]=a;selected=null;save();render();
    }
    function wire(place,zone){
      place.addEventListener('dragover',e=>{if(!locked(item))e.preventDefault();});
      place.addEventListener('drop',e=>{
        if(locked(item))return;
        e.preventDefault();const index=Number(e.dataTransfer.getData('text/plain'));
        if(Number.isInteger(index)&&index>=0&&index<item.cards.length) move(index,zone);
      });
      place.addEventListener('click',e=>{
        if(e.target.closest('.drag-card'))return;
        if(selected!==null)move(selected,zone);
      });
    }
    wire(pool,'');
    item.zones.forEach(zone=>{
      const box=el('div','drop-zone');box.dataset.zone=zone.id;box.append(el('div','zone-title',zone.label));
      wire(box,zone.id);zoneEls.set(zone.id,box);zonesWrap.append(box);
    });
    item.cards.forEach((card,i)=>{
      const btn=el('button','drag-card'+(selected===i?' is-selected':''),card.text);
      btn.type='button';btn.dataset.cardIndex=String(i);btn.draggable=!locked(item);btn.disabled=locked(item);
      btn.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/plain',String(i));});
      btn.addEventListener('click',()=>{if(!locked(item)){selected=i;render();}});
      (zoneEls.get(placements[i])||pool).append(btn);
    });
    layout.append(pool,zonesWrap);host.append(note,layout);
  }
  function hasAnswer(item){
    const a=answers[item.id];
    if(item.type==='mcq')return Number.isInteger(a) && a>=0 && a<item.options.length;
    if(item.type==='fill')return Array.isArray(a)&&a.length===item.answers.length&&a.every(x=>String(x||'').trim());
    if(item.type==='tf')return Array.isArray(a)&&a.length===item.statements.length&&a.every(x=>typeof x==='boolean');
    if(item.type==='drag')return Array.isArray(a)&&a.length===item.cards.length&&a.every(z=>item.zones.some(v=>v.id===z));
    return false;
  }
  function evaluate(item){
    const a=answers[item.id];
    if(item.type==='mcq')return a===item.answer;
    if(item.type==='fill')return item.answers.every((accepted,i)=>accepted.some(v=>norm(v)===norm(a[i])));
    if(item.type==='tf')return item.statements.every((s,i)=>a[i]===s.answer);
    if(item.type==='drag')return item.cards.every((card,i)=>a[i]===card.zone);
    return false;
  }
  function playAnswerSound(ok){
    const audio = document.getElementById(ok ? 'sfxCorrect' : 'sfxWrong');
    if (!audio) return;
    try { audio.currentTime = 0; audio.play().catch(() => {}); }
    catch (error) { console.warn('Audio unavailable:', error); }
  }
  function feedback(item){
    const ok=status[item.id],box=$('feedback');
    box.className='feedback show '+(ok?'correct':'wrong');
    box.replaceChildren(el('strong','',ok?'Correto.':'Ainda não.'));
    if(!ok){
      let answer='';
      if(item.type==='mcq')answer=item.options[item.answer];
      if(item.type==='fill')answer=item.answers.map(x=>x[0]).join(' · ');
      if(item.type==='tf')answer=item.statements.map((s,i)=>`${i+1}. ${s.answer?'V':'F'}`).join(' · ');
      if(item.type==='drag')answer='Revise a classificação na explicação.';
      box.append(el('div','feedback-answer','Resposta: '+answer));
    }
    box.append(el('div','feedback-explanation',item.explanation));
  }
  function render(){
    const item=current();if(!item)return;
    const card=$('quizCard');
    // Só muda o atributo observado quando a questão realmente muda.
    // O engagement.js já possui MutationObserver: não emitimos um segundo evento.
    if(card.dataset.questionId!==item.id) card.dataset.questionId=item.id;
    card.dataset.questionType=item.type;
    card.dataset.questionSection=item.section;
    card.dataset.questionPrompt=item.prompt;
    $('sectionLabel').textContent=item.section;
    $('typeLabel').textContent=types[item.type]||item.type;
    $('prompt').textContent=item.prompt;
    const host=$('interactive');host.replaceChildren();
    $('feedback').className='feedback';$('feedback').replaceChildren();
    $('answerState').textContent=locked(item)?(status[item.id]?'Acerto registrado':'Erro registrado'):'';
    $('answerState').className='answer-state'+(locked(item)?(status[item.id]?' is-correct':' is-wrong'):'');
    if(item.type==='mcq')renderMcq(item,host);
    if(item.type==='fill')renderFill(item,host);
    if(item.type==='tf')renderTf(item,host);
    if(item.type==='drag')renderDrag(item,host);
    $('checkBtn').disabled=locked(item)||!hasAnswer(item);
    $('checkBtn').textContent=locked(item)?'Resposta bloqueada':'Conferir e bloquear';
    if(locked(item))feedback(item);
    progress();save();
  }
  function result(){
    const done=bank.filter(q=>locked(q));
    const right=done.filter(q=>status[q.id]===true).length;
    const wrong=done.length-right;
    $('score').textContent=`${Math.round(100*right/bank.length)}%`;
    $('scoreDetail').textContent=`${right} acertos · ${wrong} erros · ${bank.length-done.length} não respondidas · ${bank.length} atividades`;
    document.querySelectorAll('.quiz-ui').forEach(e=>e.classList.add('quiz-hidden'));
    $('result').classList.add('show');
    window.dispatchEvent(new CustomEvent('law-bank-result',{detail:{answered:done.length,total:bank.length,complete:done.length===bank.length}}));
  }
  function hideResult(){
    $('result').classList.remove('show');
    document.querySelectorAll('.quiz-ui').forEach(e=>e.classList.remove('quiz-hidden'));
  }
  function shuffle(a){
    const copy=[...a];for(let i=copy.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[copy[i],copy[j]]=[copy[j],copy[i]];}return copy;
  }
  function validate(data){
    if(!Array.isArray(data?.questions)||!data.questions.length)throw Error('Nenhuma questão no JSON.');
    const seen=new Set();
    data.questions.forEach(q=>{
      if(!q.id||seen.has(q.id)||!q.prompt||!q.explanation||!q.section)throw Error('Registro duplicado ou incompleto: '+q.id);
      seen.add(q.id);
      if(q.type==='mcq'&&(!Array.isArray(q.options)||!Number.isInteger(q.answer)||q.answer<0||q.answer>=q.options.length))throw Error('Gabarito inválido: '+q.id);
      if(q.type==='fill'&&(!Array.isArray(q.answers)||q.answers.length!==q.prompt.split('{{blank}}').length-1))throw Error('Lacunas inválidas: '+q.id);
      if(q.type==='tf'&&(!Array.isArray(q.statements)||q.statements.some(s=>typeof s.answer!=='boolean')))throw Error('V/F inválido: '+q.id);
      if(q.type==='drag'&&(!Array.isArray(q.cards)||!Array.isArray(q.zones)||q.cards.some(c=>!q.zones.some(z=>z.id===c.zone))))throw Error('Cartões inválidos: '+q.id);
      if(!['mcq','fill','tf','drag'].includes(q.type))throw Error('Tipo inválido: '+q.id);
    });
  }
  async function init(){
    const response=await fetch(new URL('./'+slug+'.json',location.href),{cache:'no-store'});
    if(!response.ok)throw Error('HTTP '+response.status+' ao carregar banco.');
    const data=await response.json();validate(data);bank=data.questions;
    const counts=bank.reduce((x,q)=>(x[q.type]=(x[q.type]||0)+1,x),{mcq:0,fill:0,tf:0,drag:0});
    $('stats').replaceChildren(...[
      `${bank.length} atividades`,`${counts.mcq} múltipla escolha`,`${counts.fill} lacunas`,`${counts.tf} V/F`,`${counts.drag} arrastar`
    ].map(t=>el('span','stat',t)));
    if(!restore()){order=bank.map((_,i)=>i);pos=0;answers={};status={};}
    $('checkBtn').addEventListener('click',()=>{
      const item=current();if(locked(item))return;
      if(!hasAnswer(item)){alert('Responda todos os campos antes de conferir.');return;}
      status[item.id]=evaluate(item);playAnswerSound(status[item.id]);selected=null;save();render();
    });
    $('prevBtn').addEventListener('click',()=>{if(pos>0){pos--;selected=null;render();}});
    $('nextBtn').addEventListener('click',()=>{if(pos<order.length-1){pos++;selected=null;render();}});
    $('shuffleBtn').addEventListener('click',()=>{order=shuffle(order);pos=0;selected=null;render();});
    $('finishBtn').addEventListener('click',result);
    $('restartBtn').addEventListener('click',()=>{
      if(!confirm('Recomeçar? As respostas desta tentativa serão apagadas.'))return;
      localStorage.removeItem(STORAGE);order=bank.map((_,i)=>i);pos=0;answers={};status={};
      selected=null;hideResult();render();
    });
    $('reviewWrongBtn').addEventListener('click',()=>{
      const failed=bank.map((q,i)=>status[q.id]===false?i:null).filter(i=>i!==null);
      if(!failed.length){alert('Nenhum erro registrado.');return;}
      order=failed;pos=0;selected=null;hideResult();render();
    });
    render();
  }
  init().catch(error=>{
    console.error('Falha ao carregar banco P2:',error);
    const card=$('quizCard');
    if(card)card.replaceChildren(el('h2','','Não foi possível iniciar o banco.'),el('p','',error.message));
  });
})();
