import os
from flask import Flask,render_template,session,redirect,request,jsonify
from sqlalchemy import create_engine
import Session
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

if not os.environ.get('DATABASE_URL'):
    raise RuntimeError('DATABASE_URL is not set')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.environ.get('DATABASE_URL')
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    return render_template("frontpage.html")

@app.route("/createaccount",methods=["GET","POST"])
def createaccount():
    #Create my account
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        gender=request.form.get("gender")
        age=request.form.get("age")
        securityquestion=request.form.get("securityquestion")
        securityans=request.form.get("securityans")
        createpassword=request.form.get("createpassword")
        confirmpasword=request.form.get("confirmpassword")
        checkemail=db.execute("SELECT email from account WHERE email=:email",{"email":email})
        if email==checkemail:
            message="You already have an account!Please login."
            return render_template("login.html",emessage=message)
        elif createpassword==confirmpasword:
            db.execute("INSERT INTO account (name,email,gender,age,securityquestion,securityans,password) "
            "VALUES(:name,:email,:gender:,:age,:securityquestion,:securityans,:confirmpassword )",
            {"name":name,"email":email,"gender":gender,"age":age,"securityquestion":securityquestion,"securityans":securityans,
            "confirmpassword":confirmpassword})
            message="Congratulations! your account has been created . Please login."
            return render_template("login.html",smessage=message)
        else:
            message="Sorry! password should match"
            return render_template("createaccount.html",emessage=message)
    else:
        message="please try to submit form instead!!"
        return render_template("createaccount.html",emessage=message)


@app.route("/frontpage/login",methods=["GET","POST"])
def login():
    #clear session for a single user
    session.clear()
    if request.method=="POST":
        login_email=request.form.get("login_email")
        login_email.lower()
        login_password=request.form.get("login_password")
    #for correct information
        checkemail=db.execute("SELECT email from account WHERE email=:login_email",{"login_email":login_email})
        checkemail.lower()
        checkpassword=db.execute("SELECT password from account WHERE email=:login_email",{"login_email":login_email})
        if login_email==checkemail and checkpassword==login_password:
            session['login_email']=checkemail
            session['login_password']=checkpassword
            return redirect("/bookmain.html")
        else:
            message="Please enter a valid email or password"
            return render_template("login.html",emessage=message)

@app.route("/bookmain.html/<string:isbn>",methods=["POST","GET"])
def mainpage(isbn):
    user=session['login_email']
    if request.method=="GET":
        row=db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn})
        if row==None:
            return render_template("bookmain.html",emessage="Book not found!")
        else:
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                                                params={"key": os.getenv("KEY"),"isbn":isbn})
            data=res.json()
            no_of_rating=data["books"]["work_ratings_count"]
            average_rating=data["books"]["average_rating"]
            return render_template("result.html",row,no_of_rating,average_rating)
    else:
        searchvalue=request.form.get("searchvalue")
        if searchvalue==None:
            return render_template("bookmain.html",emessage="Please enter a search criteria!")
        else:
            try:
                row = db.execute("SELECT * FROM books WHERE isbn=:searchvalue", {"isbn": searchvalue})
                if row == None:
                    return render_template("bookmain.html", emessage="Book not found!")
                else:
                    res=requests.get("https://www.goodreads.com/book/review_counts.json",
                                                        params={"key": os.getenv("KEY"), "isbn": isbn})
                    data = res.json()
                    no_of_rating = data["books"]["work_ratings_count"]
                    average_rating = data["books"]["average_rating"]
                    return render_template("result.html", row, no_of_rating, average_rating)
            except:
                searchvalue="%"+searchvalue.title()+"%"
                isbn= db.execute("SELECT isbn FROM books WHERE bookt LIKE :searchvalue", {"searchvalue": searchvalue})
                row = db.execute("SELECT * FROM books WHERE bookt LIKE :searchvalue", {"searchvalue": searchvalue})
                if row == None:
                    return render_template("bookmain.html", emessage="Book not found!")
                else:

                    res=requests.get("https://www.goodreads.com/book/review_counts.json",
                                                        params={"key":os.getenv("KEY"), "isbn": isbn})
                    data = res.json()
                    no_of_rating = data["books"]["work_ratings_count"]
                    average_rating = data["books"]["average_rating"]
                    return render_template("result.html", row, no_of_rating, average_rating)


