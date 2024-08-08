from .extensions import db
from sqlalchemy.orm import Mapped, mapped_column


class Maps(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    size: Mapped[int] = mapped_column()
