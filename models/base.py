from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from config import Cfg
mysql_config = Cfg().bot_config.db
connection_string = f"{mysql_config.protocol}://{mysql_config.user}:{mysql_config.password}@{mysql_config.hostname}/{mysql_config.database}"
engine = create_engine(connection_string)
print(connection_string)
Session = sessionmaker(bind=engine)
class Base(DeclarativeBase):
    pass