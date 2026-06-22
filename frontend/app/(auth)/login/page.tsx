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
    <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-8">
      <h1 className="text-[#f9fafb] text-xl font-semibold mb-6">Sign in</h1>
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e]"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e]"
            placeholder="••••••••"
          />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2.5 rounded-lg hover:bg-green-400 transition disabled:opacity-60"
        >
          {loading && <Spinner size="sm" />}
          Sign in
        </button>
      </form>
      <div className="mt-5 space-y-2 text-center text-sm text-gray-500">
        <p>
          <Link href="/forgot-password" className="text-[#22c55e] hover:underline">
            Forgot password?
          </Link>
        </p>
        <p>
          No account?{" "}
          <Link href="/register" className="text-[#22c55e] hover:underline">
            Sign up free
          </Link>
        </p>
      </div>
    </div>
  )
}
