export function ScoreRing({ score, size = 80 }: { score: number | null; size?: number }): JSX.Element {
  const radius = (size - 8) / 2
  const circumference = 2 * Math.PI * radius
  const progress = score != null ? (score / 100) * circumference : 0
  const color = score == null ? "#374151" : score >= 70 ? "#22c55e" : score >= 40 ? "#eab308" : "#ef4444"

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#1f2937" strokeWidth={6} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={6}
        strokeDasharray={`${progress} ${circumference}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        fill={color}
        fontSize={size / 4}
        fontWeight="bold"
      >
        {score ?? "—"}
      </text>
    </svg>
  )
}
