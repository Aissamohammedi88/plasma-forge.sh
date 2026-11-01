// PLASMA FORGE — Frontend JS nouvelle génération
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

let currentTheme = null;
let history = [];
let regenTimer = null;
let countdown = 10;

// Custom cursor
const cursor = $('#cursor');
const trail = $('#cursor-trail');
let mouseX = 0, mouseY = 0;
let trailX = 0, trailY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  cursor.style.left = mouseX + 'px';
  cursor.style.top = mouseY + 'px';
});

// Trail lerp
function animateTrail() {
  trailX += (mouseX - trailX) * 0.15;
  trailY += (mouseY - trailY) * 0.15;
  trail.style.left = trailX + 'px';
  trail.style.top = trailY + 'px';
  requestAnimationFrame(animateTrail);
}
animateTrail();

document.addEventListener('mousedown', () => {
  cursor.style.transform = 'translate(-50%, -50%) scale(0.7)';
});
document.addEventListener('mouseup', () => {
  cursor.style.transform = 'translate(-50%, -50%) scale(1)';
});

// Hover sur éléments interactifs
$$('a, button, .swatch, .history-card').forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(1.8)';
    cursor.style.background = 'var(--accent)';
  });
  el.addEventListener('mouseleave', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(1)';
    cursor.style.background = 'color-mix(in srgb, var(--accent) 50%, transparent)';
  });
});

// Fetch theme
async function fetchTheme() {
  try {
    const r = await fetch('/api/theme?seed=' + Date.now());
    if (!r.ok) throw new Error('theme fetch failed');
    return await r.json();
  } catch (e) {
    console.error('Theme fetch:', e);
    return null;
  }
}

// Fetch SVG
async function fetchSvg(seed, points, palette) {
  try {
    const params = new URLSearchParams({
      seed,
      points,
      palette: palette.join(','),
    });
    const r = await fetch('/api/svg?' + params.toString());
    if (!r.ok) throw new Error('svg fetch failed');
    return await r.text();
  } catch (e) {
    console.error('SVG fetch:', e);
    return '';
  }
}

// Apply theme
function applyTheme(theme) {
  const root = document.documentElement;
  const c = theme.colors;
  root.style.setProperty('--bg', c.bg);
  root.style.setProperty('--surface', c.surface);
  root.style.setProperty('--primary', c.primary);
  root.style.setProperty('--accent', c.accent);
  root.style.setProperty('--accent2', c.accent2);
  root.style.setProperty('--text', c.text);
  root.style.setProperty('--muted', c.muted);

  const p = theme.params;
  root.style.setProperty('--anim-dur', p.anim_duration + 's');
  root.style.setProperty('--font-scale', p.font_scale);
  root.style.setProperty('--letter-spacing', p.letter_spacing + 'em');
  root.style.setProperty('--radius', p.border_radius + 'px');
}

// Render
function renderPalette(theme) {
  const grid = $('#palette-grid');
  grid.innerHTML = '';
  theme.colors.palette.forEach((color) => {
    const sw = document.createElement('div');
    sw.className = 'swatch';
    sw.style.background = color;
    sw.innerHTML = `<div class="swatch-code">${color}</div>`;
    sw.onclick = () => {
      navigator.clipboard.writeText(color);
      const code = sw.querySelector('.swatch-code');
      const orig = code.textContent;
      code.textContent = 'Copié!';
      setTimeout(() => code.textContent = orig, 1000);
    };
    grid.appendChild(sw);
  });

  const info = $('#color-info');
  const entries = [
    ['bg', theme.colors.bg],
    ['surface', theme.colors.surface],
    ['primary', theme.colors.primary],
    ['accent', theme.colors.accent],
    ['accent2', theme.colors.accent2],
    ['text', theme.colors.text],
  ];
  info.innerHTML = entries.map(([k, v]) =>
    `<div style="--swatch-color:${v}"><strong>${k}</strong>: ${v}</div>`
  ).join('');

  $('#css-vars').textContent = `:root {
  --bg: ${theme.colors.bg};
  --surface: ${theme.colors.surface};
  --primary: ${theme.colors.primary};
  --accent: ${theme.colors.accent};
  --accent2: ${theme.colors.accent2};
  --text: ${theme.colors.text};
  --muted: ${theme.colors.muted};
  --radius: ${theme.params.border_radius}px;
  --anim-dur: ${theme.params.anim_duration}s;
  --font-scale: ${theme.params.font_scale};
  --letter-spacing: ${theme.params.letter_spacing}em;
}`;

  $('#json-theme').textContent = JSON.stringify(theme, null, 2);
  $('#meta-seed').textContent = theme.seed.slice(-8);
  $('#meta-scheme').textContent = theme.scheme;
  $('#meta-engine').textContent = theme.engine || 'rust';
}

function applySvg(svgText) {
  $('#bg-container').innerHTML = svgText;
}

function addToHistory(theme) {
  history.unshift({ ...theme });
  if (history.length > 8) history.pop();
  renderHistory();
}

function renderHistory() {
  const grid = $('#history-grid');
  grid.innerHTML = '';
  history.forEach((t) => {
    const card = document.createElement('div');
    card.className = 'history-card';
    const mini = document.createElement('div');
    mini.className = 'mini-palette';
    t.colors.palette.forEach((c) => {
      const d = document.createElement('div');
      d.style.background = c;
      mini.appendChild(d);
    });
    card.appendChild(mini);
    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = `${t.scheme} · ${t.seed.slice(-6)}`;
    card.appendChild(label);
    card.onclick = () => {
      applyTheme(t);
      renderPalette(t);
      currentTheme = t;
    };
    grid.appendChild(card);
  });
}

async function regenerate() {
  const theme = await fetchTheme();
  if (!theme) return;
  const svg = await fetchSvg(
    theme.seed,
    theme.svg.voronoi_points,
    theme.colors.palette
  );
  applyTheme(theme);
  renderPalette(theme);
  if (svg) applySvg(svg);
  addToHistory(theme);
  currentTheme = theme;
}

$('#regenerate').addEventListener('click', () => {
  regenerate();
  resetTimer();
});

$('#btn-save').addEventListener('click', async () => {
  if (!currentTheme) return;
  try {
    const r = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currentTheme),
    });
    const data = await r.json();
    alert('Thème sauvegardé : ' + (data.saved || data.error));
  } catch (e) {
    alert('Erreur sauvegarde : ' + e.message);
  }
});

function resetTimer() {
  clearInterval(regenTimer);
  countdown = 10;
  $('#meta-timer').textContent = countdown + 's';
  regenTimer = setInterval(() => {
    countdown--;
    $('#meta-timer').textContent = countdown + 's';
    if (countdown <= 0) {
      regenerate();
      clearInterval(regenTimer);
      resetTimer();
    }
  }, 1000);
}

// Keyboard
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'r' || e.key === 'R') {
    regenerate();
    resetTimer();
  }
  if (e.key === 's' || e.key === 'S') {
    e.preventDefault();
    $('#btn-save').click();
  }
});

// IntersectionObserver pour animations au scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

$$('section').forEach((s) => {
  s.style.opacity = '0';
  s.style.transform = 'translateY(40px)';
  s.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
  observer.observe(s);
});

// Init
regenerate().then(() => {
  resetTimer();
});
