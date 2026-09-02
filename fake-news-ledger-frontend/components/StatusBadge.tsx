type Props={status:string};
export default function StatusBadge({status}:Props){
 const map:any={SUPPORTED:["Supported","bg-emerald-400/10 text-emerald-300 border-emerald-400/20"],UNCERTAIN:["Uncertain","bg-amber-400/10 text-amber-300 border-amber-400/20"],MISLEADING:["Misleading","bg-orange-400/10 text-orange-300 border-orange-400/20"],HIGH_RISK:["High Risk","bg-red-400/10 text-red-300 border-red-400/20"]};
 const [label,cls]=map[status]||map.UNCERTAIN;
 return <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${cls}`}>{label}</span>
}