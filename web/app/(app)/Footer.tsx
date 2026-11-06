import Link from "next/link";

export default function Footer() {
  return (
    <footer className="site-footer">
      <p>
        Desarrollado por{" "}
        <a href="https://github.com/pipetboy2001" target="_blank" rel="noopener">
          Pipetboy
        </a>
        <span className="sep">·</span>
        <Link href="/faq">FAQ y Aviso legal</Link>
      </p>
    </footer>
  );
}
