import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    // Hay un package.json/lockfile en la raíz del repo (scripts dev:api/dev:web/dev)
    // ademas del de web/ -- sin esto, Turbopack infiere mal la raíz del workspace.
    root: __dirname,
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  // En producción, Vercel Services rutea /api/*, /get_game_versions, /dl,
  // /search y /faq directo al servicio Flask antes de que Next.js los vea
  // (ver vercel.json en la raíz) -- estos rewrites nunca se ejecutan ahí.
  // Solo sirven para `npm run dev`, donde Flask corre aparte en
  // localhost:5000 (ver package.json de la raíz: dev:api / dev:web / dev).
  //
  // "/faq" va en `beforeFiles` porque sigue siendo de Flask y no hay ninguna
  // ruta de Next ahí que lo tape. "/" en cambio ahora SÍ es una ruta real de
  // Next (app/(app)/page.tsx, antes /games) -- por eso ya no está acá: si
  // estuviera en beforeFiles volvería a tapar la página real, el mismo bug
  // que tuvo "/" cuando todavía era el placeholder de create-next-app.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return {
      beforeFiles: [{ source: "/faq", destination: "http://localhost:5000/faq" }],
      afterFiles: [
        { source: "/api/:path*", destination: "http://localhost:5000/api/:path*" },
        { source: "/get_game_versions", destination: "http://localhost:5000/get_game_versions" },
        { source: "/dl", destination: "http://localhost:5000/dl" },
        { source: "/search", destination: "http://localhost:5000/search" },
      ],
      fallback: [],
    };
  },
};

export default nextConfig;
