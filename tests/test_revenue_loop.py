import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("revenue_loop", ROOT / "scripts" / "revenue_loop.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RevenueLoopTests(unittest.TestCase):
    def test_pct_handles_zero_denominator(self):
        self.assertEqual(module.pct(1, 0), "n/a")
        self.assertEqual(module.pct(2, 4), "50.0%")

    def test_report_has_guardrails_and_real_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            topics = tmp_path / "topics.csv"
            topics.write_text(
                "topic,audience,offer_angle,proof_needed\nTest,Creators,Offer,Proof\n",
                encoding="utf-8",
            )
            metrics = tmp_path / "metrics.csv"
            metrics.write_text(
                "landing_visits,qualified_leads,product_sales,product_revenue,service_revenue\n"
                "100,10,2,58,1000\n",
                encoding="utf-8",
            )
            old_topics, old_metrics = module.TOPICS, module.METRICS
            try:
                module.TOPICS, module.METRICS = topics, metrics
                report, summary = module.build_report(module.dt.date(2026, 9, 18), "https://example.com")
            finally:
                module.TOPICS, module.METRICS = old_topics, old_metrics
            self.assertIn("Total recorded revenue | $1,058.00", report)
            self.assertIn("Human approval", report)
            self.assertIn("does not publish", report)
            self.assertIn("Test", report)
            self.assertIn("Recorded revenue: **$1,058.00**", summary)


if __name__ == "__main__":
    unittest.main()
