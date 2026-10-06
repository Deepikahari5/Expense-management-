from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enums import ExpenseStatus, PaymentMethod


def _clean_required_text(value: str, field_label: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_label} cannot be empty")
    return value


# ----------------------------- Category -----------------------------
class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

    @field_validator("category_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _clean_required_text(v, "Category name")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    category_id: int


# ------------------------------ Expense ------------------------------
class ExpenseBase(BaseModel):
    employee_name: str = Field(..., min_length=1, max_length=100)
    category_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0, description="Must be greater than 0")
    description: str = Field(..., min_length=1, max_length=500)
    expense_date: date
    payment_method: PaymentMethod
    status: ExpenseStatus = ExpenseStatus.PENDING

    @field_validator("employee_name")
    @classmethod
    def validate_employee_name(cls, v: str) -> str:
        return _clean_required_text(v, "Employee name")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        return _clean_required_text(v, "Description")


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    expense_id: int
    created_date: datetime


class ExpenseTotalResponse(BaseModel):
    total_amount: float
    expense_count: int


# ------------------------------- Common -------------------------------
class MessageResponse(BaseModel):
    message: str
