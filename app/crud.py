from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.config import cau_hinh
from app.models import DocGia, PhieuMuon, Sach
from app.nghiep_vu import QUY_TAC_CHO_MUON, NguCanhMuon, chon_chinh_sach_phat
from app.schemas import DocGiaSua, DocGiaTao, SachSua, SachTao


# ----------------------------------------------------------------------- sach
def lay_sach(db: Session, sach_id: int) -> Sach:
    sach = db.get(Sach, sach_id)
    if sach is None:
        raise HTTPException(status_code=404, detail="Khong tim thay sach")
    return sach


def liet_ke_sach(db: Session, tim: str | None, con_hang: bool, bo_qua: int, gioi_han: int):
    truy_van = db.query(Sach)
    if tim:
        mau = f"%{tim}%"
        truy_van = truy_van.filter(
            Sach.tieu_de.ilike(mau) | Sach.tac_gia.ilike(mau)
        )
    if con_hang:
        truy_van = truy_van.filter(Sach.so_ban_con > 0)
    return truy_van.order_by(Sach.id).offset(bo_qua).limit(gioi_han).all()


def tao_sach(db: Session, du_lieu: SachTao) -> Sach:
    sach = Sach(**du_lieu.model_dump(), so_ban_con=du_lieu.so_ban)
    db.add(sach)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="ISBN da ton tai")
    db.refresh(sach)
    return sach


def sua_sach(db: Session, sach_id: int, du_lieu: SachSua) -> Sach:
    sach = lay_sach(db, sach_id)
    thay_doi = du_lieu.model_dump(exclude_unset=True)
    if "so_ban" in thay_doi:
        dang_muon = sach.so_ban - sach.so_ban_con
        if thay_doi["so_ban"] < dang_muon:
            raise HTTPException(
                status_code=409,
                detail=f"Dang co {dang_muon} ban duoc muon, khong the giam xuong thap hon",
            )
        sach.so_ban_con = thay_doi["so_ban"] - dang_muon
    for ten_cot, gia_tri in thay_doi.items():
        setattr(sach, ten_cot, gia_tri)
    db.commit()
    db.refresh(sach)
    return sach


def xoa_sach(db: Session, sach_id: int) -> None:
    sach = lay_sach(db, sach_id)
    if sach.so_ban_con < sach.so_ban:
        raise HTTPException(status_code=409, detail="Sach dang duoc muon, khong xoa duoc")
    db.delete(sach)
    db.commit()


# -------------------------------------------------------------------- doc gia
def lay_doc_gia(db: Session, doc_gia_id: int) -> DocGia:
    doc_gia = db.get(DocGia, doc_gia_id)
    if doc_gia is None:
        raise HTTPException(status_code=404, detail="Khong tim thay doc gia")
    return doc_gia


def liet_ke_doc_gia(db: Session, tim: str | None, bo_qua: int, gioi_han: int):
    truy_van = db.query(DocGia)
    if tim:
        truy_van = truy_van.filter(DocGia.ho_ten.ilike(f"%{tim}%"))
    return truy_van.order_by(DocGia.id).offset(bo_qua).limit(gioi_han).all()


def tao_doc_gia(db: Session, du_lieu: DocGiaTao) -> DocGia:
    doc_gia = DocGia(**du_lieu.model_dump())
    db.add(doc_gia)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ma doc gia da ton tai")
    db.refresh(doc_gia)
    return doc_gia


def sua_doc_gia(db: Session, doc_gia_id: int, du_lieu: DocGiaSua) -> DocGia:
    doc_gia = lay_doc_gia(db, doc_gia_id)
    for ten_cot, gia_tri in du_lieu.model_dump(exclude_unset=True).items():
        setattr(doc_gia, ten_cot, gia_tri)
    db.commit()
    db.refresh(doc_gia)
    return doc_gia


# ----------------------------------------------------------------- phieu muon
def dang_muon(db: Session, doc_gia_id: int):
    return (
        db.query(PhieuMuon)
        .filter(PhieuMuon.doc_gia_id == doc_gia_id, PhieuMuon.ngay_tra.is_(None))
        .all()
    )


