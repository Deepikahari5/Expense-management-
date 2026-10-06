from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CategoryModel
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MessageResponse,
)
from app.services import (
    category_has_expenses,
    ensure_unique_category_name,
    get_category_or_404,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    ensure_unique_category_name(db, payload.category_name)
    category = CategoryModel(
        category_name=payload.category_name, description=payload.description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.scalars(select(CategoryModel).order_by(CategoryModel.category_id)).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return get_category_or_404(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
):
    category = get_category_or_404(db, category_id)
    ensure_unique_category_name(db, payload.category_name, exclude_id=category_id)
    category.category_name = payload.category_name
    category.description = payload.description
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category_or_404(db, category_id)
    if category_has_expenses(db, category_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category that has expenses. Delete or reassign them first",
        )
    db.delete(category)
    db.commit()
    return {"message": f"Category {category_id} deleted successfully"}
