import type { Metadata } from "next";
import "./globals.css";

const title = "RA Downloader";
const description = "Buscá y descargá ROMs compatibles con RetroAchievements por nombre o hash.";

export const metadata: Metadata = {
  metadataBase: new URL("https://retroachievements.vercel.app"),
  title,
  description,
  openGraph: {
    title,
    description,
    siteName: title,
    type: "website",
    locale: "es_ES",
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
