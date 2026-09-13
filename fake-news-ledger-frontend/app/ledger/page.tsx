"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import StatusBadge from "@/components/StatusBadge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Ledger() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/verify`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : data.items || data.verifications || []))
      .catch(console.error);
  }, []);

  const filtered = rows.filter(x =>
    `${x.id} ${x.claim}`.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <main className="container py-10">
      <h1 className="text-3xl font-bold">Verification Ledger</h1>
      <p className="muted mt-2">Search the live evidence-based verification records.</p>

      <input
        value={q}
        onChange={e => setQ(e.target.value)}
        placeholder="Search verification ID or claim..."
        className="mt-7 w-full rounded-xl border border-slate-700 bg-slate-950 p-4 outline-none"
      />

      <div className="card mt-5 overflow-hidden">
        <div className="hidden grid-cols-[140px_1fr_130px_140px] gap-4 border-b border-slate-800 p-4 text-xs text-slate-500 md:grid">
          <span>ID</span><span>Claim</span><span>Assessment</span><span>Blockchain</span>
        </div>

        {filtered.map(x => (
          <Link
            href={`/results/${x.id}`}
            key={x.id}
            className="grid gap-2 border-b border-slate-800 p-4 hover:bg-slate-900 md:grid-cols-[140px_1fr_130px_140px] md:items-center"
          >
            <span className="font-mono text-sm">{x.id}</span>
            <span>{x.claim}</span>
            <StatusBadge status={x.status} />
            <span className="text-sm text-emerald-300">
              {x.transaction_hash ? "MST Testnet" : "Not recorded"}
            </span>
          </Link>
        ))}

        {!filtered.length && <p className="p-6 muted">No verification records found.</p>}
      </div>
    </main>
  );
}
