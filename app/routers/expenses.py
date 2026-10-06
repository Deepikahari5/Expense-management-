from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import ExpenseStatus, PaymentMethod
from app.models import ExpenseModel
from app.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseTotalResponse,
    ExpenseUpdate,
    MessageResponse,
)
from app.services import (
    apply_expense_filters,
    get_category_or_404,
    get_expense_or_404,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    get_category_or_404(db, payload.category_id)
    expense = ExpenseModel(
        employee_name=payload.employee_name,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description,
        expense_date=payload.expense_date,
        payment_method=payload.payment_method.value,
        status=payload.status.value,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=List[ExpenseResponse])
def get_expenses(
    category_id: Optional[int] = Query(default=None, gt=0),
    status_filter: Optional[ExpenseStatus] = Query(default=None, alias="status"),
    payment_method: Optional[PaymentMethod] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(ExpenseModel)
    query = apply_expense_filters(
        query, category_id, status_filter, payment_method, start_date, end_date
    )
    query = query.order_by(ExpenseModel.expense_date.desc(), ExpenseModel.expense_id)
    return db.scalars(query).all()


# NOTE: "/total" must be declared BEFORE "/{expense_id}", otherwise FastAPI
# would try to parse "total" as an integer expense ID.
@router.get("/total", response_model=ExpenseTotalResponse)
def get_total_expenses(
    category_id: Optional[int] = Query(default=None, gt=0),
    status_filter: Optional[ExpenseStatus] = Query(default=None, alias="status"),
    payment_method: Optional[PaymentMethod] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(
        func.coalesce(func.sum(ExpenseModel.amount), 0.0),
        func.count(ExpenseModel.expense_id),
    )
    query = apply_expense_filters(
        query, category_id, status_filter, payment_method, start_date, end_date
    )
    total, count = db.execute(query).one()
    return {"total_amount": round(float(total), 2), "expense_count": count}


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return get_expense_or_404(db, expense_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)
):
    expense = get_expense_or_404(db, expense_id)
    get_category_or_404(db, payload.category_id)

    expense.employee_name = payload.employee_name
    expense.category_id = payload.category_id
    expense.amount = payload.amount
    expense.description = payload.description
    expense.expense_date = payload.expense_date
    expense.payment_method = payload.payment_method.value
    expense.status = payload.status.value

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", response_model=MessageResponse)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = get_expense_or_404(db, expense_id)
    db.delete(expense)
    db.commit()
    return {"message": f"Expense {expense_id} deleted successfully"}
