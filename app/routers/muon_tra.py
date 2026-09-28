from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud
from app.auth import chi_thu_thu
from app.deps import lay_db
from app.schemas import MuonSach, PhieuMuonChiTiet, PhieuMuonRa

router = APIRouter(prefix="/muon-tra", tags=["Muon tra"])


@router.get(
    "", response_model=list[PhieuMuonChiTiet], dependencies=[Depends(chi_thu_thu)]
)
async def liet_ke_phieu(
    chi_dang_muon: bool = Query(default=False),
    bo_qua: int = Query(default=0, ge=0),
    gioi_han: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(lay_db),
):
    return crud.liet_ke_phieu(db, chi_dang_muon, bo_qua, gioi_han)


@router.post(
    "/muon",
    response_model=PhieuMuonRa,
    status_code=201,
    dependencies=[Depends(chi_thu_thu)],
)
async def muon_sach(du_lieu: MuonSach, db: Session = Depends(lay_db)):
    return crud.muon_sach(db, du_lieu.sach_id, du_lieu.doc_gia_id)


@router.post(
    "/tra/{phieu_id}", response_model=PhieuMuonRa, dependencies=[Depends(chi_thu_thu)]
)
async def tra_sach(phieu_id: int = Path(gt=0), db: Session = Depends(lay_db)):
    return crud.tra_sach(db, phieu_id)
