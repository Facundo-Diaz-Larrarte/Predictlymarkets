import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev_secret_change_me")
    fee_rate: float = float(os.getenv("FEE_RATE", "0.01"))


settings = Settings()

