from enum import Enum


class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"
    BANK_TRANSFER = "Bank Transfer"


class ExpenseStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
