"use client";

import { useCart } from "../CartContext";

export default function CarritoPage() {
  const cart = useCart();
  const count = cart.items.length;

  function downloadAll() {
    cart.items.forEach((item) => {
      window.open(`/dl?hash=${encodeURIComponent(item.hash)}`, "_blank");
    });
  }

  return (
    <>
      <div className="title-row">
        <div>
          <h1>Carrito</h1>
          <div className="sub">
            <b className="num">{count}</b> juego{count === 1 ? "" : "s"} listo{count === 1 ? "" : "s"} para descargar
          </div>
        </div>
        {count > 0 && (
          <button type="button" className="btn-primary" onClick={downloadAll}>
            Descargar todo ({count})
          </button>
        )}
      </div>

      {count === 0 ? (
        <p className="empty-hint">
          El carrito está vacío.{" "}
          <a href="/" style={{ color: "var(--link)" }}>
            Ir a Buscar
          </a>{" "}
          para agregar juegos.
        </p>
      ) : (
        <div className="list-card">
          <div className="list-head">
            <span>{count} juegos</span>
          </div>
          {cart.items.map((item) => (
            <div className="row" key={item.id}>
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
                Quitar
              </button>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
