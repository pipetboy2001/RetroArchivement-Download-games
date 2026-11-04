"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, type FormEvent, type ReactNode } from "react";
import { CartProvider, useCart } from "./CartContext";
import NoticeModal from "./NoticeModal";

function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { items } = useCart();
  const [q, setQ] = useState("");

  function onSearchSubmit(e: FormEvent) {
    e.preventDefault();
    const term = q.trim();
    router.push(term ? `/?q=${encodeURIComponent(term)}` : "/");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <div className="mark">R</div>
          <div>
            <div className="name">RA Downloader</div>
            <div className="sub">roms para RetroAchievements</div>
          </div>
        </Link>
        <nav className="primary">
          <Link href="/" className={pathname === "/" ? "active" : undefined}>
            <span>Buscar</span>
          </Link>
          <Link href="/carrito" className={pathname === "/carrito" ? "active" : undefined}>
            <span>Carrito</span>
            {items.length > 0 && <span className="count">{items.length}</span>}
          </Link>
        </nav>
      </aside>

      <header className="topbar">
        <form className="search" onSubmit={onSearchSubmit}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por nombre o hash…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </form>
      </header>

      <main className="app-main">{children}</main>
      <NoticeModal />
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
