import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import { SiteNav } from "@/components/site-nav";
import "./globals.css";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Viral Content Agent",
  description: "Phase 1 scaffold for on-demand TikTok and YouTube Shorts search.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="noise text-white antialiased">
        <Providers>
          <div className="min-h-screen">
            <SiteNav />
            <main>{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
