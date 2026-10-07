import csv
from pathlib import Path

from cfadvisers import pitchbook
from cfadvisers.store import Store

FIX = Path(__file__).parent / "fixtures"


def test_parse_advisers():
    got = pitchbook.parse_advisers("Alpha CF Ltd (Advisor: General), Smith & Co LLP (Legal Advisor), Foo (Bar, Baz)")
    assert got == [("Alpha CF Ltd", "Advisor: General"), ("Smith & Co LLP", "Legal Advisor"), ("Foo", "Bar, Baz")]


def test_import(tmp_path):
    f = tmp_path / "deals.csv"
    with open(f, "w", newline="") as fh:
        fh.write("PitchBook export\nDownloaded 2026\n")
        w = csv.writer(fh)
        w.writerow(["Deal ID", "Companies", "Deal Date", "Deal Size", "EBITDA", "Service Providers"])
        w.writerow(["1", "Widgets Ltd", "2025-03-01", "8", "1.2", "Alpha Corporate Finance (Advisor: General), Pinsent Masons (Legal Advisor)"])
        w.writerow(["2", "Gadgets Ltd", "2024-01-01", "30", "", "Alpha CF Limited (Advisor: General), New Boutique LLP (Advisor: General)"])
    stats, unmatched = pitchbook.import_export(f, Store(FIX).rows, 5)
    a = stats["advisers"]["alphacf-co-uk"]
    assert a["deals"] == 2 and a["deals_in_sme_band"] == 1 and a["last_deal"] == "2025-03-01"
    assert [u["name"] for u in unmatched] == ["New Boutique LLP"]
