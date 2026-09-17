#!/usr/bin/env python3
"""Generate a reviewable, ethical revenue-operations pack.

This script never publishes, sends outreach, opens accounts, or moves money.
It turns owned inputs (topics and metrics) into a dated plan and diagnostics.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "automation" / "topics.csv"
METRICS = ROOT / "automation" / "metrics.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(n: float, d: float) -> str:
    return f"{(n / d * 100):.1f}%" if d else "n/a"


def money(n: float) -> str:
    return f"${n:,.2f}"


def build_report(run_date: dt.date, site_url: str) -> tuple[str, str]:
    topics = read_csv(TOPICS)
    metrics = read_csv(METRICS)
    selected = topics[:5]

    visits = sum(float(r.get("landing_visits", 0) or 0) for r in metrics)
    leads = sum(float(r.get("qualified_leads", 0) or 0) for r in metrics)
    sales = sum(float(r.get("product_sales", 0) or 0) for r in metrics)
    product_revenue = sum(float(r.get("product_revenue", 0) or 0) for r in metrics)
    service_revenue = sum(float(r.get("service_revenue", 0) or 0) for r in metrics)
    revenue = product_revenue + service_revenue

    rows = "\n".join(
        f"| {html.escape(t.get('topic', ''))} | {html.escape(t.get('audience', ''))} | "
        f"{html.escape(t.get('offer_angle', ''))} | {html.escape(t.get('proof_needed', ''))} |"
        for t in selected
    ) or "| Add topics in `automation/topics.csv` | | | |"

    report = f"""# Revenue Loop Report — {run_date.isoformat()}

> **Status: review required.** This report is an execution aid, not a promise of earnings. It does not publish content, send outreach, open payment accounts, or provide financial advice.

## Funnel snapshot

| Metric | Value |
|---|---:|
| Landing-page visits | {visits:.0f} |
| Qualified leads | {leads:.0f} |
| Product sales | {sales:.0f} |
| Product revenue | {money(product_revenue)} |
| Service revenue | {money(service_revenue)} |
| Total recorded revenue | {money(revenue)} |
| Visit → lead rate | {pct(leads, visits)} |
| Visit → sale rate | {pct(sales, visits)} |
| Lead → sale rate | {pct(sales, leads)} |

## This cycle's content and offer angles

| Topic | Audience | Offer angle | Proof needed |
|---|---|---|---|
{rows}

## Human execution checklist

**Human approval is required before publication, outreach, or any commercial action.**

- [ ] Select one topic and add a real source, example, or customer observation.
- [ ] Produce one useful long-form asset and repurpose it with the existing prompt pack.
- [ ] Review every claim, disclosure, and link before publication.
- [ ] Publish only on channels you control and comply with their policies.
- [ ] Send no bulk or unsolicited outreach; personalize and honor opt-outs.
- [ ] Log actual outcomes in `automation/metrics.csv`.
- [ ] If a paid offer is used, confirm price, scope, taxes, refund terms, and fulfillment capacity.

## Guardrails

- No fake scarcity, fake testimonials, impersonation, spam, engagement manipulation, or outcome guarantees.
- No personalized investment, legal, medical, or tax advice.
- AI output requires human fact-checking and meaningful editing before release.
- Affiliate or sponsored relationships require clear disclosure.

## Funnel URL

{site_url or '(set SITE_URL in repository variables for a live check)'}

## Next decision

If this cycle produces at least one qualified lead or one sale, repeat the angle with stronger proof. If it produces attention but no leads after three cycles, change the offer or call to action rather than increasing volume.
"""

    summary = (
        f"## Revenue Loop — {run_date.isoformat()}\n"
        f"Recorded revenue: **{money(revenue)}** · Qualified leads: **{leads:.0f}** · "
        f"Visit→lead: **{pct(leads, visits)}**\n\n"
        "Human approval is required before publication or outreach."
    )
    return report, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="reports")
    parser.add_argument("--site-url", default=os.getenv("SITE_URL", ""))
    args = parser.parse_args()
    run_date = dt.datetime.now(dt.timezone.utc).date()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    report, summary = build_report(run_date, args.site_url)
    report_path = out / f"revenue-loop-{run_date.isoformat()}.md"
    report_path.write_text(report, encoding="utf-8")
    print(summary)
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
