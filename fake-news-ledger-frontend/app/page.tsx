import Link from "next/link"; import {ArrowRight, BrainCircuit, Link2, SearchCheck, ShieldCheck} from "lucide-react";
export default function Home(){return <main className="grid-bg min-h-screen">
 <section className="container py-24 text-center md:py-32">
  <div className="mx-auto mb-6 flex w-fit items-center gap-2 rounded-full border border-slate-700 bg-slate-900/60 px-4 py-2 text-xs text-slate-300"><ShieldCheck size={14}/> Evidence-based news verification</div>
  <h1 className="mx-auto max-w-4xl text-5xl font-black tracking-tight md:text-7xl">Can you trust what you read?</h1>
  <p className="muted mx-auto mt-6 max-w-2xl text-lg">AI analyzes the story. Evidence explains it. Blockchain preserves the verification trail.</p>
  <div className="mt-9 flex justify-center gap-3"><Link href="/verify" className="flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-slate-950">Verify a News Story <ArrowRight size={17}/></Link><Link href="/ledger" className="rounded-xl border border-slate-700 px-5 py-3 font-semibold">Explore Ledger</Link></div>
 </section>
 <section className="container grid gap-5 pb-24 md:grid-cols-3">
  {[[BrainCircuit,"AI Analysis","Extract claims and explain why evidence supports or contradicts them."],[SearchCheck,"Evidence First","See source reliability, supporting evidence and conflicts."],[Link2,"Blockchain Trail","Preserve a tamper-evident verification record."]].map(([Icon,title,desc]:any)=><div className="card p-6" key={title}><Icon size={25}/><h3 className="mt-5 text-lg font-bold">{title}</h3><p className="muted mt-2 text-sm leading-6">{desc}</p></div>)}
 </section>
</main>}