import { toast } from "sonner";

/** Abre el link de descarga en una pestaña nueva, sin tocar el toast (para descargas en lote). */
export function openDownload(hash: string): void {
  window.open(`/dl?hash=${encodeURIComponent(hash)}`, "_blank");
}

/** Descarga un solo juego y avisa con un toast. */
export function downloadGame(hash: string, name?: string): void {
  openDownload(hash);
  toast(name ? `Descargando ${name}…` : "Descargando juego…");
}
