"use client";

import { useEffect, useState } from "react";
import type { Version, VersionsResponse } from "./types";

const PAGE_SIZE = 10;

export default function VersionsModal({
  gameId,
  gameName,
  onClose,
}: {
  gameId: string | null;
  gameName: string;
  onClose: () => void;
}) {
  const [versions, setVersions] = useState<Version[] | null>(null);
  const [error, setError] = useState(false);
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!gameId) return;
    setVersions(null);
    setError(false);
    setPage(1);

    const form = new FormData();
    form.append("game_id", gameId);

    fetch("/get_game_versions", { method: "POST", body: form })
      .then((res) => res.json() as Promise<VersionsResponse>)
      .then((res) => {
        if (res.success) setVersions(res.versions);
        else setError(true);
      })
      .catch(() => setError(true));
  }, [gameId]);

  if (!gameId) return null;

  const total = versions?.length ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const current = versions?.slice(start, start + PAGE_SIZE) ?? [];

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-panel">
        <div className="modal-head">
          <h2>Versiones de {gameName}</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            &times;
          </button>
        </div>

        <div className="modal-body">
          {!versions && !error && <p className="empty-hint">Cargando versiones…</p>}
          {error && <p className="empty-hint">No se pudieron cargar las versiones.</p>}
          {versions && versions.length === 0 && <p className="empty-hint">No hay versiones disponibles.</p>}

          {versions && versions.length > 0 && (
            <>
              {current.map((v, localIdx) => {
                const idx = start + localIdx;
                const isRecommended = idx === 0;
                const filename = v.info?.filename || v.rom_path;
                return (
                  <a
                    key={v.hash}
                    href={`/dl?hash=${encodeURIComponent(v.hash)}`}
                    className={`version-option${isRecommended ? " recommended" : ""}`}
                  >
                    <h4>{filename}</h4>
                    <div style={{ display: "flex", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
                      {isRecommended && <span className="badge ok">recomendada</span>}
                      {v.info?.region && v.info.region !== "Unknown" && (
                        <span className="badge ok">{v.info.region}</span>
                      )}
                      {v.info?.is_hack && <span className="badge warn">hack</span>}
                      {v.info?.is_translation && <span className="badge warn">traducción</span>}
                    </div>
                    <div className="hash">{v.hash}</div>
                  </a>
                );
              })}

              <div className="pager" style={{ marginTop: 12, justifyContent: "center" }}>
                <button type="button" disabled={currentPage <= 1} onClick={() => setPage(1)}>
                  «
                </button>
                <button type="button" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)}>
                  ‹
                </button>
                <span className="num">
                  {currentPage} / {totalPages}
                </span>
                <button type="button" disabled={currentPage >= totalPages} onClick={() => setPage(currentPage + 1)}>
                  ›
                </button>
                <button type="button" disabled={currentPage >= totalPages} onClick={() => setPage(totalPages)}>
                  »
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
