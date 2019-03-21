import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for i,t,a,y in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": i, "title": t, "author": a, "year": y})
        #print(f"Added flight from {origin} to {destination} lasting {duration} minutes.")
        print(f"Book {t} is by {a} published in {y}")

    db.commit() #Save changes

if __name__ == "__main__":
    main()
