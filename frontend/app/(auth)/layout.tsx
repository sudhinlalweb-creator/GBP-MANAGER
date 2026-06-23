import type { ReactNode } from "react"

export default function AuthLayout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div style={{ minHeight: "100vh", background: "var(--canvas)", display: "flex", alignItems: "center", justifyContent: "center", padding: 16, fontFamily: "'Inter', ui-sans-serif, system-ui, sans-serif" }}>
      {children}
    </div>
  )
}
