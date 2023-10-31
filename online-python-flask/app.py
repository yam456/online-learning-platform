from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random

app = Flask(__name__)

app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:''@localhost/onlinelearning'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your email provider's SMTP server
app.config['MAIL_PORT'] = 587  # Port for sending email
app.config['MAIL_USE_TLS'] = True  # Use TLS for secure connection
app.config['MAIL_USERNAME'] = 'yaminimr2@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'hkiq uide xisj icjy'  # Your email password


db = SQLAlchemy(app)
mail = Mail(app)


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    courses = db.relationship('Course', back_populates='teacher')
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
     # Define the one-to-many relationship between Student and Purchase
    purchased_courses = db.relationship('Purchase', back_populates='student')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
  
# Course Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)  # Use 'teacher.id' here
    price = db.Column(db.Integer, nullable=False)

    # Define a relationship to the Teacher model
    teacher = db.relationship('Teacher', back_populates='courses')
    # Define a one-to-many relationship between Course and Purchase
    purchases = db.relationship('Purchase', back_populates='course')
    #content = db.relationship('Content', back_populates='course')
    def __init__(self, title, teacher_id, price):
        self.title = title
        self.teacher_id = teacher_id
        self.price = price

# Purchase Model
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False) 
    s_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False) 
    
    # Define a many-to-one relationship between Purchase and Course
    course = db.relationship('Course', back_populates='purchases')
    # Define the many-to-one relationship between Purchase and Student
    student = db.relationship('Student', back_populates='purchased_courses')
    def __init__(self, course_id, s_id):
        self.course_id = course_id
        self.s_id = s_id


@app.route('/')
def Index():
    return render_template("index.html")

@app.route('/teacher_signup.html')
def teacher_signup():
    all_data = Teacher.query.all()

    return render_template("teacher_signup.html", teachers= all_data)

