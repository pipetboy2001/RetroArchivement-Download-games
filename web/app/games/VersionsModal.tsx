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
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4 modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg sm:max-w-2xl overflow-hidden fade-in flex flex-col modal-panel modal-max-h">
        <div className="gradient-bg text-white p-4 flex items-center justify-between">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <span className="text-xl">🎮</span>
            Versiones de: {gameName}
          </h2>
          <button type="button" className="text-white hover:text-gray-200 text-2xl font-bold focus-ring" onClick={onClose}>
            &times;
          </button>
        </div>

        <div className="p-4 flex-1 overflow-y-auto custom-scrollbar modal-body">
          <p className="text-gray-600 mb-4 text-sm">Este juego tiene múltiples versiones disponibles. Selecciona la que prefieras:</p>

          {!versions && !error && (
            <div className="text-center py-8">
              <div className="spinner mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando versiones...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg text-center">
              No se pudieron cargar las versiones
            </div>
          )}

          {versions && versions.length === 0 && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg text-center">
              No hay versiones disponibles.
            </div>
          )}

          {versions && versions.length > 0 && (
            <>
              <div className="space-y-2">
                {current.map((v, localIdx) => {
                  const idx = start + localIdx;
                  const isRecommended = idx === 0;
                  const filename = v.info?.filename || v.rom_path;
                  return (
                    <a
                      key={v.hash}
                      href={`/dl?hash=${encodeURIComponent(v.hash)}`}
                      className={`version-option block border ${isRecommended ? "border-green-500 bg-green-50" : "border-gray-200"} rounded-lg p-3 hover:shadow-md transition-all duration-300 cursor-pointer`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="font-medium text-gray-800 text-sm">{filename}</h4>
                        {isRecommended && <span className="badge-success text-xs">✅ Recomendada</span>}
                      </div>
                      <div className="flex flex-wrap gap-1 mb-1">
                        {v.info?.region && v.info.region !== "Unknown" && (
                          <span className="badge-success text-xs">{v.info.region}</span>
                        )}
                        {v.info?.is_hack && <span className="badge-warning text-xs">HACK</span>}
                        {v.info?.is_translation && <span className="badge-warning text-xs">TRADUCCIÓN</span>}
                      </div>
                      <p className="text-xs text-gray-600">Hash: {v.hash}</p>
                    </a>
                  );
                })}
              </div>

              <div className="flex flex-wrap items-center justify-center gap-2 mt-3 modal-pagination">
                <PageButton label="<<" disabled={currentPage <= 1} onClick={() => setPage(1)} />
                <PageButton label="<" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)} />
                <span className="px-2 text-sm">Página {currentPage} de {totalPages}</span>
                <PageButton label=">" disabled={currentPage >= totalPages} onClick={() => setPage(currentPage + 1)} />
                <PageButton label=">>" disabled={currentPage >= totalPages} onClick={() => setPage(totalPages)} />
              </div>
            </>
          )}
        </div>

        <div className="bg-gray-50 px-4 py-3 flex justify-end">
          <button type="button" className="bg-gray-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-600 transition-all duration-300 btn-hover-effect focus-ring" onClick={onClose}>
            Cancelar
          </button>
        </div>
      </div>
    </div>
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
