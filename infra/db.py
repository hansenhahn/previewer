from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, database_url: str, **engine_kwargs):
        self.engine = create_engine(database_url, **engine_kwargs)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def is_healthy(self) -> bool:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def create_all(self) -> None:
        from .models import Base

        Base.metadata.create_all(self.engine)
