from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import bam_mat_khau, kiem_tra_mat_khau, lay_nguoi_dung_hien_tai, tao_token
from app.deps import lay_db
from app.models import NguoiDung
from app.schemas import NguoiDungRa, NguoiDungTao, Token

router = APIRouter(prefix="/auth", tags=["Xac thuc"])


@router.post("/dang-ky", response_model=NguoiDungRa, status_code=201)
async def dang_ky(du_lieu: NguoiDungTao, db: Session = Depends(lay_db)):
    nguoi_dung = NguoiDung(
        ten_dang_nhap=du_lieu.ten_dang_nhap,
        mat_khau_ma_hoa=bam_mat_khau(du_lieu.mat_khau),
    )
    db.add(nguoi_dung)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ten dang nhap da ton tai")
    db.refresh(nguoi_dung)
    return nguoi_dung


@router.post("/dang-nhap", response_model=Token)
async def dang_nhap(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(lay_db)
):
    nguoi_dung = (
        db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == form.username).first()
    )
    if nguoi_dung is None or not kiem_tra_mat_khau(
        form.password, nguoi_dung.mat_khau_ma_hoa
    ):
        raise HTTPException(status_code=401, detail="Sai tai khoan hoac mat khau")
    return Token(access_token=tao_token(nguoi_dung.ten_dang_nhap))


@router.get("/toi", response_model=NguoiDungRa)
async def thong_tin_cua_toi(nguoi_dung: NguoiDung = Depends(lay_nguoi_dung_hien_tai)):
    return nguoi_dung
