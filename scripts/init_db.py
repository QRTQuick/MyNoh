from settings.config import AppConfig
from database.connection import Database

if __name__ == "__main__":
    cfg = AppConfig.load()
    db = Database(cfg.database_path)
    db.initialize()
    print(f"Initialized {cfg.database_path}")
