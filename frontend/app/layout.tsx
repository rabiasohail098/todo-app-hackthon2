'use client';

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppWrapper, useApp } from "@/context/AppContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

function RootLayoutContent({ children }: { children: React.ReactNode }) {
  const { language } = useApp();

  return (
    <html
      lang={language === 'ur' ? 'ur' : 'en'}
      dir={language === 'ur' ? 'rtl' : 'ltr'}
      suppressHydrationWarning
    >
      <head>
        <title>Todo App</title>
        <meta name="description" content="A beautiful and functional todo application with theme support" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AppWrapper>
      <RootLayoutContent>{children}</RootLayoutContent>
    </AppWrapper>
  );
}
