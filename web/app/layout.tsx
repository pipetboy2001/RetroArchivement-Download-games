import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RA Downloader",
  description: "Buscá y descargá ROMs compatibles con RetroAchievements por nombre o hash.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
