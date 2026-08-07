const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

navToggle.addEventListener('click', () => {
  navToggle.classList.toggle('open');
  navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navToggle.classList.remove('open');
    navLinks.classList.remove('open');
  });
});

const revealEls = document.querySelectorAll('.card, .fact, .term, .objective, .callout, .phase, .lesson-text, .reflection, .table-wrap');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.08 }
);

revealEls.forEach((el) => el.classList.add('reveal'));
revealEls.forEach((el) => observer.observe(el));

const QUESTIONS = [
  {
    q: '¿A qué edad se ejerce el derecho al voto en Colombia?',
    options: ['16 años', '18 años', '21 años'],
    answer: 1,
    feedback: 'Correcto. En Colombia se vota desde los 18 años. La excepción: en los Consejos de Juventud pueden votar jóvenes de 14 a 28 años.'
  },
  {
    q: '¿Qué documento necesitas para votar?',
    options: ['La licencia de conducción', 'El carné estudiantil', 'La cédula de ciudadanía original (física o digital)'],
    answer: 2,
    feedback: 'Exacto. Solo sirve la cédula de ciudadanía original: física (amarilla con hologramas) o digital. No valen contraseñas, carnés ni libreta militar.'
  },
  {
    q: '¿Cómo se hace la inscripción de la cédula para cambiar de puesto de votación?',
    options: [
      'Por internet, desde la página de la Registraduría',
      'De forma presencial en la Registraduría, con huella dactilar',
      'Por teléfono, llamando al 018000'
    ],
    answer: 1,
    feedback: 'Correcto. La inscripción es presencial porque requiere tu huella dactilar: no se puede delegar ni hacer en línea.'
  },
  {
    q: '¿En qué horario están abiertas las urnas el día de las elecciones?',
    options: ['De 6:00 a.m. a 12:00 m.', 'De 8:00 a.m. a 4:00 p.m.', 'De 8:00 a.m. a 6:00 p.m.'],
    answer: 1,
    feedback: 'Así es: de 8:00 a.m. a 4:00 p.m. en punto. Después de las 4 ya no se reciben votos.'
  },
  {
    q: '¿Qué pasa si marcas más de una casilla en el tarjetón?',
    options: ['Tu voto se divide entre los candidatos', 'Tu voto se anula', 'Se cuenta como voto en blanco'],
    answer: 1,
    feedback: 'Correcto: marcar más de una casilla anula tu voto. Solo se marca UNA casilla, con X clara dentro del recuadro.'
  },
  {
    q: 'Si el voto en blanco obtiene la mayoría en una elección, ¿qué ocurre?',
    options: ['Gana el candidato que quedó de segundo', 'La elección se repite una vez', 'No tiene ningún efecto'],
    answer: 1,
    feedback: 'Muy bien. El voto en blanco no es simbólico: si gana la mayoría, la elección se repite una vez con nuevos candidatos.'
  },
  {
    q: 'Si en el tarjetón del Congreso aparecen números junto al logo del partido, ¿qué significa?',
    options: [
      'Es una lista cerrada: solo se marca la casilla del partido',
      'Es una lista abierta: puedes marcar el número del candidato que prefieras',
      'Ese tarjetón no es válido'
    ],
    answer: 1,
    feedback: 'Exacto: números junto al logo = lista abierta (marcas el número de tu candidato o el símbolo del partido). Sin números = lista cerrada (solo la casilla del partido).'
  },
  {
    q: '¿Para qué sirve el certificado electoral?',
    options: [
      'Solo como recuerdo del día',
      'Es el documento que te permite votar',
      'Da beneficios: medio día de descanso, descuentos en universidades públicas y pasaporte'
    ],
    answer: 2,
    feedback: 'Correcto. Votando obtienes beneficios legales: medio día de descanso remunerado, descuento en matrícula de universidades públicas y en el pasaporte.'
  },
  {
    q: '¿El voto en Colombia es obligatorio?',
    options: [
      'Sí, y si no votas pagas una multa',
      'No, es un derecho y un deber ciudadano, pero no es obligatorio',
      'Solo para los mayores de 25 años'
    ],
    answer: 1,
    feedback: 'Así es: el voto no es obligatorio en Colombia. La excepción es el jurado de votación: si te designan, asistir a la mesa sí es obligatorio.'
  },
  {
    q: '¿A partir de qué edad pueden votar en las elecciones de Consejos de Juventud?',
    options: ['10 años', '14 años', '18 años'],
    answer: 1,
    feedback: '¡Correcto! En los Consejos de Juventud votan y pueden ser elegidos jóvenes de 14 a 28 años. Es la puerta de entrada a la participación para los menores de 18.'
  }
];

