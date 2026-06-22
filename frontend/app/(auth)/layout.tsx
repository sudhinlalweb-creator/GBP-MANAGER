import type { ReactNode } from "react"

export default function AuthLayout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <span className="text-[#22c55e] font-bold text-2xl tracking-tight">GBP Manager</span>
          <p className="text-gray-500 text-sm mt-1">AI-powered Local SEO Platform</p>
        </div>
        {children}
      </div>
    </div>
  )
}
