from pathlib import Path

from cfadvisers import model, store
from cfadvisers.store import Store

FIX = Path(__file__).parent / "fixtures"


def s():
    return Store(FIX, multiple=5)


def test_normalise_cleans_and_derives():
    r = s().get("alphacf-co-uk")
    assert r["website"] == "https://alphacf.co.uk"
    assert r["contact_email"] == "info@alphacf.co.uk"
    assert r["sectors"] == ["Generalist", "Industrials & Manufacturing"]   # alias mapped
    assert (r["ebitda_min_m"], r["ebitda_max_m"]) == (0.4, 4)             # EV / 5
    assert r["covers_sme"] is True
    assert "cf_professionals" not in r["missing"]


def test_national_coverage_fills_regions():
    r = s().get("bigbank-com")
    assert len(r["regions_covered"]) == 12
    assert r["covers_sme"] is False


def test_unknown_size_is_none_and_kept_only_on_request():
    st = s()
    assert st.get("mystery-co-uk")["covers_sme"] is None
    ids = {r["id"] for r in st.query(sme=True)}
    assert ids == {"alphacf-co-uk", "dentaldeals-co-uk"}
    ids = {r["id"] for r in st.query(sme=True, include_unknown_size=True)}
    assert "mystery-co-uk" in ids and "bigbank-com" not in ids


def test_filters():
    st = s()
    assert [r["id"] for r in st.query(region=["North East"])] == ["alphacf-co-uk", "bigbank-com", "dentaldeals-co-uk"]
    assert [r["id"] for r in st.query(hq_region=["South West"], sector=["Healthcare"])] == ["mystery-co-uk"]
    assert [r["id"] for r in st.query(q="leeds boutique")] == ["alphacf-co-uk"]
    assert [r["id"] for r in st.query(cf_min=10)] == ["bigbank-com"]
    assert [r["id"] for r in st.query(has_contact=True)] == ["alphacf-co-uk", "mystery-co-uk"]
    assert [r["id"] for r in st.query(ebitda_min=10)] == ["bigbank-com"]
    assert [r["id"] for r in st.query(sort="cf_professionals", order="desc")][:2] == ["bigbank-com", "alphacf-co-uk"]


def test_overlaps():
    assert model.overlaps(None, None, 0.5, 2) is None
    assert model.overlaps(3, None, 0.5, 2) is False
    assert model.overlaps(None, 0.6, 0.5, 2) is True
    assert model.overlaps(2, 50, 0.5, 2) is True


def test_merge_dedupes_on_domain_and_keeps_overrides():
    a = {"name": "Alpha CF", "website": "https://www.alphacf.co.uk", "firm_type": "independent_boutique",
         "sectors": ["Healthcare"], "sources": ["https://a"]}
    b = {"name": "Alpha Corporate Finance Ltd", "website": "alphacf.co.uk/", "firm_type": "independent_boutique",
         "cf_professionals": 5, "sectors": ["Care"], "sources": ["https://b"], "hq": "Leeds"}
    rows, stats = store.merge([[a], [b]], overrides=[{"id": "alphacf-co-uk", "cf_professionals": 7}],
                              excluded={"nope"})
    assert stats["total"] == 1 and stats["merged"] == 1
    r = rows[0]
    assert r["cf_professionals"] == 7 and r["hq"] == "Leeds"
    assert set(r["sectors"]) == {"Healthcare", "Care"} and len(r["sources"]) == 2
    assert r["aliases"] and r["name"] not in r["aliases"]


def test_problems():
    assert model.problems(model.clean({"name": "x", "website": "x.com", "firm_type": "bank"}))
    assert not model.problems(model.clean({"name": "x", "website": "x.com", "firm_type": "big4", "sources": ["u"]}))


def test_real_data_is_valid():
    rows = store.read_jsonl(store.DATA / "advisers.jsonl")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        assert not model.problems(model.clean(r)), r["id"]


def test_cli_known_and_validate_batch(tmp_path, capsys):
    from cfadvisers.cli import main
    assert main(["--data", str(FIX), "known"]) == 0
    out = capsys.readouterr().out
    assert "Alpha CF | https://alphacf.co.uk | independent_boutique | Leeds" in out
    batch = tmp_path / "b.jsonl"
    batch.write_text('{"name":"X","website":"x.com","firm_type":"big4","sources":["u"]}\n'
                     '{"name":"X2","website":"https://www.x.com/","firm_type":"big4","sources":["u"]}\n')
    assert main(["validate", str(batch)]) == 1        # same website twice -> duplicate id
    assert "duplicate id" in capsys.readouterr().out


def test_merge_applies_site_check_fills(tmp_path):
    import json
    from cfadvisers.cli import main
    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "b.jsonl").write_text(
        '{"name":"X","website":"x.co.uk","firm_type":"independent_boutique","contact_email":"deals@x.co.uk","sources":["u"]}\n')
    (tmp_path / "site_checks.jsonl").write_text(json.dumps(
        {"id": "x-co-uk", "status": 200, "best_email": "info@x.co.uk", "phone": "0113 000 0000",
         "team_url": "https://x.co.uk/team", "contact_url": None}) + "\n")
    assert main(["--data", str(tmp_path), "merge", "--fresh"]) == 0
    r = store.read_jsonl(tmp_path / "advisers.jsonl")[0]
    assert r["contact_email"] == "deals@x.co.uk"          # research wins over the site check
    assert r["contact_phone"] == "0113 000 0000" and r["team_url"] == "https://x.co.uk/team"


def test_clean_dedupes_sources_ignoring_trailing_slash():
    r = model.clean({"name": "X", "website": "x.com", "sources": ["https://x.com/", "https://x.com", " https://x.com/a "]})
    assert r["sources"] == ["https://x.com/", "https://x.com/a"]
