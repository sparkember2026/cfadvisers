import csv
import io
from pathlib import Path

from fastapi.testclient import TestClient

from cfadvisers.api import create_app

FIX = Path(__file__).parent / "fixtures"


def client():
    return TestClient(create_app(FIX))


def test_health_and_meta():
    c = client()
    assert c.get("/v1/health").json()["advisers"] == 4
    m = c.get("/v1/meta").json()
    assert m["sme_band_ebitda_m"] == [0.5, 2.0] and "London" in m["regions"]


def test_list_filters_and_paging():
    c = client()
    j = c.get("/v1/advisers", params={"sme": "true"}).json()
    assert j["total"] == 2 and {i["id"] for i in j["items"]} == {"alphacf-co-uk", "dentaldeals-co-uk"}
    j = c.get("/v1/advisers", params=[("firm_type", "big4"), ("firm_type", "investment_bank")]).json()
    assert [i["id"] for i in j["items"]] == ["bigbank-com"]
    j = c.get("/v1/advisers", params={"limit": 1, "offset": 1}).json()
    assert j["total"] == 4 and len(j["items"]) == 1
    assert c.get("/v1/advisers", params={"sort": "bogus"}).status_code == 422


def test_detail_and_404():
    c = client()
    assert c.get("/v1/advisers/alphacf-co-uk").json()["name"] == "Alpha CF"
    assert c.get("/v1/advisers/nope").status_code == 404


def test_csv():
    c = client()
    r = c.get("/v1/advisers", params={"sme": "true", "format": "csv"})
    rows = list(csv.DictReader(io.StringIO(r.text)))
    assert r.headers["content-type"].startswith("text/csv") and len(rows) == 2
    assert rows[0]["sectors"] == "Generalist; Industrials & Manufacturing"
    assert len(list(csv.DictReader(io.StringIO(c.get("/v1/export.csv").text)))) == 4


def test_web_page_and_data():
    c = client()
    assert "UK Corporate Finance Advisers" in c.get("/").text
    assert c.get("/app.js").status_code == 200
    j = c.get("/data/advisers.json").json()
    assert len(j["items"]) == 4 and j["meta"]["firm_types"]


def test_token(monkeypatch):
    monkeypatch.setenv("CFA_API_TOKEN", "s3cret")
    c = client()
    assert c.get("/v1/health").status_code == 200
    assert c.get("/v1/advisers").status_code == 401
    assert c.get("/v1/advisers", headers={"Authorization": "Bearer s3cret"}).status_code == 200
    assert c.get("/data/advisers.json", params={"token": "s3cret"}).status_code == 200
    assert c.get("/").status_code == 200
