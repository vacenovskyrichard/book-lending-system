from fastapi import APIRouter, Depends, Header, Query, status

from app.api.schemas.loan import LoanCreate, LoanRead, LoanReturn
from app.dependencies import get_loan_service
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/borrow", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def borrow_book(
    payload: LoanCreate,
    x_user_id: int = Header(alias="x-user-id"),
    service: LoanService = Depends(get_loan_service),
) -> LoanRead:
    return service.borrow_book(payload, actor_user_id=x_user_id)


@router.post("/return", response_model=LoanRead)
def return_book(
    payload: LoanReturn,
    x_user_id: int = Header(alias="x-user-id"),
    service: LoanService = Depends(get_loan_service),
) -> LoanRead:
    return service.return_book(payload, actor_user_id=x_user_id)


@router.get("", response_model=list[LoanRead])
def list_loans(
    active_only: bool = Query(default=False),
    service: LoanService = Depends(get_loan_service),
) -> list[LoanRead]:
    return service.list_loans(active_only=active_only)
