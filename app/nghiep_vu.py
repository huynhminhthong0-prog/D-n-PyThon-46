"""Quy tac nghiep vu viet bang OOP.

Hai ho lop, moi ho mot cong dung:

* `QuyTacMuon` — lop truu tuong, moi quy tac cho muon la mot lop con. `crud.muon_sach`
  chi duyet qua danh sach quy tac va goi `.kiem_tra()`, khong biet ben trong tung cai.
  Them mot quy tac moi = them mot lop, khong sua ham cu.

* `ChinhSachPhat` — cach tinh tien phat. Doi cach tinh = doi mot dong cau hinh,
  khong dong vao `crud.tra_sach`.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import HTTPException

from app.models import DocGia, PhieuMuon, Sach


@dataclass
class NguCanhMuon:
    """Gom moi thu mot quy tac can biet de xet mot lan cho muon."""

    sach: Sach
    doc_gia: DocGia
    dang_giu: list[PhieuMuon]
    so_sach_toi_da: int


class QuyTacMuon(ABC):
    """Lop cha cua moi quy tac cho muon."""

    ly_do: str = "Khong dat dieu kien muon"

    @abstractmethod
    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        """True la qua duoc quy tac nay."""

    def kiem_tra(self, ngu_canh: NguCanhMuon) -> None:
        if not self.dat(ngu_canh):
            raise HTTPException(status_code=409, detail=self.mo_ta(ngu_canh))

    def mo_ta(self, ngu_canh: NguCanhMuon) -> str:
        return self.ly_do

    def __repr__(self):
        return f"<{type(self).__name__}>"


class TheConHieuLuc(QuyTacMuon):
    ly_do = "The doc gia dang bi khoa"

    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        return ngu_canh.doc_gia.dang_hoat_dong


class ConBanDeMuon(QuyTacMuon):
    ly_do = "Sach da het ban de muon"

    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        return ngu_canh.sach.so_ban_con > 0


class ChuaVuotHanMuc(QuyTacMuon):
    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        return len(ngu_canh.dang_giu) < ngu_canh.so_sach_toi_da

    def mo_ta(self, ngu_canh: NguCanhMuon) -> str:
        return f"Moi doc gia chi duoc giu toi da {ngu_canh.so_sach_toi_da} cuon"


class KhongMuonTrungCuon(QuyTacMuon):
    ly_do = "Doc gia dang muon cuon nay roi"

    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        return all(phieu.sach_id != ngu_canh.sach.id for phieu in ngu_canh.dang_giu)


# Them mot quy tac moi thi them mot lop roi ghi ten no vao day
QUY_TAC_CHO_MUON: list[QuyTacMuon] = [
    TheConHieuLuc(),
    ConBanDeMuon(),
    ChuaVuotHanMuc(),
    KhongMuonTrungCuon(),
]


class ChinhSachPhat(ABC):
    """Cach quy doi so ngay tre thanh so tien phat."""

    @abstractmethod
    def tinh(self, so_ngay_tre: int) -> int:
        """Tra ve so tien phat, don vi dong."""

    def __repr__(self):
        return f"<{type(self).__name__}>"


class PhatTheoNgay(ChinhSachPhat):
    """Moi ngay tre mot muc tien co dinh."""

    def __init__(self, moi_ngay: int):
        self.moi_ngay = moi_ngay

    def tinh(self, so_ngay_tre: int) -> int:
        return max(0, so_ngay_tre) * self.moi_ngay


class PhatBacThang(ChinhSachPhat):
    """Bay ngay dau tinh nhu thuong, tu ngay thu tam gap doi."""

    def __init__(self, moi_ngay: int, nguong: int = 7):
        self.moi_ngay = moi_ngay
        self.nguong = nguong

    def tinh(self, so_ngay_tre: int) -> int:
        so_ngay_tre = max(0, so_ngay_tre)
        if so_ngay_tre <= self.nguong:
            return so_ngay_tre * self.moi_ngay
        vuot = so_ngay_tre - self.nguong
        return (self.nguong * self.moi_ngay) + (vuot * self.moi_ngay * 2)


def chon_chinh_sach_phat(ten: str, moi_ngay: int) -> ChinhSachPhat:
    """Doi CHINH_SACH_PHAT trong .env la doi cach tinh, khong sua crud.py."""
    if ten == "bac_thang":
        return PhatBacThang(moi_ngay)
    return PhatTheoNgay(moi_ngay)
