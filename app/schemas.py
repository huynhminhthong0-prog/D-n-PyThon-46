from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ----------------------------------------------------------------- nguoi dung
class NguoiDungTao(BaseModel):
    ten_dang_nhap: str = Field(min_length=3, max_length=40)
    mat_khau: str = Field(min_length=8, max_length=72)


class NguoiDungRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ten_dang_nhap: str
    la_thu_thu: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ----------------------------------------------------------------------- sach
class SachTao(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    tieu_de: str = Field(min_length=1, max_length=200)
    tac_gia: str = Field(min_length=1, max_length=120)
    nam_xuat_ban: int | None = Field(default=None, ge=1400, le=2100)
    so_ban: int = Field(default=1, ge=1, le=1000)


class SachSua(BaseModel):
    tieu_de: str | None = Field(default=None, min_length=1, max_length=200)
    tac_gia: str | None = Field(default=None, min_length=1, max_length=120)
    nam_xuat_ban: int | None = Field(default=None, ge=1400, le=2100)
    so_ban: int | None = Field(default=None, ge=1, le=1000)


class SachRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    tieu_de: str
    tac_gia: str
    nam_xuat_ban: int | None
    so_ban: int
    so_ban_con: int


# -------------------------------------------------------------------- doc gia
class DocGiaTao(BaseModel):
    ma_dg: str = Field(min_length=3, max_length=10, pattern=r"^DG\d{3,}$")
    ho_ten: str = Field(min_length=2, max_length=60)
    email: EmailStr


class DocGiaSua(BaseModel):
    ho_ten: str | None = Field(default=None, min_length=2, max_length=60)
    email: EmailStr | None = None
    dang_hoat_dong: bool | None = None


class DocGiaRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ma_dg: str
    ho_ten: str
    email: EmailStr
    dang_hoat_dong: bool
    ngay_dang_ky: datetime


# ----------------------------------------------------------------- phieu muon
class MuonSach(BaseModel):
    sach_id: int = Field(gt=0)
    doc_gia_id: int = Field(gt=0)


class PhieuMuonRa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sach_id: int
    doc_gia_id: int
    ngay_muon: date
    han_tra: date
    ngay_tra: date | None
    tien_phat: int


class PhieuMuonChiTiet(PhieuMuonRa):
    sach: SachRa
    doc_gia: DocGiaRa


class ThongKe(BaseModel):
    so_dau_sach: int
    so_ban_sach: int
    so_doc_gia: int
    so_phieu_dang_muon: int
    so_phieu_qua_han: int
    tong_tien_phat: int


class SachXepHang(BaseModel):
    sach_id: int
    tieu_de: str
    tac_gia: str
    so_luot_muon: int


class PhieuQuaHan(BaseModel):
    ma_dg: str
    ho_ten: str
    tieu_de: str
    han_tra: date
