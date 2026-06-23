"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"

export default function LoginPage(): JSX.Element {
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--hairline)", borderRadius: 16, padding: "36px 32px", width: "100%", maxWidth: 400 }}>
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
        <div style={{ width: 32, height: 32, borderRadius: 9, background: "var(--ink)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--canvas)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M9 21v-6h6v6"/></svg>
        </div>
        <span style={{ fontSize: 17, fontWeight: 600, color: "var(--ink)", letterSpacing: "-0.3px" }}>GBP Manager</span>
      </div>

      <h1 style={{ fontSize: 20, fontWeight: 600, color: "var(--ink)", marginBottom: 4, letterSpacing: "-0.3px" }}>Welcome back</h1>
      <p style={{ fontSize: 14, color: "var(--ink-muted)", marginBottom: 24 }}>Sign in to your account to continue</p>

      <form onSubmit={(e) => void handleSubmit(e)} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <label style={{ display: "block", fontSize: 13.5, fontWeight: 500, color: "var(--ink)", marginBottom: 6 }}>Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            style={{ width: "100%", fontFamily: "inherit", fontSize: 14, color: "var(--ink)", background: "var(--canvas)", border: "1px solid var(--hairline)", borderRadius: 8, padding: "9px 12px", outline: "none", boxSizing: "border-box" }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: 13.5, fontWeight: 500, color: "var(--ink)", marginBottom: 6 }}>Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            style={{ width: "100%", fontFamily: "inherit", fontSize: 14, color: "var(--ink)", background: "var(--canvas)", border: "1px solid var(--hairline)", borderRadius: 8, padding: "9px 12px", outline: "none", boxSizing: "border-box" }}
          />
        </div>

        {error && (
          <p style={{ fontSize: 13.5, color: "#dc2626", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: "8px 12px" }}>{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: "var(--btn-bg)", color: "var(--btn-fg)", border: "none", borderRadius: 8, padding: "10px 0", fontFamily: "inherit", fontSize: 14.5, fontWeight: 500, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.65 : 1, marginTop: 2 }}
        >
          {loading && <Spinner size="sm" />}
          Sign in
        </button>
      </form>

      <div style={{ marginTop: 20, textAlign: "center", fontSize: 13.5, color: "var(--ink-muted)", display: "flex", flexDirection: "column", gap: 6 }}>
        <Link href="/forgot-password" style={{ color: "var(--fin)", textDecoration: "none" }}>Forgot password?</Link>
        <span>No account? <Link href="/register" style={{ color: "var(--fin)", textDecoration: "none", fontWeight: 500 }}>Sign up free</Link></span>
      </div>
    </div>
  )
}
