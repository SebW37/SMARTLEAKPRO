"""
Configuration de la base de données PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/smartleakpro"
)

# Création du moteur async
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log des requêtes SQL
    future=True
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base pour les modèles
Base = declarative_base()

# Métadonnées
metadata = MetaData()


async def get_db():
    """Dependency pour obtenir une session de base de données"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialisation de la base de données"""
    async with engine.begin() as conn:
        # Créer toutes les tables
        await conn.run_sync(Base.metadata.create_all)
