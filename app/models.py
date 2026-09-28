from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    false,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ten_dang_nhap: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    mat_khau_ma_hoa: Mapped[str] = mapped_column(String(60), nullable=False)
    la_thu_thu: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false(), default=False
    )

    def __repr__(self):
        return f"<NguoiDung {self.ten_dang_nhap}>"


class Sach(Base):
    __tablename__ = "sach"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    tieu_de: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tac_gia: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    nam_xuat_ban: Mapped[int | None] = mapped_column(Integer)
    so_ban: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    so_ban_con: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    phieu_muon: Mapped[list["PhieuMuon"]] = relationship(
        back_populates="sach", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sach {self.isbn} {self.tieu_de}>"


class DocGia(Base):
    __tablename__ = "doc_gia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_dg: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    ho_ten: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    dang_hoat_dong: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=true(), default=True
    )
    ngay_dang_ky: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    phieu_muon: Mapped[list["PhieuMuon"]] = relationship(
        back_populates="doc_gia", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DocGia {self.ma_dg} {self.ho_ten}>"


class PhieuMuon(Base):
    __tablename__ = "phieu_muon"
    __table_args__ = (
        UniqueConstraint("sach_id", "doc_gia_id", "ngay_muon", name="uq_phieu_muon"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sach_id: Mapped[int] = mapped_column(
        ForeignKey("sach.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doc_gia_id: Mapped[int] = mapped_column(
        ForeignKey("doc_gia.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ngay_muon: Mapped[date] = mapped_column(Date, nullable=False)
    han_tra: Mapped[date] = mapped_column(Date, nullable=False)
    ngay_tra: Mapped[date | None] = mapped_column(Date)
    tien_phat: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sach: Mapped["Sach"] = relationship(back_populates="phieu_muon")
    doc_gia: Mapped["DocGia"] = relationship(back_populates="phieu_muon")

    def __repr__(self):
        return f"<PhieuMuon {self.id} sach={self.sach_id} dg={self.doc_gia_id}>"
