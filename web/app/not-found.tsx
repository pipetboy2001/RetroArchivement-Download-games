import Link from "next/link";
import { Ghost } from "lucide-react";

export default function NotFound() {
  return (
    <div className="notfound-page">
      <Ghost className="notfound-ghost" size={40} strokeWidth={1.5} />
      <div className="code">404</div>
      <h1>Página no encontrada</h1>
      <p>La página que buscás no existe o se movió de lugar.</p>
      <Link href="/" className="btn-primary" style={{ marginTop: 8 }}>
        Volver al inicio
      </Link>
    </div>
  );
}
