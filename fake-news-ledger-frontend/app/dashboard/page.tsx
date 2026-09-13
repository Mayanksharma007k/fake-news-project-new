"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import StatusBadge from "@/components/StatusBadge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Dashboard() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/api/verify`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : data.items || data.verifications || []))
      .catch(console.error);
  }, []);

  return (
    <main className="container py-10">
      <h1 className="text-3xl font-bold">Your Dashboard</h1>
      <p className="muted mt-2">Your verification and community activity.</p>

      <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Articles checked", rows.length],
          ["Community reviews", rows.reduce((n, x) => n + (x.community_agreement ? 1 : 0), 0)],
          ["Average trust score", rows.length ? Math.round(rows.reduce((n, x) => n + (x.trust_score || 0), 0) / rows.length) : 0],
          ["Blockchain records", rows.filter(x => x.transaction_hash).length],
        ].map(([label, value]) => (
          <div className="card p-5" key={String(label)}>
            <div className="muted text-sm">{label}</div>
            <div className="mt-2 text-2xl font-bold">{value}</div>
          </div>
        ))}
      </div>

      <div className="card mt-5 p-6">
        <h2 className="text-xl font-bold">Recent verifications</h2>
        <div className="mt-4 space-y-2">
          {rows.slice(0, 10).map(x => (
            <Link
              href={`/results/${x.id}`}
              key={x.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 p-4"
            >
              <span className="max-w-2xl">{x.claim}</span>
              <StatusBadge status={x.status} />
            </Link>
          ))}
          {!rows.length && <p className="muted">No verifications yet.</p>}
        </div>
      </div>
    </main>
  );
}
