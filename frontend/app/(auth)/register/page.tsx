"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useAuth } from "@/contexts/auth-context"
import { Spinner } from "@/components/ui/spinner"

export default function RegisterPage(): JSX.Element {
  const { register } = useAuth()
  const [form, setForm] = useState({ full_name: "", email: "", password: "", org_name: "" })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [key]: e.target.value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await register(form.email, form.password, form.full_name, form.org_name)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-8">
      <h1 className="text-[#f9fafb] text-xl font-semibold mb-6">Create account</h1>
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        {[
          { key: "full_name" as const, label: "Full name", type: "text", placeholder: "Jane Smith" },
          { key: "email" as const, label: "Email", type: "email", placeholder: "you@example.com" },
          { key: "password" as const, label: "Password", type: "password", placeholder: "••••••••" },
          { key: "org_name" as const, label: "Organization name", type: "text", placeholder: "Acme SEO" },
        ].map(({ key, label, type, placeholder }) => (
          <div key={key}>
            <label className="block text-sm text-gray-400 mb-1">{label}</label>
            <input
              type={type}
              required
              value={form[key]}
              onChange={set(key)}
              placeholder={placeholder}
              className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e]"
            />
          </div>
        ))}
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2.5 rounded-lg hover:bg-green-400 transition disabled:opacity-60"
        >
          {loading && <Spinner size="sm" />}
          Create account
        </button>
      </form>
      <p className="mt-5 text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link href="/login" className="text-[#22c55e] hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  )
}
