from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, nhap_xuat
from app.auth import chi_thu_thu
from app.deps import lay_db
from app.models import Sach

router = APIRouter(prefix="/nhap-xuat", tags=["Nhap xuat file"])

KICH_THUOC_TOI_DA = 1_000_000   # 1 MB


@router.get("/sach.csv")
async def xuat_sach_csv(db: Session = Depends(lay_db)):
    """Tai toan bo danh muc sach ve duoi dang file CSV."""
    noi_dung = nhap_xuat.ghi_sach_ra_csv(db.query(Sach).order_by(Sach.id).all())
    return Response(
        content=noi_dung,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="sach.csv"'},
    )


@router.get("/bao-cao.json")
async def xuat_bao_cao_json(db: Session = Depends(lay_db)):
    """Bao cao tong hop duoi dang file JSON."""
    bao_cao = {
        "ngay_xuat": date.today(),
        "tong_hop": crud.thong_ke(db),
        "sach_muon_nhieu": crud.sach_muon_nhieu(db, 10),
    }
    return Response(
        content=nhap_xuat.ghi_bao_cao_json(bao_cao),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="bao-cao.json"'},
    )


@router.post("/sach.csv", status_code=201, dependencies=[Depends(chi_thu_thu)])
async def nhap_sach_csv(file: UploadFile, db: Session = Depends(lay_db)):
    """Nhap danh muc sach tu file CSV.

    ISBN da co thi bo qua dong do va bao lai, khong lam hong ca lan nhap.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="Chi nhan file .csv")

    byte = await file.read(KICH_THUOC_TOI_DA + 1)
    if len(byte) > KICH_THUOC_TOI_DA:
        raise HTTPException(status_code=413, detail="File qua lon, toi da 1 MB")
    try:
        noi_dung = byte.decode("utf-8-sig")     # -sig de bo BOM cua Excel
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File phai luu bang ma UTF-8")

    try:
        cac_dong = nhap_xuat.doc_sach_tu_csv(noi_dung)
    except ValueError as loi:
        raise HTTPException(status_code=422, detail=str(loi))

    da_them, bo_qua = 0, []
    for dong in cac_dong:
        db.add(Sach(**dong, so_ban_con=dong["so_ban"]))
        try:
            db.commit()
            da_them += 1
        except IntegrityError:
            db.rollback()
            bo_qua.append(dong["isbn"])
    return {"da_them": da_them, "bo_qua_vi_trung_isbn": bo_qua}
