"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ExternalLink, Link2 } from "lucide-react";
import TrustScore from "@/components/TrustScore";
import StatusBadge from "@/components/StatusBadge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Results() {
  const params = useParams();
  const id = String(params.id);

  const [v, setV] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_URL}/api/verify/${encodeURIComponent(id)}`);
        const data = await res.json().catch(() => null);

        if (!res.ok) {
          throw new Error(data?.detail || `Verification not found [${res.status}]`);
        }

        setV(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unable to load verification.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  if (loading) {
    return <main className="container py-20 text-center">Loading verification...</main>;
  }

  if (error || !v) {
    return (
      <main className="container py-20 text-center">
        <h1 className="text-3xl font-bold">Verification not found</h1>
        <p className="muted mt-3">{error}</p>
      </main>
    );
  }

  const explorerUrl = v.transaction_hash
    ? `https://testnet.mstscan.com/tx/${v.transaction_hash}`
    : "";

  return (
    <main className="container py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-sm text-slate-400">Verification {v.id}</div>
          <h1 className="mt-2 text-4xl font-bold">Trust assessment</h1>
        </div>
        <StatusBadge status={v.status} />
      </div>

      <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
        <div className="card p-8 flex items-center justify-center">
          <TrustScore score={v.trust_score} />
        </div>

        <div className="card p-7">
          <div className="text-sm text-slate-400">Analyzed claim</div>
          <p className="mt-3 text-xl font-semibold">{v.claim}</p>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Evidence strength", v.evidence_strength],
              ["Source reliability", v.source_reliability],
              ["AI confidence", v.ai_confidence],
              ["Community agreement", v.community_agreement],
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-xl bg-slate-950 p-4">
                <div className="text-xs text-slate-400">{label}</div>
                <div className="mt-2 text-xl font-bold">{value ?? 0}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <section className="card mt-5 p-7">
        <h2 className="text-xl font-bold">AI analysis</h2>
        <p className="muted mt-4 leading-7">{v.explanation}</p>
      </section>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <section className="card p-7">
          <h2 className="text-xl font-bold">Evidence</h2>

          <div className="mt-5 space-y-4">
            {(v.evidence || []).map((e: any, index: number) => (
              <div key={index} className="rounded-xl border border-slate-800 p-5">
                <div className="flex justify-between gap-3">
                  <span className="font-semibold">{e.type}</span>
                  <span className="text-sm text-slate-400">
                    {e.reliability}/100
                  </span>
                </div>
                <div className="mt-3 font-medium">{e.source}</div>
                <p className="muted mt-2">{e.text}</p>
                {e.url && (
                  <a
                    href={e.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-flex items-center gap-2 text-sm underline"
                  >
                    View source <ExternalLink size={14} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="card p-7">
          <h2 className="text-xl font-bold">Blockchain verification</h2>

          <div className="mt-5 space-y-4">
            {[
              ["Verification ID", v.id],
              ["Content hash", v.content_hash],
              ["Network", v.blockchain_network],
              ["Transaction hash", v.transaction_hash],
            ].map(([label, value]) => (
              <div
                key={String(label)}
                className="flex items-center justify-between gap-4 border-b border-slate-800 pb-3"
              >
                <span className="text-sm text-slate-400">{label}</span>
                <span className="max-w-[65%] break-all text-right text-sm font-medium">
                  {value || "Not available"}
                </span>
              </div>
            ))}
          </div>

          {explorerUrl && (
            <a
              href={explorerUrl}
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex items-center gap-2 underline"
            >
              <Link2 size={16} />
              View on MST Explorer
              <ExternalLink size={14} />
            </a>
          )}

          <div className="mt-4 flex items-center gap-2 rounded-xl bg-emerald-400/10 p-3 text-sm text-emerald-400">
            <Link2 size={16} />
            Verification record preserved on MST Testnet
          </div>
        </section>
      </div>
    </main>
  );
}