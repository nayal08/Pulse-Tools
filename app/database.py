from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy import  inspect
from sqlalchemy.orm import Session

print('**************************************************************')

# print(settings.DATABASE_URI)
engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@as_declarative()
class Base:

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                    for c in inspect(self).mapper.column_attrs}