@app.route("/result",methods=["POST"])
def myresult():
    email=session['login_email']
    review=request.form.get("review")
    comment=request.form.get("comment")
    isbn=row[0]
    checkemail=db.execute("SELECT email FROM track WHERE isbn=:isbn",{"isbn":isbn})
    if checkemail==None:
        db.execute("INSERT INTO track (email,isbn,review,comment) VALUES (:email,:isbn,:review,:comment)",
                   {"email":email,"isbn":isbn,"review":review,"comment":comment})
        db.commit()
        return render_template("bookmain.html",smessage="You successfully submitted your review!")
    else:
        return render_template("result.html",emessage="You already posted a comment previously!")
@app.route("/logout")
def logout():
    session.clear()
    return render_template("frontpage.html")
@app.route("/forgotpassword",methods=["POST"])
def forgotpassword():
    checkemail=request.form.get("email")
    checkques=request.form.get("securityquestion")
    checkans=request.form.get("securityans")
    useremail=db.execute("SELECT email FROM account WHERE email=:checkemail ",{"checkemail":checkemail})
    userques=db.execute("SELECT securityquestion FROM account WHERE email=:checkemail ",{"checkemail":checkemail})
    userans=db.execute("SELECT securityans FROM account WHERE email=:checkemail ",{"checkemail":checkemail})
    userans=userans.lower()
    if useremail==None:
        render_template("forgotpassword.html",emessage="Enter a valid email id!")
    elif userans==None:
        render_template("forgotpassword.html", emessage="Enter correct answer!")
    elif userques==None:
        render_template("forgotpassword.html", emessage="Enter the question you choose!")
    else:
        render_template("newpassword.html", smessage="congratulations!")

@app.route("/newpassword",methods=["POST"])
def newpassword():
    newpassword=request.form.get("newpassword")
    confirmpassword=request.form.get("confirmpassword")
    if newpassword==confirmpassword:
        db.execute("INSERT INTO account (password) VALUE(newpassword:newpassword)",{"newpassword":newpassword})
        return render_template("login.html",smessage="Password successfully changed.")
    return render_template("newpassword.html",emessage="Password should match.")


@app.route("/bookmain/myaccount",methods=["GET"])
def myaccount():
    email = session['login_email']
    user=db.execute("SELECT * FROM account WHERE email=:email",{"email":email})
    name=user[0]
    age=user[3]
    gender=user[2]

@app.route("/bookmain/myaccount/editmail",methods=["POST"])
def editmail():
    email=request.form.get(["email"])
    email=email.lower()
    password=session['login_password']
    enteredpassword=request.form.get(["password"])
    if enteredpassword==None or email==None:
        render_template("editmail.html",emessage="Please fill the field provided.")
    if password==enteredpassword:
        db.execute("INSERT INTO account password VALUE (:enteredpassword) WHERE email=:email)",{"enteredpassword":enteredpassword,"email":email})
        db.commit()
        render_template("myaccount.html",smessage="Your password has been changed successfully.")
    else:
        return render_template("editmail.html",emessage="Password should match")

@app.route("/bookmain/myaccount/editquestion")
def editquestion():
    email=request.form.get(["email"])
    email=email.lower()
    securityquestion=request.form.get(["securityquestions"])
    securityans=request.form.get(["securityans"])
    securityans=securityans.lower()
    password=session['login_password']
    enteredpassword=request.form.get(["password"])
    if enteredpassword==None or securityans==None or securityquestion==None:
        render_template("editquestion.html",emessage="Please fill the field provided.")
    if password==enteredpassword:
        db.execute("INSERT INTO account securityquestion,securityans VALUES (:securityquestion,:securityans) WHERE email=:email)",
                   {"securityquestion":securityquestion,"securityans":securityans})
        db.commit()
        render_template("myaccount.html",smessage="Your password has been changed successfully.")
    else:
        return render_template("editquestion.html",emessage="Password should match")

@app.route("/api/bookmain/<string:isbn>")
def booksapi(isbn):
    #make sure book exists
    userisbn=db.execute("SELECT isbn from books WHERE isbn=:isbn",{"isbn":isbn})
    if userisbn==None:
        return jasonify({"error":"INVALID ISBN no"}),422
    book=db.execute("SELECT isbn,bookt,booka,year,review FROM books JOIN track ON books.isbn=track.isbn")
    isbn=book[0]
    bookt=book[1]
    booka=book[2]
    year=book[3]
    review=book[4]
    return jsonify({
        "isbn":isbn,
        "booktitle":bookt,
        "bookauthor":booka,
        "year":year,
        "review":review
    })


if __name__=="__main__":
    app.run(debug=True)
