import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fake News Ledger",
  description: "Verify news using evidence and a transparent ledger.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
