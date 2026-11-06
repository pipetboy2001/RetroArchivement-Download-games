"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useCart } from "./CartContext";
import { openDownload } from "./download";
import { TrashIcon, XIcon } from "./icons";

const EXIT_MS = 280;

export default function CartDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const cart = useCart();
  const count = cart.items.length;
  const [mounted, setMounted] = useState(open);
  const [entered, setEntered] = useState(false);

  // Abrir: montar ya (durante el render, no en un efecto -- React lo aplica
  // antes del paint) para que el frame siguiente pueda animar desde el
  // estado "cerrado". Cerrar: desmontar recién después de EXIT_MS, para que
  // la transición de salida llegue a verse antes de sacar el nodo del DOM.
  if (open && !mounted) setMounted(true);
  if (!open && entered) setEntered(false);

  useEffect(() => {
    if (open) {
      const raf = requestAnimationFrame(() => setEntered(true));
      return () => cancelAnimationFrame(raf);
    }
    const t = setTimeout(() => setMounted(false), EXIT_MS);
    return () => clearTimeout(t);
  }, [open]);

  if (!mounted) return null;

  function downloadAll() {
    cart.items.forEach((item) => openDownload(item.hash));
    toast(`Descargando ${count} juego${count === 1 ? "" : "s"}…`);
  }

  return (
    <>
      <div className={`drawer-overlay${entered ? " open" : ""}`} onClick={onClose} />
      <aside className={`drawer-panel${entered ? " open" : ""}`}>
        <div className="drawer-head">
          <div>
            <h2>Carrito de descarga</h2>
            <div className="sub">{count} juego{count === 1 ? "" : "s"} seleccionado{count === 1 ? "" : "s"}</div>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            <XIcon />
          </button>
        </div>

        <div className="drawer-body">
          {count === 0 ? (
            <p className="empty-hint" style={{ margin: 0, borderTop: "none", paddingTop: 0 }}>
              El carrito está vacío.
            </p>
          ) : (
            cart.items.map((item) => (
              <div className="cart-item" key={item.id}>
                {item.image_icon ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={item.image_icon} alt="" className="icon" loading="lazy" />
                ) : (
                  <div className="icon" />
                )}
                <div className="meta">
                  <div className="name">{item.name}</div>
                  <div className="sub">{item.consoles.join(", ") || "Consola desconocida"}</div>
                </div>
                <button type="button" className="remove" onClick={() => cart.remove(item.id)} aria-label="Quitar">
                  <TrashIcon />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="drawer-section">
          <label>
            Estructura de exportación
            <span className="soon-badge">próximamente</span>
          </label>
          <select className="gcard-select" disabled style={{ marginBottom: 8 }}>
            <option>Raíz plana (todos juntos)</option>
          </select>
          <div className="tree-preview">
            <span style={{ opacity: 0.6, fontStyle: "italic" }}>
              El empaquetado en ZIP con estructura de carpetas (RetroArch, OnionOS, Batocera) todavía no está
              disponible. Por ahora, &quot;Descargar todo&quot; abre cada archivo por separado.
            </span>
          </div>
        </div>

        <div className="drawer-footer">
          <button type="button" className="btn-primary" disabled={count === 0} onClick={downloadAll}>
            Descargar todo ({count})
          </button>
        </div>
      </aside>
    </>
  );
}
