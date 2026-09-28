from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import cau_hinh
from app.deps import lay_db
from app.models import NguoiDung

THUAT_TOAN = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/dang-nhap")


def bam_mat_khau(mat_khau: str) -> str:
    return bcrypt.hashpw(mat_khau.encode(), bcrypt.gensalt()).decode()


def kiem_tra_mat_khau(mat_khau: str, ma_bam: str) -> bool:
    return bcrypt.checkpw(mat_khau.encode(), ma_bam.encode())


def tao_token(ten_dang_nhap: str) -> str:
    het_han = datetime.now(timezone.utc) + timedelta(
        minutes=cau_hinh.so_phut_het_han
    )
    return jwt.encode(
        {"sub": ten_dang_nhap, "exp": het_han},
        cau_hinh.khoa_bi_mat,
        algorithm=THUAT_TOAN,
    )


def lay_nguoi_dung_hien_tai(
    token: str = Depends(oauth2_scheme), db: Session = Depends(lay_db)
) -> NguoiDung:
    loi_xac_thuc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token khong hop le hoac da het han",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        du_lieu = jwt.decode(
            token, cau_hinh.khoa_bi_mat, algorithms=[THUAT_TOAN]
        )
    except jwt.PyJWTError:
        raise loi_xac_thuc

    nguoi_dung = (
        db.query(NguoiDung)
        .filter(NguoiDung.ten_dang_nhap == du_lieu.get("sub"))
        .first()
    )
    if nguoi_dung is None:
        raise loi_xac_thuc
    return nguoi_dung


def chi_thu_thu(
    nguoi_dung: NguoiDung = Depends(lay_nguoi_dung_hien_tai),
) -> NguoiDung:
    if not nguoi_dung.la_thu_thu:
        raise HTTPException(status_code=403, detail="Chi thu thu duoc thao tac")
    return nguoi_dung
