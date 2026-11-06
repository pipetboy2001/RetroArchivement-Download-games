"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { SearchIcon } from "./icons";
import type { ConsoleCount } from "./types";

export default function ConsoleFilterDropdown({
  consoles,
  value,
  selected,
  onChange,
}: {
  consoles: ConsoleCount[];
  /** true si el valor seleccionado actual pertenece a esta lista (no a los pills de arriba). */
  selected: boolean;
  value: string;
  onChange: (name: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  // Posición calculada a mano y el panel va en un portal a <body>: .pill-row
  // tiene overflow-x: auto, que en CSS también clippea verticalmente -- un
  // panel position:absolute anidado ahí adentro queda invisible/inclickeable
  // más allá de la altura de la fila, sin importar su z-index.
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function close() {
    setOpen(false);
    setQuery("");
  }

  function toggle() {
    if (!open && triggerRef.current) {
      const r = triggerRef.current.getBoundingClientRect();
      setPos({ top: r.bottom + 6, left: r.left });
    }
    setOpen((v) => !v);
  }

  useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      const target = e.target as Node;
      if (panelRef.current?.contains(target)) return;
      if (triggerRef.current?.contains(target)) return;
      close();
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  const filtered = consoles.filter((c) => c.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <>
      <button type="button" ref={triggerRef} className={`pill${selected ? " active" : ""}`} onClick={toggle}>
        {selected ? value : `+${consoles.length} más`}
      </button>
      {open &&
        pos &&
        createPortal(
          <div className="console-dropdown" ref={panelRef} style={{ top: pos.top, left: pos.left }}>
            <div className="console-dropdown-search">
              <SearchIcon />
              <input
                ref={inputRef}
                type="text"
                placeholder="Buscar consola…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Escape") close();
                }}
              />
            </div>
            <div className="console-dropdown-list">
              {filtered.length === 0 && <div className="console-dropdown-empty">Sin resultados</div>}
              {filtered.map((c) => (
                <button
                  key={c.name}
                  type="button"
                  className={`console-dropdown-item${value === c.name ? " active" : ""}`}
                  onClick={() => {
                    onChange(c.name);
                    close();
                  }}
                >
                  <span>{c.name}</span>
                  <span className="console-dropdown-count">{c.count}</span>
                </button>
              ))}
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
