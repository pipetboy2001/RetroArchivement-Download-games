(function(){
  const state = { q: '', console: '', page: 1, page_size: 50, typingTimer: null };

  function esc(str) { return (str || '').replace(/[&<>"]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s])); }
  function buildQuery(){
    const p = new URLSearchParams();
    if (state.q) p.set('q', state.q);
    if (state.console) p.set('console', state.console);
    p.set('page', state.page);
    p.set('page_size', state.page_size);
    return p.toString();
  }

  async function fetchGames(){
    const res = await fetch(`/api/games?${buildQuery()}`);
    const data = await res.json();
    renderList(data);
  }

  function renderList(data){
    const list = document.getElementById('list');
    const pag = document.getElementById('pagination');
    const summary = document.getElementById('summary');
    list.innerHTML = '';
    pag.innerHTML = '';

    summary.textContent = `${data.total} juegos encontrados` + (state.console ? ` en ${state.console}` : '') + (state.q ? ` para "${state.q}"` : '');

    if (!data.items || data.items.length === 0){
      list.innerHTML = '<div class="py-6 text-center text-gray-500">Sin resultados</div>';
      return;
    }

    for (const g of data.items){
      const consoles = (g.consoles || []).join(', ');
      const name = esc(g.name);
      const versions = g.versions || 0;
      const row = document.createElement('div');
      row.className = 'py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-2';
      row.innerHTML = `
        <div>
          <div class="font-medium text-gray-800">${name}</div>
          <div class="text-xs text-gray-500">Consolas: ${esc(consoles)} • Versiones: ${versions}</div>
        </div>
        <div class="text-right">
          <button type="button" class="px-3 py-1 border rounded hover:bg-gray-100 text-gray-700" data-action="placeholder" data-game-id="${esc((g.id || '').toString())}">Acción</button>
        </div>`;
      list.appendChild(row);
    }

    const { page, total_pages } = data;
    const btn = (p, label, disabled=false) => `<button ${disabled?'disabled':''} class="px-3 py-1 border rounded ${disabled?'opacity-50 cursor-not-allowed':'hover:bg-gray-100'}" data-page="${p}">${label}</button>`;
    pag.innerHTML = `
      ${btn(1, '« Primero', page<=1)}
      ${btn(page-1, '‹ Anterior', page<=1)}
      <span class="px-2">Página ${page} de ${total_pages || 1}</span>
      ${btn(page+1, 'Siguiente ›', page>=total_pages)}
      ${btn(total_pages, 'Último »', page>=total_pages)}
    `;
    pag.querySelectorAll('button[data-page]').forEach(b => b.addEventListener('click', () => { state.page = parseInt(b.dataset.page); fetchGames(); }));
  }

  function toggleScrollBtn(){
    const btn = document.getElementById('scrollTopBtn');
    if (!btn) return;
    if (window.scrollY > 300) btn.classList.remove('hidden'); else btn.classList.add('hidden');
  }

  function init(){
    const q = document.getElementById('q');
    const c = document.getElementById('console');
    const ps = document.getElementById('page_size');
    if (q) q.addEventListener('input', () => {
      clearTimeout(state.typingTimer);
      state.typingTimer = setTimeout(() => { state.q = q.value.trim(); state.page = 1; fetchGames(); }, 300);
    });
    if (c) c.addEventListener('change', () => { state.console = c.value; state.page = 1; fetchGames(); });
    if (ps) ps.addEventListener('change', () => { state.page_size = parseInt(ps.value); state.page = 1; fetchGames(); });

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action="placeholder"]');
      if (btn){
        e.preventDefault();
        alert('Funcionalidad próximamente');
      }
    });

    window.addEventListener('scroll', toggleScrollBtn, { passive: true });
    const topBtn = document.getElementById('scrollTopBtn');
    if (topBtn) topBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    fetchGames();
    toggleScrollBtn();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
