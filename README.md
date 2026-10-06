# Expense Management API

FastAPI + SQLAlchemy + SQLite + Pydantic.

## Project structure
```
expense_api/
├── app/
│   ├── main.py          # App creation, router registration, startup
│   ├── database.py      # SQLite engine, session, Base, get_db
│   ├── enums.py         # PaymentMethod, ExpenseStatus
│   ├── models.py        # SQLAlchemy tables
│   ├── schemas.py       # Pydantic request/response models
│   ├── services.py      # Business logic and DB helpers
│   ├── exceptions.py    # Global exception handlers
│   └── routers/
│       ├── categories.py
│       └── expenses.py
├── requirements.txt
└── README.md
```

## Run
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Swagger UI: http://127.0.0.1:8000/docs

## Endpoints
Categories: POST/GET /categories, GET/PUT/DELETE /categories/{category_id}
Expenses:   POST/GET /expenses, GET/PUT/DELETE /expenses/{expense_id}
Total:      GET /expenses/total
Filters (combinable, also work on /expenses/total):
`?category_id=1` `?status=Approved` `?payment_method=UPI` `?start_date=2026-10-01&end_date=2026-10-06`
