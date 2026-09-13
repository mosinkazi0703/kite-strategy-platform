def summarize(trades):
    resolved=[t for t in trades if t.get("pnl") is not None]; pnls=[t["pnl"] for t in resolved]
    gross=sum(pnls); wins=[p for p in pnls if p>0]; losses=[p for p in pnls if p<0]
    return {"trade_count":len(resolved),"unresolved_count":len(trades)-len(resolved),"gross_pnl":gross,"win_rate":len(wins)/len(pnls) if pnls else 0,"profit_factor":sum(wins)/abs(sum(losses)) if losses else None}
