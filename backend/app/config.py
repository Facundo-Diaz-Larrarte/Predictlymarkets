import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    fee_rate: float = float(os.getenv("FEE_RATE", "0.01"))


settings = Settings()

