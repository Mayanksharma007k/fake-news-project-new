export const verification={
 id:"FL-82931",
 claim:"The government has announced ₹50,000 for every college student.",
 status:"HIGH_RISK", trustScore:23, aiConfidence:81, evidenceStrength:18, sourceReliability:25, communityAgreement:72,
 hash:"0x7a82...91bf", network:"Sepolia Testnet", timestamp:"01 Sep 2026, 7:20 PM",
 explanation:"The claim appears misleading based on the available evidence. No matching announcement was found in the identified official sources, while credible sources contradict the claim.",
 evidence:[
  {type:"CONTRADICTS",source:"Official Government Website",reliability:98,text:"No matching announcement was identified in the relevant official information."},
  {type:"SUPPORTS",source:"Unknown Blog",reliability:31,text:"The blog repeats the claim but provides no primary source or verifiable announcement."}
 ]
};
export const ledger=[
 verification,
 {id:"FL-82930",claim:"A new scholarship will double student grants.",status:"UNCERTAIN",score:54,date:"01 Sep 2026"},
 {id:"FL-82929",claim:"UPI will stop working after 10 PM.",status:"MISLEADING",score:34,date:"31 Aug 2026"},
 {id:"FL-82928",claim:"College examination dates were updated.",status:"SUPPORTED",score:91,date:"31 Aug 2026"},
 {id:"FL-82927",claim:"A viral image shows a recent flood.",status:"UNCERTAIN",score:49,date:"30 Aug 2026"}
];