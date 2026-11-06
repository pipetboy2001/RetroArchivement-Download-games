"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useCart } from "./CartContext";
import { downloadGame } from "./download";
import { BoltIcon, CheckIcon, CopyIcon, PlusIcon, TrophyIcon } from "./icons";
import type { Game, Version, VersionsResponse } from "./types";

export default function GameCard({ game }: { game: Game }) {
  const cart = useCart();
  const [versions, setVersions] = useState<Version[] | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const form = new FormData();
    form.append("game_id", game.id);
    fetch("/get_game_versions", { method: "POST", body: form })
      .then((res) => res.json() as Promise<VersionsResponse>)
      .then((data) => {
        if (!cancelled && data.success) setVersions(data.versions);
      });
    return () => {
      cancelled = true;
    };
  }, [game.id]);

  const active = versions?.[selectedIndex];
  const inCart = cart.has(game.id);

  function addToCart() {
    if (!active) return;
    cart.add({
      id: game.id,
      name: game.name,
      consoles: game.consoles,
      image_icon: game.image_icon,
      achievements: game.achievements,
      hash: active.hash,
      rom_path: active.rom_path,
    });
  }

  function copyHash() {
    if (!active) return;
    navigator.clipboard.writeText(active.hash).then(() => {
      toast("Hash copiado");
    });
  }

  return (
    <div className="gcard">
      <div className="gcard-cover">
        {game.image_icon ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={game.image_icon} alt="" loading="lazy" />
        ) : (
          <div className="placeholder" />
        )}
        <span className="gcard-console">{game.consoles.join(", ") || "?"}</span>
        {game.achievements != null && (
          <span className="gcard-trophy">
            <TrophyIcon /> {game.achievements}
          </span>
        )}
      </div>

      <div className="gcard-body">
        <div className="gcard-title">{game.name}</div>

        <div className="gcard-field">
          <label>Versión / ROM</label>
          <select
            className="gcard-select"
            value={selectedIndex}
            disabled={!versions || versions.length === 0}
            onChange={(e) => setSelectedIndex(Number(e.target.value))}
          >
            {!versions && <option>Cargando…</option>}
            {versions?.length === 0 && <option>Sin versiones</option>}
            {versions?.map((v, idx) => (
              <option key={v.hash} value={idx}>
                {v.info?.filename || v.rom_path}
              </option>
            ))}
          </select>
        </div>

        <div className="gcard-field">
          <label>Espejo de descarga</label>
          <div className="mirror-row">
            <span className="mirror-chip active">archive.org</span>
            <button type="button" className="mirror-chip" disabled title="Próximamente">
              CoolROM
            </button>
          </div>
          <div className="mirror-note">
            Otros espejos <span className="soon-badge">próximamente</span>
          </div>
        </div>

        <div className="gcard-actions">
          {active ? (
            <button type="button" className="btn-ghost" onClick={() => downloadGame(active.hash, game.name)}>
              <BoltIcon /> Descargar
            </button>
          ) : (
            <span className="btn-ghost" aria-disabled>
              <BoltIcon /> Descargar
            </span>
          )}
          <button type="button" className="icon-btn" onClick={copyHash} disabled={!active} title="Copiar hash MD5">
            <CopyIcon />
          </button>
          <button
            type="button"
            className={`icon-btn${inCart ? " in-cart" : ""}`}
            onClick={addToCart}
            disabled={!active || inCart}
            title={inCart ? "En el carrito" : "Agregar al carrito"}
          >
            {inCart ? <CheckIcon key="check" className="icon-pop" /> : <PlusIcon key="plus" />}
          </button>
        </div>
      </div>
    </div>
  );
}
