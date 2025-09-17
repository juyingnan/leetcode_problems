import json, ast, re, sys, argparse
from typing import Any, Dict, List
import pandas as pd

# CHANGE THIS if you want a different set of rings
KEEP_RINGS = ["msit", "sdfv2", "sdf", "tdf"]

def try_parse_json(s: Any) -> Any:
    if s is None: return None
    s = str(s).strip()
    if not s: return None
    try:
        return json.loads(s)
    except Exception:
        pass
    try:
        return json.loads(s.replace("'", '"'))
    except Exception:
        pass
    try:
        return ast.literal_eval(s)
    except Exception:
        pass
    # fallback: extract first { ... } block
    try:
        start = s.find("{")
        if start != -1:
            stack = 0
            for i in range(start, len(s)):
                if s[i] == "{":
                    stack += 1
                elif s[i] == "}":
                    stack -= 1
                    if stack == 0:
                        return json.loads(s[start:i+1])
    except Exception:
        pass
    return None

def compute_default_min_from_defaultimpact(cell: Any) -> int:
    """Return integer default (0 if none). Tries to parse list/dict for MinRequestCount(s)."""
    parsed = try_parse_json(cell)
    mins = []
    if isinstance(parsed, list):
        for e in parsed:
            if isinstance(e, dict):
                for k, v in e.items():
                    if k.lower() == "minrequestcount":
                        try:
                            mins.append(int(v))
                        except Exception:
                            pass
    elif isinstance(parsed, dict):
        for k, v in parsed.items():
            if k.lower() == "minrequestcount":
                try:
                    mins.append(int(v))
                except Exception:
                    pass
    else:
        # try to extract numeric from raw string
        if cell is not None and str(cell).strip():
            m = re.search(r"\d+", str(cell))
            if m:
                try:
                    mins.append(int(m.group()))
                except Exception:
                    pass
    return max(mins) if mins else 0

def extract_ring_min_from_scope(scope_cell: Any, default_min: int) -> Dict[str,int]:
    """
    Parse the scope cell and return a dict ring -> MinRequestCount.
    If a ring has no explicit MinRequestCount, use default_min for that ring.
    """
    parsed = try_parse_json(scope_cell)
    result: Dict[str,int] = {}
    if not isinstance(parsed, dict):
        return result
    # ImpactConfigs expected; fall back to top-level lists/dicts
    impact = None
    if "ImpactConfigs" in parsed and isinstance(parsed["ImpactConfigs"], dict):
        impact = parsed["ImpactConfigs"]
    else:
        impact = {k:v for k,v in parsed.items() if isinstance(v, (list, dict))}
    if not isinstance(impact, dict):
        return result

    for ring, entries in impact.items():
        entries_list = entries if isinstance(entries, list) else [entries]
        found = []
        for e in entries_list:
            if isinstance(e, dict):
                for k,v in e.items():
                    if k.lower() == "minrequestcount":
                        try:
                            found.append(int(v))
                        except Exception:
                            pass
        result[ring] = max(found) if found else default_min
    return result

def main(inpath: str, outpath: str, sep: str):
    df = pd.read_csv(inpath, sep=sep, dtype=str, keep_default_na=False, na_values=[""])
    if "PartitionKey" not in df.columns:
        raise SystemExit("Missing PartitionKey column.")
    # prefer these column names (based on your sample)
    scope_col = "ScopeImpactConfigs" if "ScopeImpactConfigs" in df.columns else None
    default_col = "DefaultImpactConfigs" if "DefaultImpactConfigs" in df.columns else None

    # fallback heuristics
    if scope_col is None:
        # likely the 14th column in your sample (index 13)
        scope_col = df.columns[13] if len(df.columns) > 13 else df.columns[-1]
    if default_col is None:
        default_col = "DefaultImpactConfigs" if "DefaultImpactConfigs" in df.columns else (df.columns[5] if len(df.columns) > 5 else None)

    out_rows: List[Dict[str,Any]] = []
    for _, row in df.iterrows():
        pk = row.get("PartitionKey", "")
        scope_cell = row.get(scope_col, "")
        default_cell = row.get(default_col, "")
        default_min = compute_default_min_from_defaultimpact(default_cell)
        ring_map = extract_ring_min_from_scope(scope_cell, default_min)

        # For each ring we care about, include a row only if that ring appears in the scope
        for ring in KEEP_RINGS:
            if ring not in ring_map:
                continue
            minval = ring_map[ring]
            out_rows.append({
                "PartitionKey": pk,
                "Ring": ring,
                "MinRequestCount": int(minval),
                "DefaultMinRequestCount": int(default_min)
            })

    out_df = pd.DataFrame(out_rows, columns=["PartitionKey", "Ring", "MinRequestCount", "DefaultMinRequestCount"])
    out_df.to_csv(outpath, index=False)
    print(f"Wrote {len(out_df)} rows to {outpath}")

if __name__ == "__main__":
    INPUT_CSV = r"C:\Users\yingnanju\Downloads\ImpactConfig.csv"
    OUTPUT_CSV = r"C:\Users\yingnanju\Downloads\output_min_request_counts.csv"
    main(INPUT_CSV, OUTPUT_CSV, sep=",")
