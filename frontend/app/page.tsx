"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { getAccessToken } from "@/lib/auth"
import { Spinner } from "@/components/ui/spinner"

export default function HomePage(): JSX.Element {
  const router = useRouter()

  useEffect(() => {
    const token = getAccessToken()
    if (token) {
      router.replace("/dashboard")
    } else {
      router.replace("/login")
    }
  }, [router])

  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center">
      <Spinner size="lg" />
    </div>
  )
}
