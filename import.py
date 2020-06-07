import os, csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
# database engine object from SQLAlchemy that manages connections to the database
password = os.getenv('project1dbpassword')
user = os.getenv('project1dbuser')
host = os.getenv('project1dbhost')
database = os.getenv('project1db')

engine = create_engine('postgres://rdstzxdmflqkwu:84fccd0cec0e08ad62dae857081de7e2861758c2b9f4f7fdb86e950776c5264d@ec2-18-210-214-86.compute-1.amazonaws.com:5432/df7o3kgtp3cf5s')
# create a 'scoped session' that ensures different users' interactions with the database are kept separate
db = scoped_session(sessionmaker(bind=engine))
file = open("books.csv")
reader = csv.reader(file)
n=0
for isbn, title, author, year in reader:
    n=n+1
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn,
                "title": title,
                "author": author,
                "year": year})
    print(f"{n}Added book {title} to database.")
db.commit()
