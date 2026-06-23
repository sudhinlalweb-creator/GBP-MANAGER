"use client"

import { useCallback, useRef, useState } from "react"

type Dot = { el?: HTMLDivElement; r: number; c: number; dist: number; rank: number }

function colorRank(rank: number) {
  if (rank <= 3) return { bg: "#0bdf50", fg: "#06351a" }
  if (rank <= 7) return { bg: "#f59e0b", fg: "#4a2e00" }
  return { bg: "#c41c1c", fg: "#fff" }
}

export function RankTracker() {
  const [avgRank, setAvgRank] = useState("2.3")
  const [scanning, setScanning] = useState(false)
  const keywordRef = useRef<HTMLInputElement>(null)
  const dotsRef = useRef<Dot[]>([])
  const gridRef = useRef<HTMLDivElement>(null)

  const buildGrid = useCallback((initial = false) => {
    const wrap = gridRef.current
    if (!wrap) return
    wrap.innerHTML = ""
    dotsRef.current = []
    const N = 5, ctr = 2
    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const cell = document.createElement("div")
        cell.style.cssText = "display:flex;align-items:center;justify-content:center;position:relative"
        if (r === ctr && c === ctr) {
          cell.innerHTML =
            '<span style="position:absolute;width:42px;height:42px;border-radius:50%;background:rgba(17,17,17,.16);animation:pinly-ping 2.4s ease-out infinite"></span>' +
            '<span style="position:relative;width:42px;height:42px;border-radius:50%;background:#111;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 8px rgba(17,17,17,.32);border:2.5px solid #fff">' +
            '<svg width="21" height="21" viewBox="0 0 24 24" fill="none"><path d="M12 22s7-6.16 7-12A7 7 0 0 0 5 10c0 5.84 7 12 7 12Z" fill="#fff"/><circle cx="12" cy="10" r="2.6" fill="#111"/></svg></span>'
          wrap.appendChild(cell)
          continue
        }
        const dist = Math.sqrt((r - ctr) ** 2 + (c - ctr) ** 2)
        const dot = document.createElement("div")
        dot.style.cssText = "width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;background:#fff;color:#c2c5c0;border:2px solid #fff;box-shadow:0 1px 3px rgba(17,17,17,.16);transition:transform .18s ease"
        const rank = Math.max(1, Math.round(Math.pow(dist, 1.7) * 1.35))
        const entry: Dot = { el: dot, r, c, dist, rank }
        dotsRef.current.push(entry)
        if (initial) {
          const col = colorRank(rank)
          dot.style.background = col.bg
          dot.style.color = col.fg
          dot.textContent = String(rank)
        }
        cell.appendChild(dot)
        wrap.appendChild(cell)
      }
    }
    if (initial) {
      const central = dotsRef.current.filter(d => d.dist <= 1.45)
      const mean = central.reduce((s, d) => s + d.rank, 0) / central.length
      setAvgRank(mean.toFixed(1))
    }
  }, [])

  const gridRefCallback = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      gridRef.current = node
      buildGrid(true)
    }
  }, [buildGrid])

  const runScan = useCallback(() => {
    if (scanning) return
    setScanning(true)
    const dots = dotsRef.current
    for (const d of dots) {
      d.rank = Math.max(1, Math.round(Math.pow(d.dist, 1.7) * 1.35 + (Math.random() * 1.5 - 0.6)))
      if (d.el) { d.el.style.background = "#fff"; d.el.style.color = "#c2c5c0"; d.el.textContent = "" }
    }
    const order = dots.map((_, i) => i).sort(() => Math.random() - 0.5)
    let i = 0
    const step = () => {
      if (i >= order.length) {
        const central = dots.filter(d => d.dist <= 1.45)
        const mean = central.reduce((s, d) => s + d.rank, 0) / central.length
        setAvgRank(mean.toFixed(1))
        setScanning(false)
        return
      }
      const d = dots[order[i]]
      if (d.el) {
        const col = colorRank(d.rank)
        d.el.style.background = col.bg
        d.el.style.color = col.fg
        d.el.textContent = String(d.rank)
        d.el.style.transform = "scale(1.18)"
        setTimeout(() => { if (d.el) d.el.style.transform = "scale(1)" }, 220)
      }
      i++
      setTimeout(step, 26)
    }
    step()
  }, [scanning])

  return (
    <section style={{ maxWidth: 1200, margin: "0 auto", padding: "64px 24px 0" }}>
      <div style={{ maxWidth: 680, marginBottom: 40 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#ff5600", marginBottom: 14 }}>Rank tracker</div>
        <h2 style={{ fontSize: "clamp(28px,4vw,42px)", lineHeight: 1.1, letterSpacing: "-1.2px", fontWeight: 600 }}>
          See where you rank. Everywhere that matters.
        </h2>
        <p style={{ fontSize: 17, lineHeight: 1.5, color: "#626260", marginTop: 16 }}>
          Track your local search rankings on a geo-grid. Each point shows your position for a keyword in that exact spot.
        </p>
      </div>

      <div style={{ background: "#fff", border: "1px solid #d3cec6", borderRadius: 16, padding: 28 }}>
        <div style={{ display: "flex", gap: 10, marginBottom: 22, flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#7b7b78", display: "inline-flex", alignItems: "center", gap: 7 }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9c9fa5" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 21s7-6.16 7-12A7 7 0 0 0 5 9c0 5.84 7 12 7 12Z"/><circle cx="12" cy="9" r="2.4"/>
            </svg>
            Tracking
          </span>
          <input
            ref={keywordRef}
            type="text"
            defaultValue="dentist near me"
            onKeyDown={(e) => e.key === "Enter" && runScan()}
            style={{ flex: 1, minWidth: 200, background: "#f5f1ec", border: "1px solid #d3cec6", borderRadius: 8, padding: "11px 14px", fontSize: 15, fontFamily: "inherit", color: "#111", outline: "none" }}
          />
          <button
            onClick={runScan}
            disabled={scanning}
            style={{ background: "#111", color: "#fff", fontSize: 15, fontWeight: 500, padding: "11px 20px", borderRadius: 8, border: "none", cursor: scanning ? "not-allowed" : "pointer", display: "inline-flex", alignItems: "center", gap: 8, opacity: scanning ? 0.7 : 1 }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              style={scanning ? { animation: "pinly-spin .8s linear infinite" } : {}}>
              {scanning
                ? <path d="M21 12a9 9 0 1 1-6.2-8.5" />
                : <><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></>}
            </svg>
            {scanning ? "Scanning" : "Scan grid"}
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 28, alignItems: "stretch" }}>
          {/* Map + grid */}
          <div style={{ position: "relative", width: "100%", aspectRatio: "1.6/1", borderRadius: 12, overflow: "hidden", border: "1px solid #e3ddd4", background: "#eef0ec" }}>
            <svg viewBox="0 0 520 356" preserveAspectRatio="xMidYMid slice" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
              <rect width="520" height="356" fill="#eceee9"/>
              <rect x="34" y="210" width="170" height="118" rx="8" fill="#e3eadd"/>
              <path d="M280 0 V356 M0 178 H520" stroke="#fbfcfb" strokeWidth="20"/>
              <path d="M280 0 V356 M0 178 H520" stroke="#dfe3da" strokeWidth="1"/>
              <path d="M104 0 V356 M440 0 V356 M0 62 H520 M0 294 H520" stroke="#f6f7f4" strokeWidth="11"/>
              <path d="M104 0 V356 M440 0 V356 M0 62 H520 M0 294 H520" stroke="#e4e7df" strokeWidth="0.8"/>
              <path d="M0 52 L224 178 L134 356" fill="none" stroke="#f6f7f4" strokeWidth="9"/>
              <path d="M0 52 L224 178 L134 356" fill="none" stroke="#e4e7df" strokeWidth="0.8"/>
              <path d="M340 0 L520 150" fill="none" stroke="#e7f0fa" strokeWidth="22" strokeLinecap="round"/>
            </svg>
            <div ref={gridRefCallback} style={{ position: "absolute", inset: 0, display: "grid", gridTemplateColumns: "repeat(5,1fr)", gridTemplateRows: "repeat(5,1fr)", placeItems: "center", padding: "34px 56px" }} />
          </div>

          {/* Stats panel */}
          <div style={{ background: "#f7f4ef", border: "1px solid #ebe7e1", borderRadius: 12, padding: "30px 26px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 24 }}>
            <div>
              <div style={{ fontSize: 13, color: "#7b7b78", marginBottom: 7 }}>Your average rank</div>
              <div style={{ fontSize: 58, fontWeight: 600, letterSpacing: "-2.2px", lineHeight: 1 }}>{avgRank}</div>
              <div style={{ fontSize: 13.5, color: "#626260", marginTop: 6 }}>within 1&nbsp;km radius</div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 13, fontSize: 13.5, color: "#626260", borderTop: "1px solid #e3ddd4", paddingTop: 22 }}>
              {[
                { color: "#0bdf50", label: "Rank 1–3 · top of map pack" },
                { color: "#f59e0b", label: "Rank 4–7 · page one" },
                { color: "#c41c1c", label: "Rank 8+ · invisible" },
              ].map(({ color, label }) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ width: 13, height: 13, borderRadius: "50%", background: color, display: "inline-block", flexShrink: 0 }} />
                  {label}
                </div>
              ))}
            </div>
            <div style={{ fontSize: 12, color: "#9c9fa5" }}>Sampled across 24 grid points · 2 km²</div>
          </div>
        </div>
      </div>
    </section>
  )
}
