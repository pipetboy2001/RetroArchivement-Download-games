"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";
import { CartProvider, useCart } from "./CartContext";
import CartDrawer from "./CartDrawer";
import Footer from "./Footer";
import HasherModal from "./HasherModal";
import NoticeModal from "./NoticeModal";
import RaAccountModal from "./RaAccountModal";
import { CartIcon, FingerprintIcon, SearchIcon, UserIcon } from "./icons";

function Shell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { items } = useCart();
  const [q, setQ] = useState("");
  const [cartOpen, setCartOpen] = useState(false);
  const [hasherOpen, setHasherOpen] = useState(false);
  const [raOpen, setRaOpen] = useState(false);

  function onSearchSubmit(e: FormEvent) {
    e.preventDefault();
    const term = q.trim();
    router.push(term ? `/?q=${encodeURIComponent(term)}` : "/");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link href="/" className="brand">
            <div className="mark">R</div>
            <div className="name">RA Downloader</div>
          </Link>

          <form className="search" onSubmit={onSearchSubmit}>
            <SearchIcon />
            <input
              type="text"
              placeholder="Buscar por nombre o hash…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </form>

          <div className="header-actions">
            <button type="button" className="icon-btn-labeled" onClick={() => setHasherOpen(true)}>
              <FingerprintIcon /> <span>Verificar ROM</span>
            </button>
            <button type="button" className="icon-btn-labeled" onClick={() => setRaOpen(true)}>
              <UserIcon /> <span>Conectar RA</span>
            </button>
            <button type="button" className="cart-trigger" onClick={() => setCartOpen(true)} aria-label="Abrir carrito">
              <CartIcon />
              {items.length > 0 && <span className="count">{items.length}</span>}
            </button>
          </div>
        </div>
      </header>

      <main className="app-main">{children}</main>
      <Footer />
      <NoticeModal />
      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
      <HasherModal open={hasherOpen} onClose={() => setHasherOpen(false)} />
      <RaAccountModal open={raOpen} onClose={() => setRaOpen(false)} />
    </div>
  );
}

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <CartProvider>
      <Shell>{children}</Shell>
    </CartProvider>
  );
}
