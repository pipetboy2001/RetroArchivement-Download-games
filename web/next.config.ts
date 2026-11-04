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
  // En producción, Vercel Services rutea /api/*, /get_game_versions y /dl
  // directo al servicio Flask antes de que Next.js los vea (ver vercel.json
  // en la raíz) -- estos rewrites nunca se ejecutan ahí. Solo sirven para
  // `npm run dev`, donde Flask corre aparte en localhost:5000 (ver
  // package.json de la raíz: dev:api / dev:web / dev).
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return [
      { source: "/api/:path*", destination: "http://localhost:5000/api/:path*" },
      { source: "/get_game_versions", destination: "http://localhost:5000/get_game_versions" },
      { source: "/dl", destination: "http://localhost:5000/dl" },
    ];
  },
};

export default nextConfig;
