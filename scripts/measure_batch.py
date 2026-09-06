"""Run the chest anatomy adapter over converted packages and summarise CTR. Usage: python scripts/measure_batch.py vindr [limit]"""
import json, sys, time, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from oip.anatomy import measure_chest
name = sys.argv[1] if len(sys.argv) > 1 else "vindr"; limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
pkgs = sorted((ROOT / "data/oip" / name).glob("*.oip"))[:limit]
res = []; t0 = time.time()
for i, p in enumerate(pkgs, 1):
    try:
        r = measure_chest(p); r["pkg"] = p.name; res.append(r)
    except Exception as e:
        res.append({"pkg": p.name, "error": f"{type(e).__name__}: {str(e)[:150]}"})
    if i % 10 == 0: print(f"  {i}/{len(pkgs)} ({(time.time()-t0)/i:.1f} s/img)", flush=True)
ctrs = [r["ctr"] for r in res if r.get("ctr")]
out = {"dataset": name, "n": len(res), "with_ctr": len(ctrs), "errors": sum(1 for r in res if "error" in r),
       "ctr_median": statistics.median(ctrs) if ctrs else None, "ctr_p10": sorted(ctrs)[len(ctrs)//10] if ctrs else None, "ctr_p90": sorted(ctrs)[9*len(ctrs)//10] if ctrs else None,
       "ctr_gt_0_5": sum(c > 0.5 for c in ctrs), "laterality_notes": sum(1 for r in res if r.get("notes")), "seconds_per_image": round((time.time()-t0)/max(len(res),1), 2), "results": res}
(ROOT / "data/oip" / name / "_measure.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "results"}, indent=1))
for r in [r for r in res if "error" in r][:3]: print("ERR", r)
