import datetime
from typing import Annotated

from sqlalchemy import text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, mapped_column



class Base(DeclarativeBase):

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"({self.__class__.__name__}: {', '.join(cols)})"




created_at = Annotated[datetime.datetime, mapped_column(TIMESTAMP, server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(TIMESTAMP,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )]