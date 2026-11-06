"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogClose } from "@/components/ui/dialog";

const STORAGE_KEY = "ra-downloader-notice-seen";

export default function NoticeModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!sessionStorage.getItem(STORAGE_KEY)) setOpen(true);
  }, []);

  function dismiss() {
    sessionStorage.setItem(STORAGE_KEY, "1");
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={(o: boolean) => !o && dismiss()}>
      <DialogContent className="modal-panel" showCloseButton={false}>
        <div className="modal-head">
          <DialogTitle>Antes de descargar</DialogTitle>
          <DialogClose className="modal-close" aria-label="Cerrar">
            &times;
          </DialogClose>
        </div>
        <div className="modal-body">
          <p style={{ margin: 0 }}>
            Nota: Para descargar, primero inicia sesión en{" "}
            <a href="https://archive.org/" target="_blank" rel="noopener" style={{ color: "var(--link)" }}>
              archive.org
            </a>
            . Los juegos no son de mi propiedad; todo el contenido está alojado en archive.org. Esta
            herramienta solo facilita enlaces de ROMs compatibles con RetroAchievements. Consulta la{" "}
            <a href="/faq" style={{ color: "var(--link)" }}>
              FAQ y Aviso legal
            </a>
            .
          </p>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "0 18px 16px" }}>
          <button type="button" className="btn-primary" onClick={dismiss}>
            Entendido
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
