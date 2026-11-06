"use client";

import { Dialog, DialogContent, DialogTitle, DialogClose } from "@/components/ui/dialog";
import { UserIcon } from "./icons";

export default function RaAccountModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Dialog open={open} onOpenChange={(o: boolean) => !o && onClose()}>
      <DialogContent className="modal-panel" style={{ maxWidth: 420 }} showCloseButton={false}>
        <div className="modal-head">
          <DialogTitle>Conectar RetroAchievements</DialogTitle>
          <DialogClose className="modal-close" aria-label="Cerrar">
            &times;
          </DialogClose>
        </div>
        <div className="modal-body">
          <div className="soon-panel">
            <UserIcon size={32} />
            <h3>Próximamente</h3>
            <p>
              Vas a poder conectar tu cuenta con tu propia Web API Key (nunca se guarda en nuestro servidor)
              para traer tu lista &quot;Want to Play&quot; y ver qué juegos ya tenemos disponibles para descargar.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
