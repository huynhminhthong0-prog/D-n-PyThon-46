from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud
from app.auth import chi_thu_thu
from app.deps import lay_db
from app.schemas import DocGiaRa, DocGiaSua, DocGiaTao, PhieuMuonRa

router = APIRouter(prefix="/doc-gia", tags=["Doc gia"])


@router.get("", response_model=list[DocGiaRa], dependencies=[Depends(chi_thu_thu)])
async def liet_ke_doc_gia(
    tim: str | None = Query(default=None, max_length=60),
    bo_qua: int = Query(default=0, ge=0),
    gioi_han: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(lay_db),
):
    return crud.liet_ke_doc_gia(db, tim, bo_qua, gioi_han)


@router.get(
    "/{doc_gia_id}", response_model=DocGiaRa, dependencies=[Depends(chi_thu_thu)]
)
async def lay_doc_gia(doc_gia_id: int = Path(gt=0), db: Session = Depends(lay_db)):
    return crud.lay_doc_gia(db, doc_gia_id)


@router.get(
    "/{doc_gia_id}/dang-muon",
    response_model=list[PhieuMuonRa],
    dependencies=[Depends(chi_thu_thu)],
)
async def sach_dang_muon(doc_gia_id: int = Path(gt=0), db: Session = Depends(lay_db)):
    crud.lay_doc_gia(db, doc_gia_id)
    return crud.dang_muon(db, doc_gia_id)


@router.post(
    "", response_model=DocGiaRa, status_code=201, dependencies=[Depends(chi_thu_thu)]
)
async def them_doc_gia(du_lieu: DocGiaTao, db: Session = Depends(lay_db)):
    return crud.tao_doc_gia(db, du_lieu)


@router.put(
    "/{doc_gia_id}", response_model=DocGiaRa, dependencies=[Depends(chi_thu_thu)]
)
async def sua_doc_gia(
    du_lieu: DocGiaSua, doc_gia_id: int = Path(gt=0), db: Session = Depends(lay_db)
):
    return crud.sua_doc_gia(db, doc_gia_id, du_lieu)