const quizBody = document.getElementById('quizBody');
const quizCounter = document.getElementById('quizCounter');
const quizProgress = document.getElementById('quizProgress');
const quizPrev = document.getElementById('quizPrev');
const quizNext = document.getElementById('quizNext');
const quizRestart = document.getElementById('quizRestart');

let current = 0;
let selected = new Array(QUESTIONS.length).fill(null);

function render() {
  const isResult = current >= QUESTIONS.length;
  quizCounter.textContent = isResult ? 'Resultado final' : `Pregunta ${current + 1} de ${QUESTIONS.length}`;
  quizProgress.style.width = `${(Math.min(current + 1, QUESTIONS.length) / QUESTIONS.length) * 100}%`;

  quizPrev.hidden = current === 0 || isResult;
  quizNext.hidden = isResult;
  quizRestart.hidden = !isResult;

  if (isResult) {
    renderResult();
    return;
  }

  const item = QUESTIONS[current];
  const answered = selected[current];

  quizBody.innerHTML = `
    <h3>${item.q}</h3>
    <div class="quiz-options">
      ${item.options.map((opt, i) => {
        let cls = 'quiz-option';
        if (answered !== null) {
          if (i === item.answer) cls += ' correct';
          else if (i === answered) cls += ' wrong';
          cls += ' disabled';
        }
        return `<button class="${cls}" data-i="${i}">${String.fromCharCode(65 + i)}) ${opt}</button>`;
      }).join('')}
    </div>
    ${answered !== null ? `
      <div class="quiz-feedback ${answered === item.answer ? 'good' : 'bad'}">
        ${answered === item.answer ? '✅ ' + item.feedback : '❌ ' + item.feedback}
      </div>` : ''}
  `;

  quizBody.querySelectorAll('.quiz-option').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (answered !== null) return;
      selected[current] = parseInt(btn.dataset.i, 10);
      render();
    });
  });
}

function renderResult() {
  const correct = selected.filter((s, i) => s === QUESTIONS[i].answer).length;
  const pct = Math.round((correct / QUESTIONS.length) * 100);
  let msg;

  if (pct === 100) msg = '¡Perfecto! Dominas el tema. Prepárate para ser jurado de votación o monitor electoral del curso.';
  else if (pct >= 70) msg = '¡Muy bien! Aprobaste el módulo. Repasa las preguntas que fallaste y quedarás listo.';
  else if (pct >= 40) msg = 'Vas bien, pero vuelve a leer las unidades: el voto es un tema demasiado importante para dejarlo a medias.';
  else msg = 'Te recomendamos repasar el módulo completo y hacer el quiz de nuevo. ¡Tú puedes!';

  quizBody.innerHTML = `
    <div class="quiz-score">
      <h3>Tu puntaje: <span class="score-num">${correct}/${QUESTIONS.length}</span> (${pct}%)</h3>
      <p>${msg}</p>
      <p style="font-size:0.85rem;">Repasa las unidades y vuelve a intentarlo cuantas veces quieras.</p>
    </div>
  `;
}

quizPrev.addEventListener('click', () => {
  if (current > 0) {
    current -= 1;
    render();
  }
});

quizNext.addEventListener('click', () => {
  if (selected[current] === null) {
    quizBody.insertAdjacentHTML('beforeend', '<div class="quiz-feedback bad">Primero selecciona una respuesta antes de continuar.</div>');
    return;
  }
  current += 1;
  render();
});

quizRestart.addEventListener('click', () => {
  current = 0;
  selected = new Array(QUESTIONS.length).fill(null);
  render();
});

render();
