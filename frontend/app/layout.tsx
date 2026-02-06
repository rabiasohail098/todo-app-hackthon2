'use client';

import "./globals.css";
import { AppWrapper, useApp } from "@/context/AppContext";

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
        className="font-sans antialiased min-h-screen"
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
