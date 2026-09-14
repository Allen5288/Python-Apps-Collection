"""
17 - SQL (relational) database with SQLModel (SQLAlchemy + Pydantic in one).

Run:   fastapi dev 17_sql_database.py     (creates ./database.db, SQLite)
Deps:  sqlmodel   (uv add sqlmodel)

Key ideas:
    - `class Hero(SQLModel, table=True)`  -> a DB TABLE and a Pydantic model at once.
    - Separate models for API input/output vs the table (never expose `secret_name`,
      never let clients set `id`):
          HeroBase    common fields
          Hero        table=True, adds id + secret_name
          HeroPublic  what we return (id required)
          HeroCreate  what clients POST (includes secret_name)
          HeroUpdate  PATCH: everything optional
    - One Session per request via a `yield` dependency.
    - Endpoints are plain `def` (SQLAlchemy is blocking) -> FastAPI runs them in a threadpool.

Try:
    POST  /heroes/  {"name":"Deadpond","age":30,"secret_name":"Dive Wilson"}
    GET   /heroes/?offset=0&limit=10
    GET   /heroes/1
    PATCH /heroes/1  {"age":31}
    DELETE /heroes/1
"""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class HeroBase(SQLModel):
    name: str = Field(index=True)  # index=True -> DB index for fast lookups
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):  # table=True -> this one IS a table
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    secret_name: str


class HeroUpdate(SQLModel):  # not HeroBase: every field optional for PATCH
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


# ---------------------------------------------------------------------------
# Engine + session dependency
# ---------------------------------------------------------------------------
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False: FastAPI may use the same connection from different
# threads (one request = one session, so this is safe). SQLite-only setting.
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)  # echo=True to print SQL


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)  # creates tables for every `table=True` model


def get_session():
    with Session(engine) as session:  # closed automatically after the response
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# lifespan: code before `yield` runs on startup, after `yield` on shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # (shutdown cleanup would go here)


app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------
@app.post("/heroes/", response_model=HeroPublic, status_code=201)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)  # HeroCreate -> Hero (table model)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)  # load the generated id
    return db_hero


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)  # by primary key
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)  # only fields the client sent
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep) -> None:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()


# ---------------------------------------------------------------------------
# A filtered query with `where`
#   GET /heroes/search/?name=Dead
# ---------------------------------------------------------------------------
@app.get("/heroes/search/", response_model=list[HeroPublic])
def search_heroes(session: SessionDep, name: str, min_age: int | None = None):
    stmt = select(Hero).where(Hero.name.contains(name))  # type: ignore[union-attr]
    if min_age is not None:
        stmt = stmt.where(Hero.age >= min_age)  # type: ignore[operator]
    return session.exec(stmt).all()
