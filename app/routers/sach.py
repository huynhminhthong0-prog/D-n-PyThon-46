from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app import crud
from app.auth import chi_thu_thu
from app.deps import lay_db
from app.schemas import SachRa, SachSua, SachTao

router = APIRouter(prefix="/sach", tags=["Sach"])


@router.get("", response_model=list[SachRa])
async def liet_ke_sach(
    tim: str | None = Query(default=None, max_length=100),
    con_hang: bool = Query(default=False),
    bo_qua: int = Query(default=0, ge=0),
    gioi_han: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(lay_db),
):
    return crud.liet_ke_sach(db, tim, con_hang, bo_qua, gioi_han)


@router.get("/{sach_id}", response_model=SachRa)
async def lay_sach(sach_id: int = Path(gt=0), db: Session = Depends(lay_db)):
    return crud.lay_sach(db, sach_id)


@router.post(
    "", response_model=SachRa, status_code=201, dependencies=[Depends(chi_thu_thu)]
)
async def them_sach(du_lieu: SachTao, db: Session = Depends(lay_db)):
    return crud.tao_sach(db, du_lieu)


@router.put(
    "/{sach_id}", response_model=SachRa, dependencies=[Depends(chi_thu_thu)]
)
async def sua_sach(
    du_lieu: SachSua, sach_id: int = Path(gt=0), db: Session = Depends(lay_db)
):
    return crud.sua_sach(db, sach_id, du_lieu)


@router.delete("/{sach_id}", status_code=204, dependencies=[Depends(chi_thu_thu)])
async def xoa_sach(sach_id: int = Path(gt=0), db: Session = Depends(lay_db)):
    crud.xoa_sach(db, sach_id)
    return Response(status_code=204)
