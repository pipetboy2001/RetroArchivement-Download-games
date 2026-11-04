"use client";

import { useEffect, useRef, useState } from "react";
import VersionsModal from "./VersionsModal";
import type { ConsoleCount, Game, GamesResponse } from "./types";

const PAGE_SIZES = [25, 50, 75, 100, 150, 200, 300, 400];

export default function GamesPage() {
  const [q, setQ] = useState("");
  const [consoleFilter, setConsoleFilter] = useState("");
  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(1);

  const [items, setItems] = useState<Game[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [consoles, setConsoles] = useState<ConsoleCount[]>([]);

  const [activeGame, setActiveGame] = useState<{ id: string; name: string } | null>(null);
  const [showScrollTop, setShowScrollTop] = useState(false);

  const typingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (consoleFilter) params.set("console", consoleFilter);
    params.set("page", String(page));
    params.set("page_size", String(pageSize));

    fetch(`/api/games?${params.toString()}`)
      .then((res) => res.json() as Promise<GamesResponse>)
      .then((data) => {
        setItems(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
        setConsoles(data.consoles || []);
      });
  }, [q, consoleFilter, page, pageSize]);

  useEffect(() => {
    const onScroll = () => setShowScrollTop(window.scrollY > 300);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  function onSearchChange(value: string) {
    if (typingTimer.current) clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => {
      setQ(value.trim());
      setPage(1);
    }, 300);
  }

  const summary = `${total} juegos encontrados` + (consoleFilter ? ` en ${consoleFilter}` : "") + (q ? ` para "${q}"` : "");

  return (
    <main className="container mx-auto px-4 py-4 max-w-2xl bg-gray-50 min-h-screen">
      <header className="text-center mb-6">
        <div className="bg-white rounded-xl shadow-md p-4 card-shadow">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-3 flex items-center justify-center gap-2">
            <span className="text-2xl md:text-3xl">📚</span>
            <span className="gradient-bg bg-clip-text text-transparent">Listado de juegos</span>
          </h1>
          <p className="text-gray-600">Explora todos los juegos disponibles. Filtra por consola y busca por nombre.</p>
          <div className="mt-3">
            <a href="/" className="inline-flex items-center gap-1 text-retro-blue hover:underline text-sm">
              ← Volver al inicio
            </a>
          </div>
        </div>
      </header>

      <div className="bg-white rounded-xl shadow-md p-4 card-shadow">
        <div className="flex flex-col md:flex-row gap-3 md:items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
            <input
              type="text"
              placeholder="Nombre del juego..."
              defaultValue={q}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-retro-blue"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Consola</label>
            <select
              value={consoleFilter}
              onChange={(e) => { setConsoleFilter(e.target.value); setPage(1); }}
              className="border rounded-md px-3 py-2"
            >
              <option value="">Todas</option>
              {consoles.map((c) => (
                <option key={c.name} value={c.name}>{c.name} ({c.count})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tamaño página</label>
            <select
              value={pageSize}
              onChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(1); }}
              className="border rounded-md px-3 py-2"
            >
              {PAGE_SIZES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div className="text-sm text-gray-600 mt-3">{summary}</div>

        <div className="divide-y mt-3">
          {items.length === 0 && <div className="py-6 text-center text-gray-500">Sin resultados</div>}
          {items.map((g) => (
            <div key={g.id} className="py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <div className="flex items-center gap-3">
                {g.image_icon ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={g.image_icon} alt="" className="w-10 h-10 rounded object-cover flex-shrink-0" loading="lazy" />
                ) : (
                  <div className="w-10 h-10 rounded bg-gray-100 flex-shrink-0"></div>
                )}
                <div>
                  <div className="font-medium text-gray-800">
                    {g.name}
                    {g.achievements != null && (
                      <span className="ml-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-1.5 py-0.5">
                        🏆 {g.achievements}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">Consolas: {g.consoles.join(", ")} • Versiones: {g.versions}</div>
                </div>
              </div>
              <div className="text-right">
                <button
                  type="button"
                  className="px-3 py-1 border rounded hover:bg-gray-100 text-gray-700"
                  onClick={() => setActiveGame({ id: g.id, name: g.name })}
                >
                  Descargar
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-center gap-2 mt-4">
          <PageButton label="<<" disabled={page <= 1} onClick={() => setPage(1)} />
          <PageButton label="<" disabled={page <= 1} onClick={() => setPage(page - 1)} />
          <span className="px-2">Página {page} de {totalPages}</span>
          <PageButton label=">" disabled={page >= totalPages} onClick={() => setPage(page + 1)} />
          <PageButton label=">>" disabled={page >= totalPages} onClick={() => setPage(totalPages)} />
        </div>
      </div>

      {showScrollTop && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="fixed bottom-6 right-6 bg-retro-blue text-white rounded-full w-11 h-11 shadow-lg hover:opacity-90 btn-hover-effect focus-ring"
          aria-label="Volver arriba"
        >
          ↑
        </button>
      )}

      {activeGame && (
        <VersionsModal
          gameId={activeGame.id}
          gameName={activeGame.name}
          onClose={() => setActiveGame(null)}
        />
      )}
    </main>
  );
}

function PageButton({ label, disabled, onClick }: { label: string; disabled: boolean; onClick: () => void }) {
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      className={`px-3 py-1 border rounded ${disabled ? "opacity-50 cursor-not-allowed" : "hover:bg-gray-100"}`}
      aria-label={label}
    >
      {label}
    </button>
  );
}