@app.route('/teacher_signup/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        my_data = Teacher(name, email, password)
        db.session.add(my_data)
        db.session.commit()

        flash("Teacher Inserted Successfully")

        return redirect(url_for('teacher_signup'))

@app.route('/teacher_signup/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        my_data= Teacher.query.get(request.form.get('id'))

        my_data.name= request.form['name']
        my_data.email = request.form['email']
        my_data.password = request.form['password']

        db.session.commit()
        flash("Teacher Updated Successfully")

        return redirect(url_for('teacher_signup'))

@app.route('/delete/<id>', methods=['GET','POST'])
def delete(id):
    my_data= Teacher.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Teacher Deleted Successfully")

    return redirect(url_for('teacher_signup'))

@app.route('/student_signup.html')
def student_signup():
    all_data = Student.query.all()

    return render_template("student_signup.html", students= all_data)

@app.route('/student_signup/insert1', methods=['POST'])
def insert1():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        my_data = Student(name, email, password)
        db.session.add(my_data)
        db.session.commit()

        flash("Student Inserted Successfully")

        return redirect(url_for('student_signup'))

@app.route('/student_signup/update1',methods=['GET','POST'])
def update1():
    if request.method == 'POST':
        my_data= Student.query.get(request.form.get('id'))

        my_data.name= request.form['name']
        my_data.email = request.form['email']
        my_data.password = request.form['password']

        db.session.commit()
        flash("Student Updated Successfully")

        return redirect(url_for('student_signup'))

@app.route('/delete1/<id>/', methods=['GET','POST'])
def delete1(id):
    my_data= Student.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Student Deleted Successfully")

    return redirect(url_for('student_signup'))
#..........................................................


#SignIn
@app.route('/teacher_signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verify the email and password.
        teacher = Teacher.query.filter_by(email=email).first()
        if teacher:
            if teacher.password == password:
                session['teacher_id'] = teacher.id
                session['teacher_email'] = teacher.email
                # Password is correct. Proceed with OTP generation and sending.
                # Generate a random OTP (6-digit code).
                otp = str(random.randint(100000, 999999))
                session['otp'] = otp  # Store OTP in session for verification

                # Send the OTP to the user's email.
                msg = Message('Your OTP for Sign In', sender='yaminimr2@gmail.com', recipients=[email])
                msg.body = f'Your OTP is: {otp}'
                mail.send(msg)

                flash("An OTP has been sent to your email. Please check your inbox and verify your sign-in.")
                return redirect(url_for('verify_signin_otp'))
            else:
                flash("Invalid password. Please try again.")
        else:
            flash("Email not found. Please check your email or sign up.")

    return render_template("teacher_signin.html")

@app.route('/student_signin', methods=['GET', 'POST'])
def signin1():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verify the email and password.
        student = Student.query.filter_by(email=email).first()  # Use the Student model
        if student:
            if student.password == password:
                # Password is correct. Proceed with OTP generation and sending.
                # Generate a random OTP (6-digit code).
                otp = str(random.randint(100000, 999999))
                session['otp'] = otp  # Store OTP in session for verification

                # Store student's ID and name in the session
                session['student_id'] = student.id
                session['student_name'] = student.name

                # Send the OTP to the user's email.
                msg = Message('Your OTP for Sign In', sender='yaminimr2@gmail.com', recipients=[email])
                msg.body = f'Your OTP is: {otp}'
                mail.send(msg)

                flash("An OTP has been sent to your email. Please check your inbox and verify your sign-in.")
                return redirect(url_for('verify_signin_otp1'))
            else:
                flash("Invalid password. Please try again.")
        else:
            flash("Email not found. Please check your email or sign up.")

    return render_template("student_signin.html")



@app.route('/verify_signin_otp', methods=['GET', 'POST'])
def verify_signin_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session['otp']:
            # OTP is correct. You can consider the user signed in.

            flash("Sign-in successful.")
            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Invalid OTP. Please try again.")

    return render_template("verify_signin_otp.html")

@app.route('/verify_signin_otp1', methods=['GET', 'POST'])
def verify_signin_otp1():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session['otp']:
            # OTP is correct. You can consider the user signed in.

            flash("Sign-in successful.")
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid OTP. Please try again.")

    return render_template("verify_signin_otp.html")
#........................................
@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Retrieve the teacher's ID from the session
    teacher_id = session.get('teacher_id')

    if teacher_id:
        # Query the database to get the teacher's information based on their ID
        teacher = Teacher.query.get(teacher_id)

        if teacher:
            # Query the database to get the registered students associated with this teacher
            registered_students = Student.query.join(Purchase).join(Course).filter(Course.teacher == teacher).all()
            all_data = Course.query.all()

            return render_template("teacher_dashboard.html", courses=all_data, registered_students=registered_students)
''''
@app.route('/teacher_dashboard')
def teacher_dashboard():
    all_data = Course.query.all()

    return render_template("teacher_dashboard.html",courses= all_data)

'''
@app.route('/teacher_dashboard/insert3', methods=['POST'])
def insert3():
    if request.method == 'POST':
        title = request.form['title']
        teacher_id = request.form['teacher_id']
        price = int(request.form['price'])

        my_data = Course(title, teacher_id, price)
        db.session.add(my_data)
        db.session.commit()

        flash("Course Inserted Successfully")

        return redirect(url_for('teacher_dashboard'))

@app.route('/teacher_dashboard/update3',methods=['GET','POST'])
def update3():
    if request.method == 'POST':
        my_data= Course.query.get(request.form.get('id'))

        my_data.title= request.form['title']
        my_data.teacher_id = request.form['teacher_id']
        my_data.price = request.form['price']

        db.session.commit()
        flash("Course Updated Successfully")

        return redirect(url_for('teacher_dashboard'))

@app.route('/delete3/<id>', methods=['GET','POST'])
def delete3(id):
    my_data= Course.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Course Deleted Successfully")

    return redirect(url_for('teacher_dashboard'))

#------------------------------------
@app.route('/student_dashboard')
def student_dashboard():
    search_query = request.args.get('search_query')
    
    # Retrieve student's ID and name from the session
    student_id = session.get('student_id')
    student_name = session.get('student_name')
    
    if student_id:
        # Query the database to get the courses the student has subscribed to
        subscribed_courses = Purchase.query.filter_by(s_id=student_id).join(Course).all()

        # Continue with the rest of your logic for displaying courses
        if search_query:
            # Perform a database query to find courses matching the search query
            courses = Course.query.filter(Course.title.ilike(f'%{search_query}%')).all()
        else:
            # If no search query is provided, show all courses
            courses = Course.query.all()

        return render_template("student_dashboard.html", courses=courses, student_id=student_id, student_name=student_name, subscribed_courses=subscribed_courses)
    else:
        flash("Please sign in to access the student dashboard.")
        return redirect(url_for('student_signin'))
    

@app.route('/explore_courses', methods=['GET'])
def explore_courses():
    # Handle the course exploration logic here
    # This is where you will search for courses and display them

    # For example, you can retrieve the search query from the request args:
    courses = Course.query.all()
    search_query = request.args.get('search_query')
  
    # Then, query the database for courses matching the search query
    if search_query:
        courses = Course.query.filter(Course.title.ilike(f'%{search_query}%')).all()
    else:
        courses = Course.query.all()

    # Render the explore_courses.html template and pass the courses
    return render_template('explore_courses.html', courses=courses)

@app.route('/course_details/<int:course_id>')
def course_details(course_id):
    course = Course.query.get(course_id)
    return render_template("course_details.html", course=course)

@app.route('/enroll_course/<int:course_id>', methods=['GET'])
def enroll_course(course_id):
    # Retrieve the student's ID from the session
    student_id = session.get('student_id')

    if student_id:
        course = Course.query.get(course_id)

        if course:
            # Check if the student is already enrolled in the course
            existing_purchase = Purchase.query.filter_by(course_id=course_id, s_id=student_id).first()

            if existing_purchase:
                flash("You are already enrolled in this course.")
            else:
                # Create a new purchase record
                purchase = Purchase(course_id=course_id, s_id=student_id)
                db.session.add(purchase)
                db.session.commit()
                flash("Enrollment successful.")  # Add this flash message

            # Pass the path to the existing qrcode.jpeg image to the template
            qr_code_image_path = 'qrcode.jpeg'

            return render_template('enroll_course.html', qr_code_image_path=qr_code_image_path)
        else:
            flash("Course not found.")
    else:
        flash("Invalid student ID.")

    return redirect(url_for('student_dashboard'))


#........................................
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

