import os
from models import *
from flask import Flask, session, request, render_template, jsonify
from flask_session import Session
from sqlalchemy import *#create_engine
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#
Session(app)

#
#with app.app_context():
#    db.init_app(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#with app.app_context():
#    SQLAlchemy.init_app(app)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

register = db.execute("SELECT * FROM register").fetchall()
reviews = db.execute("SELECT * FROM new_review").fetchall()
BOOKS = db.execute("SELECT * FROM books").fetchall()
user_review=[]
name="no name"

@app.route("/")
def index():
    #db.create_all()
    #register = Register.query.all()

    return render_template("index.html", register=register )


@app.route("/search/<string:name>", methods=["GET","POST"])
def search(name):
    #books = Books.query.all()

    search_value = request.form.get("search")
    print(f"{search_value} was requested by {name}")

    search_book= Books.query.filter(or_ (Books.title.like("%"+search_value+"%"), Books.isbn.like(search_value+"%"),Books.author.like("%"+search_value+"%"))).all()
    #print(f"The ORI version: {search_book}")
#IMPORTANT
    #SEARCH_BOOK = db.execute("SELECT * FROM BOOKS WHERE title LIKE :search_value OR isbn LIKE :search_value OR author LIKE  :search_value",{"search_value":"%"+search_value+"%"}).fetchall()
    #print(f"The SQL version: {SEARCH_BOOK}")

    if search_book == []:
        print("Book not present")
        return render_template("NotFound.html")

    else:
        print("Book found")
        a=[]
        s_list = []
        for i in search_book:
            #a = session.query(Books.title).filter(Books.id == i).all()
            a.append(i.isbn)
            s_list.append(i)


        return render_template("found.html", s_list=s_list, isbn= a, name=name)#str(a)[1:-1])


@app.route("/login", methods=["GET","POST"])
def login():
    """Login into library."""


    # Get form information.
    name = request.form.get("name")
    print(name)
    password = request.form.get("password")

    #if db.execute("SELECT * FROM register WHERE name = :name", {"name": name}).rowcount == 0:
    #    return render_template("error.html", message="No such flight with that id.")
    users = db.execute("SELECT name, password FROM register").fetchall()
    flag=0
    v=0
    for user in users:
        if(user.name == name):
            print("Already registered") #Prints in cmd, not webpage
            flag = 1
            break
    if(flag==1 and user.password != password):
        v = 1
        return render_template("error.html")
    if(flag != 1 and v !=1):
        db.execute("INSERT INTO register (name, password) VALUES (:name, :password)",
            {"name": name, "password": password})
        db.commit()
        return render_template("success.html")
    return render_template("home.html", register=register, name=name)

#name= db.execute("SELECT id, name FROM register WHERE name=name").fetchall()
#print(name)
@app.route("/detail/<string:name>/<string:isbn>", methods=["GET","POST"])

def detail(name,isbn):

        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "81oHo1RzaHFe9uovNmoHw", "isbns": isbn})
        #print(res) Response 200
        boo = Books.query.filter_by(isbn=isbn).first()
        boo_id = boo.id
        print(boo_id) #<Book 5>
        print(f"{name} is the name")
        u_name = db.execute("SELECT id FROM register WHERE name= :name", {"name":name}).fetchone()
        print(u_name[0])
        print(type(u_name[0]))
        res = res.json()
        rating = res['books'][0]['ratings_count']
        avg_rating = res['books'][0]['average_rating']

        r_flag = db.execute("SELECT * FROM new_review WHERE r_book= :r_book AND r_user= :r_user",{"r_book":boo_id, "r_user":u_name[0]}).fetchone()
        rr = 0
        print(r_flag)
        print(f"{type(r_flag)} is its type")

        if r_flag == None:
            if request.method == "POST":

            #user_id = db.execute("SELECT id FROM register WHERE str(name)==(name)")
            #print(int(user_id))
                rr = 0
                rev = request.form.get("user_review")
                rev_no = request.form.get("user_review_no")
                db.execute("INSERT INTO new_review (r_user, rev, r_book, rev_no ) VALUES (:r_user, :rev, :r_book, :rev_no)", {"r_user": u_name[0], "rev": rev, "r_book":boo_id, "rev_no":rev_no})
                db.commit()

            #user_review.append(request.form.get("user_review"))
            #rint(user_review)
                #print(type(user_review))

                #return render_template("detail.html", rating=rating, avg=avg_rating, boo=boo, user_review=user_review ,name=name)
        else:
            rr = 1;
        book_reviews = db.execute("SELECT rev, rev_no FROM new_review WHERE r_book = :r_book", {"r_book":boo_id}).fetchall()
        print(book_reviews)
        #list_len = len(book_reviews)
        #print(f"No. of reviews is {list_len}")
        return render_template("detail.html", rating=rating, avg=avg_rating, boo=boo, user_review=book_reviews ,name=name, rr=rr)#, list_len=list_len)

@app.route("/api/<string:isbn>")
def book_api(isbn):

    #Ensure isbn exists
    b_isbn = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if b_isbn is None:
        return jsonify({"Sorry": "Book not yet added or Invalid isbn"})  ,404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "81oHo1RzaHFe9uovNmoHw", "isbns": isbn})
    res = res.json()
    rating = res['books'][0]['ratings_count']
    avg_rating = res['books'][0]['average_rating']

    return jsonify({"title": b_isbn.title,
    "author": b_isbn.author,
    "year": b_isbn.year,
    "isbn": b_isbn.isbn,
    "review_count": rating,
    "average_score": avg_rating})
