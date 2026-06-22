"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { apiForgotPassword } from "@/lib/auth"
import { Spinner } from "@/components/ui/spinner"

export default function ForgotPasswordPage(): JSX.Element {
  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    await apiForgotPassword(email).catch(() => {})
    setSent(true)
    setLoading(false)
  }

  return (
    <div className="bg-[#0b1220] border border-[#1f2937] rounded-xl p-8">
      <h1 className="text-[#f9fafb] text-xl font-semibold mb-2">Reset password</h1>
      {sent ? (
        <div className="space-y-4">
          <p className="text-gray-400 text-sm">
            If an account exists for <strong className="text-[#f9fafb]">{email}</strong>, you will
            receive a reset link shortly.
          </p>
          <Link href="/login" className="block text-center text-sm text-[#22c55e] hover:underline">
            Back to sign in
          </Link>
        </div>
      ) : (
        <>
          <p className="text-gray-400 text-sm mb-6">
            Enter your email and we&apos;ll send you a reset link.
          </p>
          <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full bg-[#030712] border border-[#1f2937] rounded-lg px-3 py-2 text-[#f9fafb] text-sm focus:outline-none focus:border-[#22c55e]"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-[#22c55e] text-black font-semibold px-4 py-2.5 rounded-lg hover:bg-green-400 transition disabled:opacity-60"
            >
              {loading && <Spinner size="sm" />}
              Send reset link
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-500">
            <Link href="/login" className="text-[#22c55e] hover:underline">
              Back to sign in
            </Link>
          </p>
        </>
      )}
    </div>
  )
}
