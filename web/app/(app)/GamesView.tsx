"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import GameCard from "./GameCard";
import { useCart } from "./CartContext";
import { SearchIcon } from "./icons";
import type { ConsoleCount, Game, GamesResponse, SearchResult } from "./types";

const PAGE_SIZE = 50;
const PILL_COUNT = 6;
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
  const topConsoles = sortedConsoles.slice(0, PILL_COUNT);
  const restConsoles = sortedConsoles.slice(PILL_COUNT);
  const filterInRest = restConsoles.some((c) => c.name === consoleFilter);

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
        <SearchIcon />
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
          <div className="pill-row">
            <button
              type="button"
              className={`pill${consoleFilter === "" ? " active" : ""}`}
              onClick={() => {
                setConsoleFilter("");
                setPage(1);
              }}
            >
              Todo
            </button>
            {topConsoles.map((c) => (
              <button
                key={c.name}
                type="button"
                className={`pill${consoleFilter === c.name ? " active" : ""}`}
                onClick={() => {
                  setConsoleFilter(c.name);
                  setPage(1);
                }}
              >
                {c.name}
              </button>
            ))}
            {restConsoles.length > 0 && (
              <div className={`pill pill-more${filterInRest ? " active" : ""}`}>
                <span>{filterInRest ? consoleFilter : `+${restConsoles.length} más`}</span>
                <select
                  value={filterInRest ? consoleFilter : ""}
                  onChange={(e) => {
                    setConsoleFilter(e.target.value);
                    setPage(1);
                  }}
                  aria-label="Más consolas"
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

          <div className="grid-head">
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

          {items.length === 0 ? (
            <p className="empty-hint">Sin resultados.</p>
          ) : (
            <div className="games-grid">
              {items.map((g) => (
                <GameCard key={g.id} game={g} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  );
}
