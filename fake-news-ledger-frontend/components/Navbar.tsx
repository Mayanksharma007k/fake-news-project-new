import Link from "next/link";
import { ShieldCheck, Menu, Wallet } from "lucide-react";
export default function Navbar(){
 return <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#070b12]/90 backdrop-blur">
  <div className="container flex h-16 items-center justify-between">
   <Link href="/" className="flex items-center gap-2 font-bold"><span className="rounded-xl bg-white p-2 text-slate-950"><ShieldCheck size={18}/></span>Fake News Ledger</Link>
   <nav className="hidden gap-7 text-sm text-slate-300 md:flex"><Link href="/verify">Verify</Link><Link href="/ledger">Ledger</Link><Link href="/dashboard">Dashboard</Link></nav>
   <button className="hidden items-center gap-2 rounded-xl border border-slate-700 px-3 py-2 text-sm md:flex"><Wallet size={16}/> Connect Wallet</button>
   <button className="rounded-xl border border-slate-700 p-2 md:hidden"><Menu size={18}/></button>
  </div>
 </header>
}