def muon_sach(db: Session, sach_id: int, doc_gia_id: int) -> PhieuMuon:
    sach = lay_sach(db, sach_id)
    doc_gia = lay_doc_gia(db, doc_gia_id)

    ngu_canh = NguCanhMuon(
        sach=sach,
        doc_gia=doc_gia,
        dang_giu=dang_muon(db, doc_gia_id),
        so_sach_toi_da=cau_hinh.so_sach_toi_da,
    )
    for quy_tac in QUY_TAC_CHO_MUON:
        quy_tac.kiem_tra(ngu_canh)

    hom_nay = date.today()
    phieu = PhieuMuon(
        sach_id=sach_id,
        doc_gia_id=doc_gia_id,
        ngay_muon=hom_nay,
        han_tra=hom_nay + timedelta(days=cau_hinh.so_ngay_duoc_muon),
    )
    sach.so_ban_con -= 1
    db.add(phieu)
    db.commit()
    db.refresh(phieu)
    return phieu


def tra_sach(db: Session, phieu_id: int) -> PhieuMuon:
    phieu = db.get(PhieuMuon, phieu_id)
    if phieu is None:
        raise HTTPException(status_code=404, detail="Khong tim thay phieu muon")
    if phieu.ngay_tra is not None:
        raise HTTPException(status_code=409, detail="Phieu nay da tra roi")

    hom_nay = date.today()
    phieu.ngay_tra = hom_nay
    chinh_sach = chon_chinh_sach_phat(
        cau_hinh.chinh_sach_phat, cau_hinh.tien_phat_moi_ngay
    )
    phieu.tien_phat = chinh_sach.tinh((hom_nay - phieu.han_tra).days)
    phieu.sach.so_ban_con += 1
    db.commit()
    db.refresh(phieu)
    return phieu


def liet_ke_phieu(db: Session, chi_dang_muon: bool, bo_qua: int, gioi_han: int):
    truy_van = db.query(PhieuMuon).options(
        selectinload(PhieuMuon.sach), selectinload(PhieuMuon.doc_gia)
    )
    if chi_dang_muon:
        truy_van = truy_van.filter(PhieuMuon.ngay_tra.is_(None))
    return truy_van.order_by(PhieuMuon.id.desc()).offset(bo_qua).limit(gioi_han).all()


def thong_ke(db: Session) -> dict:
    """Gop bang ham tong hop cua SQL, khong keo ca bang ve Python roi sum()."""
    hom_nay = date.today()
    return {
        "so_dau_sach": db.query(Sach).count(),
        "so_ban_sach": db.scalar(select(func.coalesce(func.sum(Sach.so_ban), 0))),
        "so_doc_gia": db.query(DocGia).count(),
        "so_phieu_dang_muon": db.query(PhieuMuon)
        .filter(PhieuMuon.ngay_tra.is_(None))
        .count(),
        "so_phieu_qua_han": db.query(PhieuMuon)
        .filter(PhieuMuon.ngay_tra.is_(None), PhieuMuon.han_tra < hom_nay)
        .count(),
        "tong_tien_phat": db.scalar(
            select(func.coalesce(func.sum(PhieuMuon.tien_phat), 0))
        ),
    }


def sach_muon_nhieu(db: Session, gioi_han: int):
    """JOIN + GROUP BY + COUNT: xep hang sach theo so luot muon.

    LEFT JOIN (isouter=True) de sach chua ai muon van hien ra voi so_luot = 0.
    """
    cac_dong = (
        db.query(
            Sach.id,
            Sach.tieu_de,
            Sach.tac_gia,
            func.count(PhieuMuon.id).label("so_luot"),
        )
        .join(PhieuMuon, PhieuMuon.sach_id == Sach.id, isouter=True)
        .group_by(Sach.id, Sach.tieu_de, Sach.tac_gia)
        .order_by(func.count(PhieuMuon.id).desc(), Sach.tieu_de)
        .limit(gioi_han)
        .all()
    )
    return [
        {"sach_id": d.id, "tieu_de": d.tieu_de, "tac_gia": d.tac_gia,
         "so_luot_muon": d.so_luot}
        for d in cac_dong
    ]


def doc_gia_qua_han(db: Session):
    """Vi du viet SQL tay khi cau truy van de doc hon o dang SQL.

    Tham so truyen qua :ten, khong noi chuoi - chan SQL injection.
    """
    cau = text(
        """
        SELECT dg.ma_dg, dg.ho_ten, s.tieu_de, pm.han_tra
        FROM phieu_muon pm
        JOIN doc_gia dg ON dg.id = pm.doc_gia_id
        JOIN sach s ON s.id = pm.sach_id
        WHERE pm.ngay_tra IS NULL AND pm.han_tra < :hom_nay
        ORDER BY pm.han_tra
        """
    )
    cac_dong = db.execute(cau, {"hom_nay": date.today()}).mappings().all()
    return [dict(d) for d in cac_dong]
