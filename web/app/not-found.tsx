import Link from "next/link";

export default function NotFound() {
  return (
    <div className="notfound-page">
      <div className="code">404</div>
      <h1>Página no encontrada</h1>
      <p>La página que buscás no existe o se movió de lugar.</p>
      <Link href="/" className="btn-primary" style={{ textDecoration: "none", display: "inline-block", marginTop: 8 }}>
        Volver al inicio
      </Link>
    </div>
  );
}
