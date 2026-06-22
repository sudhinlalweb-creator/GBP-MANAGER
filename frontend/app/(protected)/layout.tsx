"use client"

import { useEffect, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { Sidebar } from "@/components/layout/sidebar"
import { Spinner } from "@/components/ui/spinner"

export default function ProtectedLayout({ children }: { children: ReactNode }): JSX.Element {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login")
    }
  }, [isLoading, user, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!user) return <></>

  return (
    <div className="flex min-h-screen bg-[#030712] text-[#f9fafb]">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  )
}
