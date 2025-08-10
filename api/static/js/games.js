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

  async function fetchVersions(gameId){
    const form = new FormData();
    form.append('game_id', gameId);
    const res = await fetch('/get_game_versions', { method: 'POST', body: form });
    return await res.json();
  }

  function openModal(id){
    const el = document.getElementById(id);
    if (el){ el.classList.remove('hidden'); el.classList.add('flex'); document.body.classList.add('overflow-hidden'); }
  }
  function closeModal(id){
    const el = document.getElementById(id);
    if (el){ el.classList.add('hidden'); el.classList.remove('flex'); document.body.classList.remove('overflow-hidden'); }
  }

  // Exponer helpers a nivel global para soportar los onclick de los botones (X / Cancelar)
  // Esto asegura que closeModal('versionsModal') y similares funcionen en /games
  window.openModal = openModal;
  window.closeModal = closeModal;

  // Paginación de versiones (cliente)
  const versionsState = { all: [], page: 1, pageSize: 10 };

  function renderVersions(list){
    versionsState.all = list || [];
    versionsState.page = 1;
    renderVersionsPage();
  }

  function renderVersionsPage(){
    const container = document.getElementById('versionsContainer');
    const pag = document.getElementById('versionsPagination');
    if (!container) return;
    const list = versionsState.all;
    if (!list || list.length === 0){
      container.innerHTML = '<div class="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg text-center">No hay versiones disponibles.</div>';
      if (pag) pag.innerHTML = '';
      return;
    }
    const total = list.length;
    const totalPages = Math.max(1, Math.ceil(total / versionsState.pageSize));
    const page = Math.min(versionsState.page, totalPages);
    const start = (page - 1) * versionsState.pageSize;
    const current = list.slice(start, start + versionsState.pageSize);

    container.innerHTML = current.map((v, localIdx) => {
      const idx = start + localIdx;
      const isRecommended = idx === 0;
      const recommendedBadge = isRecommended ? '<span class="badge-success text-xs">✅ Recomendada</span>' : '';
      const region = v.info && v.info.region && v.info.region !== 'Unknown' ? `<span class="badge-success text-xs">${v.info.region}</span>` : '';
      const hack = v.info && v.info.is_hack ? '<span class="badge-warning text-xs">HACK</span>' : '';
      const trans = v.info && v.info.is_translation ? '<span class="badge-warning text-xs">TRADUCCIÓN</span>' : '';
      const fname = v.info && v.info.filename ? v.info.filename : v.rom_path;
      return `
        <div class="version-option border ${isRecommended?'border-green-500 bg-green-50':'border-gray-200'} rounded-lg p-3 hover:shadow-md transition-all duration-300 cursor-pointer" data-hash="${v.hash}">
          <div class="flex justify-between items-start mb-1">
            <h4 class="font-medium text-gray-800 text-sm">${fname}</h4>
            ${recommendedBadge}
          </div>
          <div class="flex flex-wrap gap-1 mb-1">${region}${hack}${trans}</div>
          <p class="text-xs text-gray-600">Hash: ${v.hash}</p>
        </div>`;
    }).join('');

    if (pag){
      const btn = (p, label, disabled=false) => `<button ${disabled?'disabled':''} class="px-3 py-1 border rounded ${disabled?'opacity-50 cursor-not-allowed':'hover:bg-gray-100'}" data-vpage="${p}">${label}</button>`;
      pag.innerHTML = `
        ${btn(1, '« Primero', page<=1)}
        ${btn(page-1, '‹ Anterior', page<=1)}
        <span class="px-2 text-sm">Página ${page} de ${totalPages}</span>
        ${btn(page+1, 'Siguiente ›', page>=totalPages)}
        ${btn(totalPages, 'Último »', page>=totalPages)}
      `;
      pag.querySelectorAll('button[data-vpage]').forEach(b => b.addEventListener('click', () => { versionsState.page = parseInt(b.dataset.vpage); renderVersionsPage(); }));
    }
  }

  async function openVersionsFor(gameId, gameName){
    const label = document.getElementById('versionsModalLabel');
    const container = document.getElementById('versionsContainer');
    if (label) label.innerHTML = `<span class="text-3xl">🎮</span> Versiones de: ${gameName || ''}`;
    if (container) container.innerHTML = `
      <div class="text-center py-8">
        <div class="spinner mx-auto mb-4"></div>
        <p class="text-gray-600">Cargando versiones...</p>
      </div>`;
    openModal('versionsModal');
    try{
      const res = await fetchVersions(gameId);
      if (res.success){ renderVersions(res.versions); }
      else { container.innerHTML = '<div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg text-center">No se pudieron cargar las versiones</div>'; }
    }catch(e){
      container.innerHTML = '<div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg text-center">Error al cargar las versiones</div>';
    }
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
  // Asegurar clase overlay en modales para poder detectar clic fuera
  ['versionsModal','instructionsModal'].forEach(id => { const el = document.getElementById(id); if (el) el.classList.add('modal-overlay'); });
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
        const gameId = btn.dataset.gameId;
        const nameEl = btn.closest('div').previousElementSibling?.querySelector('.font-medium');
        const gameName = nameEl ? nameEl.textContent.trim() : '';
        openVersionsFor(gameId, gameName);
      }
      const versionEl = e.target.closest('.version-option');
      if (versionEl){
        const hash = versionEl.dataset.hash;
        // Usar redirect interno para evitar pop-ups y CORS
        window.location.href = `/dl?hash=${encodeURIComponent(hash)}`;
      }
      // Cerrar al hacer clic fuera (overlay)
      if (e.target && e.target.classList && e.target.classList.contains('modal-overlay')){
        closeAllModals();
      }
    });

    // Cerrar con tecla ESC
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAllModals(); });

    window.addEventListener('scroll', toggleScrollBtn, { passive: true });
    const topBtn = document.getElementById('scrollTopBtn');
    if (topBtn) topBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    fetchGames();
    toggleScrollBtn();
  }

  function closeAllModals(){ ['versionsModal','instructionsModal'].forEach(closeModal); }

  document.addEventListener('DOMContentLoaded', init);
})();
