
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.enums import ExpenseStatus, PaymentMethod
from app.models import CategoryModel, ExpenseModel


def get_category_or_404(db: Session, category_id: int) -> CategoryModel:
    category = db.get(CategoryModel, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category


def get_expense_or_404(db: Session, expense_id: int) -> ExpenseModel:
    expense = db.get(ExpenseModel, expense_id)
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found",
        )
    return expense


def ensure_unique_category_name(
    db: Session, name: str, exclude_id: Optional[int] = None
) -> None:
    
    query = select(CategoryModel).where(
        func.lower(CategoryModel.category_name) == name.lower()
    )
    if exclude_id is not None:
        query = query.where(CategoryModel.category_id != exclude_id)
    if db.scalars(query).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name '{name}' already exists",
        )


def category_has_expenses(db: Session, category_id: int) -> bool:
    found = db.scalars(
        select(ExpenseModel.expense_id)
        .where(ExpenseModel.category_id == category_id)
        .limit(1)
    ).first()
    return found is not None


def apply_expense_filters(
    query,
    category_id: Optional[int],
    status_filter: Optional[ExpenseStatus],
    payment_method: Optional[PaymentMethod],
    start_date: Optional[date],
    end_date: Optional[date],
):
    
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after end_date",
        )
    if category_id is not None:
        query = query.where(ExpenseModel.category_id == category_id)
    if status_filter is not None:
        query = query.where(ExpenseModel.status == status_filter.value)
    if payment_method is not None:
        query = query.where(ExpenseModel.payment_method == payment_method.value)
    if start_date is not None:
        query = query.where(ExpenseModel.expense_date >= start_date)
    if end_date is not None:
        query = query.where(ExpenseModel.expense_date <= end_date)
    return query
