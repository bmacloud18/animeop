import type { Metadata } from "next";
import { Inter, Archivo_Black } from "next/font/google";
import "./globals.css";
import "./animeop.css";

const inter = Inter({ subsets: ["latin"] });
const archivo = Archivo_Black({
  subsets: ["latin"],
  weight: "400"
});

export const metadata: Metadata = {
  title: "AnimeOP",
  description: "Anime OP/ED Channel",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      
      <body className={`bg-gradient-radial from-blue to-purple`}>{children}</body>
    </html>
  );
}
