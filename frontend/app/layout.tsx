import "./globals.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";

import { appConfig } from "@/lib/env";

export const metadata: Metadata = {
  title: appConfig.appName,
  description: "AI-powered Local SEO SaaS platform"
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
