import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "FAQ y Aviso Legal - RA Downloader",
};

export default function FaqPage() {
  return (
    <div className="faq-page">
      <div className="title-row">
        <div>
          <h1>Preguntas frecuentes (FAQ)</h1>
        </div>
      </div>

      <div className="faq-panel">
        <details className="faq-item" open>
          <summary>¿Qué es este proyecto?</summary>
          <p className="faq-answer">
            Esta herramienta ayuda a localizar y abrir enlaces de descarga de ROMs compatibles con los logros de
            RetroAchievements. No aloja ni distribuye archivos; solo redirige a contenidos públicos alojados en
            archive.org.
          </p>
        </details>

        <details className="faq-item" open>
          <summary>Inicio de sesión en archive.org</summary>
          <p className="faq-answer">
            Para descargar, primero inicia sesión en{" "}
            <a href="https://archive.org/" target="_blank" rel="noopener" style={{ color: "var(--link)" }}>
              archive.org
            </a>
            . Sin sesión activa, las descargas pueden fallar o requerir verificación adicional.
          </p>
        </details>

        <details className="faq-item">
          <summary>¿De quién son los juegos/ROMs?</summary>
          <p className="faq-answer">
            Todos los archivos referenciados pertenecen a sus respectivos propietarios y están{" "}
            <strong>almacenados en archive.org</strong>. Este proyecto no es propietario de ningún juego ni
            contenido y no los almacena.
          </p>
        </details>

        <details className="faq-item">
          <summary>Compatibilidad con RetroAchievements</summary>
          <p className="faq-answer">
            Los enlaces se centran en ROMs que funcionan con los <em>sets</em> de logros de RetroAchievements. No
            se garantiza compatibilidad universal; sigue las recomendaciones de hashes y versiones publicadas por
            RetroAchievements.
          </p>
        </details>

        <details className="faq-item">
          <summary>¿La app descarga automáticamente?</summary>
          <p className="faq-answer">No. Abrimos la URL de descarga en tu navegador para que completes el proceso en archive.org.</p>
        </details>

        <h2>Aviso legal</h2>
        <ul className="faq-list">
          <li>Este proyecto no aloja, modifica, ni redistribuye ROMs. Solo facilita el acceso a enlaces públicos en archive.org.</li>
          <li>Los juegos, marcas y contenidos son propiedad de sus respectivos titulares. Su uso está sujeto a las leyes de derechos de autor aplicables en tu jurisdicción.</li>
          <li>El autor/desarrollador <strong>no se responsabiliza</strong> por el uso indebido de la herramienta ni por posibles infracciones de copyright por parte de los usuarios.</li>
          <li>El usuario es responsable de verificar que posee los derechos para descargar y usar cada archivo (por ejemplo, copias de seguridad de juegos que posee legalmente).</li>
          <li>RetroAchievements es una plataforma de terceros sin relación oficial con este proyecto.</li>
        </ul>

        <h2>Consejos</h2>
        <ul className="faq-list">
          <li>Inicia sesión en archive.org antes de usar la búsqueda o abrir enlaces.</li>
          <li>Prefiere ROMs y hashes listados como compatibles en la página del juego de RetroAchievements.</li>
          <li>Respeta las leyes locales y los términos de uso de archive.org y RetroAchievements.</li>
        </ul>

        <div style={{ marginTop: 24 }}>
          <Link href="/" className="btn-primary">
            Volver al inicio
          </Link>
        </div>
      </div>
    </div>
  );
}
