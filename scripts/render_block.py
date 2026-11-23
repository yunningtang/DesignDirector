#!/usr/bin/env python3
"""Render config/defaults.json as the 'Default looks to avoid' block (markdown)."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(R, "config/defaults.json"), encoding="utf-8"))
out = [f"## Default looks to avoid — {d['version']}", "",
       "Pages built by models cluster around a few looks whatever the subject. Each item below is a **combination**; any single ingredient on its own (a serif headline, square corners, a grey background, a rounded button) is fine. Where the brief leaves the look open, do not land on one of these combinations:", ""]
for i, it in enumerate(d["items"], 1):
    out.append(f"{i}. **{it['name']}.** {it['text']}" + (" (Never, unless the brief names it.)" if it["tier"] == "floor" else ""))
out += ["", "The brief's own words always win: if it asks for one of these (a newspaper-style story, a dark terminal, a named font), follow it. A subject that feels warm, bookish, calm, friendly or child-facing is not such a request.",
        "", "Check pass: at 375×812 `document.documentElement.scrollWidth` must be ≤ 375 (fix the overflowing element; never hide overflow on body/html). Go through the items against your screenshots and computed styles; for each hit, change it or record in meta.json why the brief calls for it (`default_hits`)."]
print("\n".join(out))
