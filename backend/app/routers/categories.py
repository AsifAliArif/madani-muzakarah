from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.note import Category
from app.models.user import User
from app.schemas import CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cats = db.query(Category).order_by(Category.name).all()
    return [CategoryOut(id=c.id, name=c.name) for c in cats]
