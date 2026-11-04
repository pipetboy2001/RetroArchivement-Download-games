"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import VersionsModal from "./VersionsModal";
import { useCart } from "./CartContext";
import type { ConsoleCount, Game, GamesResponse, SearchResult } from "./types";

const PAGE_SIZE = 50;
const HASH_RE = /^[0-9a-f]{8,}$/i;

export default function GamesView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const cart = useCart();

  const [input, setInput] = useState("");
  const [q, setQ] = useState("");
  const [consoleFilter, setConsoleFilter] = useState("");
  const [page, setPage] = useState(1);

  // Sincroniza con ?q= de la URL: en el primer montaje (deep link) y cuando
  // otro componente (el buscador del topbar) navega a /?q=... mientras
  // esta vista ya está montada -- el valor inicial de useState no reacciona
  // a esos cambios por sí solo.
  useEffect(() => {
    const next = searchParams.get("q") ?? "";
    setInput(next);
    setQ(next);
    setPage(1);
  }, [searchParams]);

  const [items, setItems] = useState<Game[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [consoles, setConsoles] = useState<ConsoleCount[]>([]);
  const [allTotal, setAllTotal] = useState(0);

  const [verify, setVerify] = useState<SearchResult | null>(null);
  const [verifyHash, setVerifyHash] = useState("");
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [verifyError, setVerifyError] = useState("");

  const [activeGame, setActiveGame] = useState<{ id: string; name: string } | null>(null);
  const [addingId, setAddingId] = useState<string | null>(null);

  const typingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isHash = HASH_RE.test(q);

  useEffect(() => {
    fetch("/api/games?page=1&page_size=1")
      .then((res) => res.json() as Promise<GamesResponse>)
      .then((data) => setAllTotal(data.total || 0));
  }, []);

  useEffect(() => {
    if (isHash) return;
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (consoleFilter) params.set("console", consoleFilter);
    params.set("page", String(page));
    params.set("page_size", String(PAGE_SIZE));

    fetch(`/api/games?${params.toString()}`)
      .then((res) => res.json() as Promise<GamesResponse>)
      .then((data) => {
        setItems(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
        setConsoles(data.consoles || []);
      });
  }, [q, consoleFilter, page, isHash]);

  useEffect(() => {
    if (!isHash) {
      setVerify(null);
      setVerifyError("");
      return;
    }
    setVerifyLoading(true);
    setVerify(null);
    setVerifyError("");
    setVerifyHash(q);

    const form = new FormData();
    form.append("search_term", q);

    fetch("/search", { method: "POST", body: form })
      .then((res) => res.json() as Promise<SearchResult>)
      .then((data) => {
        if (data.success) setVerify(data);
        else setVerifyError(data.message || "No se encontró ese hash en la base de datos.");
      })
      .catch(() => setVerifyError("No se pudo verificar el hash."))
      .finally(() => setVerifyLoading(false));
  }, [q, isHash]);

  function runSearch(value: string) {
    const trimmed = value.trim();
    setQ(trimmed);
    setPage(1);
    router.replace(trimmed ? `/?q=${encodeURIComponent(trimmed)}` : "/");
  }

  function onInputChange(value: string) {
    setInput(value);
    if (typingTimer.current) clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => runSearch(value), 300);
  }

  async function addRowToCart(g: Game) {
    setAddingId(g.id);
    try {
      const form = new FormData();
      form.append("game_id", g.id);
      const res = await fetch("/get_game_versions", { method: "POST", body: form });
      const data = await res.json();
      if (data.success && data.versions?.length) {
        const v = data.versions[0];
        cart.add({
          id: g.id,
          name: g.name,
          consoles: g.consoles,
          image_icon: g.image_icon,
          achievements: g.achievements,
          hash: v.hash,
          rom_path: v.rom_path,
        });
      }
    } finally {
      setAddingId(null);
    }
  }

  function addVerifyToCart() {
    if (!verify) return;
    cart.add({
      id: verifyHash,
      name: verify.name ?? verifyHash,
      consoles: verify.console ? [verify.console] : [],
      image_icon: null,
      achievements: null,
      hash: verifyHash,
      rom_path: "",
    });
  }

  const sortedConsoles = [...consoles].sort((a, b) => b.count - a.count);
  const topConsoles = sortedConsoles.slice(0, 4);
  const restConsoles = sortedConsoles.slice(4);

  return (
    <>
      <div className="title-row">
        <div>
          <h1>Buscar juegos</h1>
          <div className="sub">
            <b className="num">{allTotal}</b> juegos indexados
          </div>
        </div>
      </div>

      <div className="search" style={{ marginBottom: 24, maxWidth: 420 }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input type="text" placeholder="Nombre o hash…" value={input} onChange={(e) => onInputChange(e.target.value)} />
      </div>

      {isHash ? (
        <>
          {verifyLoading && <p className="empty-hint">Verificando hash…</p>}
          {verifyError && <p className="empty-hint">{verifyError}</p>}
          {verify && (
            <div className="verify">
              <div className="icon" />
              <div className="meta">
                <div className="name">{verify.name ?? "Juego encontrado"}</div>
                <div className="sub">{verify.console ?? "Consola desconocida"}</div>
                <div className="hash">{verifyHash}</div>
              </div>
              <div className="checks">
                <span className={`badge ${verify.ra_recognized ? "ok" : "warn"}`}>
                  {verify.ra_recognized ? "reconocido por RA" : "no reconocido por RA"}
                </span>
                <span className={`badge ${verify.link_ok ? "ok" : "warn"}`}>
                  {verify.link_ok ? "enlace verificado" : "enlace no verificado"}
                </span>
              </div>
              <button
                type="button"
                className="btn-ghost"
                disabled={cart.has(verifyHash)}
                onClick={addVerifyToCart}
              >
                {cart.has(verifyHash) ? "En el carrito" : "Agregar al carrito"}
              </button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="filters">
            <button
              type="button"
              className={`fcard${consoleFilter === "" ? " selected" : ""}`}
              onClick={() => {
                setConsoleFilter("");
                setPage(1);
              }}
            >
              <div className="flabel">Todas</div>
              <div className="fvalue num">{allTotal}</div>
            </button>
            {topConsoles.map((c) => (
              <button
                key={c.name}
                type="button"
                className={`fcard${consoleFilter === c.name ? " selected" : ""}`}
                onClick={() => {
                  setConsoleFilter(c.name);
                  setPage(1);
                }}
              >
                <div className="flabel">{c.name}</div>
                <div className="fvalue num">{c.count}</div>
              </button>
            ))}
            {restConsoles.length > 0 && (
              <div className="fcard more" style={{ position: "relative" }}>
                <span>{restConsoles.some((c) => c.name === consoleFilter) ? consoleFilter : `+${restConsoles.length} más`}</span>
                <select
                  value={restConsoles.some((c) => c.name === consoleFilter) ? consoleFilter : ""}
                  onChange={(e) => {
                    setConsoleFilter(e.target.value);
                    setPage(1);
                  }}
                  style={{ position: "absolute", inset: 0, opacity: 0, cursor: "pointer" }}
                >
                  <option value="">+{restConsoles.length} más</option>
                  {restConsoles.map((c) => (
                    <option key={c.name} value={c.name}>
                      {c.name} ({c.count})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="list-card">
            <div className="list-head">
              <span>
                {total} juegos{consoleFilter ? ` en ${consoleFilter}` : ""}
              </span>
              <div className="pager">
                <button type="button" disabled={page <= 1} onClick={() => setPage(1)}>
                  «
                </button>
                <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  ‹
                </button>
                <span className="num">
                  {page} / {totalPages}
                </span>
                <button type="button" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                  ›
                </button>
                <button type="button" disabled={page >= totalPages} onClick={() => setPage(totalPages)}>
                  »
                </button>
              </div>
            </div>

            {items.length === 0 && (
              <div className="row">
                <div className="meta">Sin resultados.</div>
              </div>
            )}

            {items.map((g) => (
              <div className="row" key={g.id}>
                {g.image_icon ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={g.image_icon} alt="" className="icon" loading="lazy" />
                ) : (
                  <div className="icon" />
                )}
                <div className="meta">
                  <div className="name">
                    {g.name}
                    {g.achievements != null && (
                      <span className="badge gold" style={{ marginLeft: 8 }}>
                        logros · {g.achievements}
                      </span>
                    )}
                  </div>
                  <div className="sub">
                    {g.consoles.join(", ")} · {g.versions} versión{g.versions === 1 ? "" : "es"}
                  </div>
                </div>
                <button
                  type="button"
                  className="btn-ghost"
                  disabled={cart.has(g.id) || addingId === g.id}
                  onClick={() => addRowToCart(g)}
                >
                  {cart.has(g.id) ? "En el carrito" : addingId === g.id ? "Agregando…" : "Agregar al carrito"}
                </button>
                <button type="button" className="btn-ghost" onClick={() => setActiveGame({ id: g.id, name: g.name })}>
                  Descargar
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {activeGame && (
        <VersionsModal gameId={activeGame.id} gameName={activeGame.name} onClose={() => setActiveGame(null)} />
      )}
    </>
  );
}
