import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    users = db.execute("SELECT name, password FROM register").fetchall()
    for user in users:
        print(f"{user.name} to {user.password}.")

if __name__ == "__main__":
    main()
