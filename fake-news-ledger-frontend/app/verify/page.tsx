"use client";

import { useState } from "react";
import { ArrowRight, FileText, Link2, Loader2, Search } from "lucide-react";
import { useRouter } from "next/navigation";

const API_URL = "http://127.0.0.1:8000";

export default function Verify() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function analyze() {
    if (!input.trim()) return;
    setLoading(true);

    try {
      // Check if the user entered a URL or a text claim
      const isUrl = input.trim().startsWith("http://") || input.trim().startsWith("https://");
      
      const payload = isUrl 
        ? { claim: "", url: input.trim() } 
        : { claim: input.trim() };

      // Send the request to your FastAPI backend
      const response = await fetch(`${API_URL}/api/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to reach backend");
      }

      const data = await response.json();
      
      // Redirect to the real database-generated ID
      router.push(`/results/${data.id}`);

    } catch (error) {
      console.error(error);
      alert("Failed to connect to the backend server.");
      setLoading(false);
    }
  }

  return (
    <main className="container min-h-[calc(100vh-64px)] py-16">
      <div className="mx-auto max-w-3xl">
        
        <div className="mb-10 text-center">
          <div className="mx-auto w-fit rounded-xl border border-slate-700 p-3">
            <Search />
          </div>
          <h1 className="mt-5 text-4xl font-bold">Verify a news story</h1>
          <p className="muted mt-3">
            Paste a URL, headline, or claim and let the evidence guide the assessment.
          </p>
        </div>

        <div className="card p-5">
          <label className="mb-3 block text-sm font-medium">News URL or claim</label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={6}
            placeholder="e.g. Paste a news URL or type a claim..."
            className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 p-4 outline-none focus:border-slate-400"
          />
          
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <button
              onClick={() => setInput("The government has announced ₹50,000 for every college student.")}
              className="text-sm text-slate-400 underline"
            >
              Use example claim
            </button>
            
            <button
              onClick={analyze}
              disabled={loading || !input.trim()}
              className="flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={16} />
                  Analyzing...
                </>
              ) : (
                <>
                  Analyze News <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {[
            [FileText, "Claim extraction"],
            [Search, "Evidence search"],
            [Link2, "Ledger record"],
          ].map(([Icon, text]: any) => (
            <div className="card p-4" key={text}>
              <Icon size={18} />
              <div className="mt-3 text-sm font-semibold">{text}</div>
            </div>
          ))}
        </div>
        
      </div>
    </main>
  );
}