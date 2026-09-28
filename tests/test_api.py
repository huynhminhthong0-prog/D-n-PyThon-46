"""Kiem thu API bang database trong RAM — khong dung toi thu_vien.db that.

    pip install pytest
    pytest -q
"""
import os

# Phai dat TRUOC khi import app: app.config doc bien moi truong ngay luc import
os.environ["TAO_DU_LIEU_MAU"] = "false"
os.environ["CHUOI_KET_NOI"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, chuan_hoa  # noqa: E402
from app.deps import lay_db  # noqa: E402
from app.main import app  # noqa: E402

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # khong co dong nay thi moi ket noi la mot DB rong khac
)
SessionTest = sessionmaker(bind=engine_test, autoflush=False)


def lay_db_test():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[lay_db] = lay_db_test


@pytest.fixture(autouse=True)
def db_sach():
    Base.metadata.create_all(engine_test)
    yield
    Base.metadata.drop_all(engine_test)


@pytest.fixture
def api():
    return TestClient(app)


@pytest.fixture
def token_thu_thu(api):
    api.post("/auth/dang-ky", json={"ten_dang_nhap": "thuthu", "mat_khau": "matkhau123"})
    db = SessionTest()
    from app.models import NguoiDung

    nd = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == "thuthu").first()
    nd.la_thu_thu = True
    db.commit()
    db.close()
    r = api.post("/auth/dang-nhap", data={"username": "thuthu", "password": "matkhau123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(api):
    assert api.get("/health").status_code == 200


def test_them_sach_can_token(api):
    r = api.post("/sach", json={"isbn": "1234567890", "tieu_de": "X", "tac_gia": "Y"})
    assert r.status_code == 401


def test_luong_muon_tra(api, token_thu_thu):
    sach = api.post(
        "/sach",
        json={"isbn": "1234567890", "tieu_de": "Sach A", "tac_gia": "Tac gia", "so_ban": 1},
        headers=token_thu_thu,
    ).json()
    doc_gia = api.post(
        "/doc-gia",
        json={"ma_dg": "DG001", "ho_ten": "Nguyen Van A", "email": "a@b.vn"},
        headers=token_thu_thu,
    ).json()

    r = api.post(
        "/muon-tra/muon",
        json={"sach_id": sach["id"], "doc_gia_id": doc_gia["id"]},
        headers=token_thu_thu,
    )
    assert r.status_code == 201
    phieu = r.json()

    assert api.get(f"/sach/{sach['id']}").json()["so_ban_con"] == 0

    r = api.post(
        "/muon-tra/muon",
        json={"sach_id": sach["id"], "doc_gia_id": doc_gia["id"]},
        headers=token_thu_thu,
    )
    assert r.status_code == 409

    r = api.post(f"/muon-tra/tra/{phieu['id']}", headers=token_thu_thu)
    assert r.status_code == 200
    assert r.json()["tien_phat"] == 0
    assert api.get(f"/sach/{sach['id']}").json()["so_ban_con"] == 1

    assert api.post(f"/muon-tra/tra/{phieu['id']}", headers=token_thu_thu).status_code == 409


def test_isbn_trung(api, token_thu_thu):
    than = {"isbn": "1234567890", "tieu_de": "A", "tac_gia": "B"}
    assert api.post("/sach", json=than, headers=token_thu_thu).status_code == 201
    assert api.post("/sach", json=than, headers=token_thu_thu).status_code == 409


def test_khong_du_quyen(api):
    api.post("/auth/dang-ky", json={"ten_dang_nhap": "khach", "mat_khau": "matkhau123"})
    r = api.post("/auth/dang-nhap", data={"username": "khach", "password": "matkhau123"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = api.post(
        "/sach",
        json={"isbn": "1234567890", "tieu_de": "A", "tac_gia": "B"},
        headers=h,
    )
    assert r.status_code == 403


# ---------------------------------------------------------------- quy tac OOP
def test_chinh_sach_phat():
    from app.nghiep_vu import PhatBacThang, PhatTheoNgay

    assert PhatTheoNgay(5000).tinh(10) == 50_000
    assert PhatTheoNgay(5000).tinh(-3) == 0          # tra som khong duoc thuong
    assert PhatBacThang(5000).tinh(7) == 35_000      # chua vuot nguong
    assert PhatBacThang(5000).tinh(10) == 65_000     # 7*5000 + 3*10000


def test_qua_han_muc_ba_cuon(api, token_thu_thu):
    doc_gia = api.post(
        "/doc-gia",
        json={"ma_dg": "DG009", "ho_ten": "Nguyen Van A", "email": "a@b.vn"},
        headers=token_thu_thu,
    ).json()
    for i in range(4):
        sach = api.post(
            "/sach",
            json={"isbn": f"978000000000{i}", "tieu_de": f"S{i}", "tac_gia": "T"},
            headers=token_thu_thu,
        ).json()
        r = api.post(
            "/muon-tra/muon",
            json={"sach_id": sach["id"], "doc_gia_id": doc_gia["id"]},
            headers=token_thu_thu,
        )
        assert r.status_code == (201 if i < 3 else 409)
    assert "toi da 3 cuon" in r.json()["detail"]


# ---------------------------------------------------------------------- file
def test_doc_sach_tu_csv():
    from app.nhap_xuat import doc_sach_tu_csv

    cac_dong = doc_sach_tu_csv(
        "isbn,tieu_de,tac_gia,nam_xuat_ban,so_ban\n"
        "9780000000001,Sach A,Tac gia A,2020,3\n"
        "9780000000002,Sach B,Tac gia B,,\n"
        ",,,,\n"                                     # dong rong -> bo qua
    )
    assert len(cac_dong) == 2
    assert cac_dong[0]["so_ban"] == 3
    assert cac_dong[1]["nam_xuat_ban"] is None
    assert cac_dong[1]["so_ban"] == 1                # mac dinh


def test_csv_thieu_cot():
    import pytest as _pytest

    from app.nhap_xuat import doc_sach_tu_csv

    with _pytest.raises(ValueError, match="thieu cot"):
        doc_sach_tu_csv("cot_la,abc\n1,2\n")


def test_nhap_xuat_csv(api, token_thu_thu):
    noi_dung = (
        "isbn,tieu_de,tac_gia,nam_xuat_ban,so_ban\n"
        "9780000000001,Lap Trinh Python,Nguyen Van A,2020,3\n"
        "9780000000001,Trung ISBN,Ai Do,2000,1\n"
    )
    r = api.post(
        "/nhap-xuat/sach.csv",
        files={"file": ("sach.csv", noi_dung, "text/csv")},
        headers=token_thu_thu,
    )
    assert r.status_code == 201
    assert r.json() == {"da_them": 1, "bo_qua_vi_trung_isbn": ["9780000000001"]}

    r = api.get("/nhap-xuat/sach.csv")
    assert r.status_code == 200
    assert "Lap Trinh Python" in r.text
    assert r.headers["content-disposition"] == 'attachment; filename="sach.csv"'


def test_nhap_csv_can_quyen(api):
    r = api.post(
        "/nhap-xuat/sach.csv", files={"file": ("a.csv", "isbn\n1\n", "text/csv")}
    )
    assert r.status_code == 401


def test_xuat_bao_cao_json(api):
    import json

    r = api.get("/nhap-xuat/bao-cao.json")
    assert r.status_code == 200
    bao_cao = json.loads(r.text)
    assert set(bao_cao) == {"ngay_xuat", "tong_hop", "sach_muon_nhieu"}


def test_chuan_hoa_chuoi_ket_noi():
    """Loi nay chi lo ra khi deploy: o may dev dung SQLite nen khong ai thay.

    Render cap chuoi khong ghi ro driver. 'postgres://' thi SQLAlchemy 2.0 khong
    hieu, 'postgresql://' thi no chon psycopg2 — goi ma du an khong cai.
    """
    mong_doi = "postgresql+psycopg://u:p@h:5432/db"
    assert chuan_hoa("postgres://u:p@h:5432/db") == mong_doi
    assert chuan_hoa("postgresql://u:p@h:5432/db") == mong_doi

    # Da ghi ro driver, hoac khong phai Postgres: giu nguyen
    assert chuan_hoa("postgresql+psycopg2://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert chuan_hoa("sqlite:///./thu_vien.db") == "sqlite:///./thu_vien.db"
