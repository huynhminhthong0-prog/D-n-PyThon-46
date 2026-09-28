"""Doc va ghi file: CSV de nhap/xuat danh muc sach, JSON de xuat bao cao.

Chi lam viec voi chuoi va list/dict — khong dinh gi toi FastAPI hay database,
nen test duoc rieng va doc lai duoc de dang.
"""
import csv
import io
import json
from datetime import date, datetime

COT_SACH = ["isbn", "tieu_de", "tac_gia", "nam_xuat_ban", "so_ban", "so_ban_con"]


def doc_sach_tu_csv(noi_dung: str) -> list[dict]:
    """Doc noi dung mot file CSV thanh danh sach dict.

    Bat buoc co cot isbn, tieu_de, tac_gia. Cot nam_xuat_ban va so_ban co thi dung,
    khong co thi lay mac dinh. Dong nao thieu du lieu thi bo qua, khong lam hong ca file.
    """
    cac_dong = []
    doc = csv.DictReader(io.StringIO(noi_dung))
    thieu = {"isbn", "tieu_de", "tac_gia"} - set(doc.fieldnames or [])
    if thieu:
        raise ValueError(f"File CSV thieu cot: {', '.join(sorted(thieu))}")

    for so_thu_tu, dong in enumerate(doc, start=2):   # dong 1 la dong tieu de
        isbn = (dong.get("isbn") or "").strip()
        tieu_de = (dong.get("tieu_de") or "").strip()
        tac_gia = (dong.get("tac_gia") or "").strip()
        if not (isbn and tieu_de and tac_gia):
            continue
        try:
            nam = int(dong["nam_xuat_ban"]) if dong.get("nam_xuat_ban") else None
            so_ban = int(dong["so_ban"]) if dong.get("so_ban") else 1
        except ValueError:
            raise ValueError(f"Dong {so_thu_tu}: nam_xuat_ban hoac so_ban khong phai so")
        cac_dong.append({
            "isbn": isbn,
            "tieu_de": tieu_de,
            "tac_gia": tac_gia,
            "nam_xuat_ban": nam,
            "so_ban": max(1, so_ban),
        })
    return cac_dong


def ghi_sach_ra_csv(cac_sach) -> str:
    """Doi danh sach object Sach thanh mot chuoi CSV tai ve duoc."""
    bo_dem = io.StringIO()
    ghi = csv.DictWriter(bo_dem, fieldnames=COT_SACH)
    ghi.writeheader()
    for sach in cac_sach:
        ghi.writerow({cot: getattr(sach, cot) for cot in COT_SACH})
    return bo_dem.getvalue()


def _doi_kieu(gia_tri):
    """json.dumps khong hieu date/datetime, doi sang chuoi ISO."""
    if isinstance(gia_tri, (date, datetime)):
        return gia_tri.isoformat()
    raise TypeError(f"Khong doi duoc kieu {type(gia_tri).__name__}")


def ghi_bao_cao_json(bao_cao: dict) -> str:
    return json.dumps(bao_cao, ensure_ascii=False, indent=2, default=_doi_kieu)


def luu_ra_file(duong_dan: str, noi_dung: str) -> int:
    """Ghi ra dia, tra ve so ky tu da ghi. encoding='utf-8' de khong hong tieng Viet."""
    with open(duong_dan, "w", encoding="utf-8") as f:
        return f.write(noi_dung)
