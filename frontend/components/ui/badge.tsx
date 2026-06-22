type Variant = "green" | "yellow" | "red" | "gray" | "blue"

const variants: Record<Variant, string> = {
  green: "bg-green-900/40 text-green-400 border border-green-800",
  yellow: "bg-yellow-900/40 text-yellow-400 border border-yellow-800",
  red: "bg-red-900/40 text-red-400 border border-red-800",
  gray: "bg-gray-800 text-gray-400 border border-gray-700",
  blue: "bg-blue-900/40 text-blue-400 border border-blue-800",
}

export function Badge({
  children,
  variant = "gray",
}: {
  children: React.ReactNode
  variant?: Variant
}): JSX.Element {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  )
}

export function planBadgeVariant(plan: string): Variant {
  if (plan === "agency") return "blue"
  if (plan === "pro") return "green"
  if (plan === "starter") return "yellow"
  return "gray"
}
