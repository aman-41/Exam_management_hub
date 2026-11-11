from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.secret_key='dev-secret-key-change-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exams_manager.db'
db = SQLAlchemy(app)

#table --> class
#column --> attributes
#CREATE ADMIN (id int primary key,username varchar(20),password varchar(20))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String)

class Examiner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    username = db.Column(db.String(20))
    password = db.Column(db.String(50))
    department= db.Column(db.String)
    email_id = db.Column(db.String(100))
    contact_no = db.Column(db.String(10))
    status = db.Column(db.String, default= 'Pending')
    examination_slot = db.relationship('ExaminationSlot', backref = 'examiner',lazy = True)
    examination = db.relationship('Examination', backref = 'examiner',foreign_keys='Examination.examiner_id',lazy = True)
    
    
class Examination(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    type = db.Column(db.String)
    maximum_marks = db.Column(db.Integer)
    duration = db.Column(db.String)
    slot_open_date = db.Column(db.Date)
    slot_close_date = db.Column(db.Date)
    booking_open_date = db.Column(db.Date)
    booking_close_date = db.Column(db.Date)
    status = db.Column(db.String)
    course_id =db.Column(db.String,db.ForeignKey('course.course_id')) 
    examiner_id =db.Column(db.String,db.ForeignKey('examiner.id')) 
    examination_slot = db.relationship('ExaminationSlot', backref = 'examination',lazy = True)
    examination_rubrics = db.relationship('ExaminationRubrics', backref = 'examination',lazy = True)

class ExaminationRubrics(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    examination_id =db.Column(db.String,db.ForeignKey('examination.id'))
    criterion = db.Column(db.String,nullable = False)
    maximum_marks=db.Column(db.Integer)
    weightage = db.Column(db.Integer)
    remark = db.Column(db.String)


class ExaminationSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    date = db.Column(db.Date)
    start_time = db.Column(db.String)
    end_time = db.Column(db.String)
    maximum_slots = db.Column(db.String)
    available_slots= db.Column(db.String)
    status = db.Column(db.String)
    created_by = db.Column(db.String,nullable=False)
    examination_id = db.Column(db.String,db.ForeignKey('examination.id'))
    examiner_id = db.Column(db.Integer,db.ForeignKey('examiner.id'))
    bookings = db.relationship('Booking', backref = 'examinationslot',lazy = True)
        
    

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    username = db.Column(db.String(20))
    password = db.Column(db.String(50))
    email_id = db.Column(db.String(100))
    contact_no = db.Column(db.String(10))
    bookings = db.relationship('Booking', backref = 'student',lazy = True)


class Booking(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey(Student.id))
    examination_slot_id=db.Column(db.Integer,db.ForeignKey(ExaminationSlot.id))
    status = db.Column(db.String)
    rubrics = db.Column(db.JSON,default=dict)
    examination_slot = db.relationship('ExaminationSlot', backref = 'booking',lazy = True)

class Course(db.Model):
    course_id = db.Column(db.String, primary_key=True)
    course_name = db.Column(db.String,nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, default= 'Pending')
    examination = db.relationship('Examination', backref = 'course_details',lazy = True)


    
with app.app_context():
    db.create_all()
    #select * from Admin where username = 'admin'
    admin = Admin.query.filter_by(username= 'admin').first()
    if admin==None:
        admin = Admin(username='admin' ,password ='pass')
        db.session.add(admin)
        db.session.commit()


@app.route('/register' ,methods=['GET','POST'])
def home():
    if request.method == "GET":
        return render_template('home.html')
    else:
        usertype = request.form.get('usertype')
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        department = request.form.get('department')
        email_id = request.form.get('email_id')
        contact_no = request.form.get('contact_no')
    
        if usertype == 'Examiner':
            examiner = Examiner(id=request.form.get('id'),name=name,username=username,password=password,department=department,email_id=email_id,contact_no=contact_no)
            db.session.add(examiner)
            db.session.commit()
            flash('Your registeration is succesfully completed,Please wait for Approval from Institute.','success')
        else:
            student = Student(name=name,username=username,password=password,email_id=email_id,contact_no=contact_no)
            db.session.add(student)
            db.session.commit()
            flash('Your registeration is succesfully completed.','success')
            return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        usertype=request.form.get('usertype')
        username=request.form.get('username')
        password=request.form.get('password')
        if usertype=='Examiner':
            examiner = Examiner.query.filter_by(username=username,password=password).first()
            if examiner:
                if examiner.status == "Approved":
                    session.clear()
                    session['examiner_id']=examiner.id 
                    return redirect('/examiner_dashboard')
                elif examiner.status == "Deactivate":
                    return "Your id is deactivate"
                else:
                    return "You are not approved.Please contact admin or wait for approval"
        
            else:
                return "Either Username or Password is wrong  " 
        elif usertype=='Admin':
            admin = Admin.query.filter_by(username=username,password=password).first()
            if admin:
                session.clear()
                session['admin_id']=admin.id 
            
                return redirect ('/admin_dashboard')
            else:
                return "Either Username or Password is wrong  "
        elif usertype=='Student':
                    session.clear()
                    student = Student.query.filter_by(username=username,password=password).first()
                    if student:
                        session['student_id']=student.id 
                        return redirect ('/student_dashboard')
                    else:
                        return "Either Username or Password is wrong  "

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect('/login')
    total_course = Course.query.count()
    total_examination = Examination.query.count()   
    total_examiner = Examiner.query.count()
    total_student = Student.query.count()
    total_slots = ExaminationSlot.query.count()
    total_booking = Booking.query.count()
    return render_template('admin_dashboard.html',total_course=total_course,total_examination=total_examination,total_examiner=total_examiner,total_student=total_student,total_slots=total_slots,total_booking=total_booking)


@app.route('/student_dashboard')
def student_dashboard():
    student_id=session['student_id']
    if 'student_id' not in session: 
        return redirect('/login')
    student = Student.query.filter_by(id=student_id).first()
    search_query = request.args.get('search', '')
    available_slots = ExaminationSlot.query.filter_by(status = "Available").all()
    evaluation = Booking.query.filter_by(student_id = student_id,status = "Evaluated").all()
    bookings = Booking.query.filter_by(student_id = student_id,status = 'Booked').all()
    booked_course = [b.examination_slot.examination_id for b in Booking.query.filter_by(student_id=student_id).all()]
    booking_available_slots = []
    for slot in available_slots:
        if slot.examination and slot.examination.status == "booking open":
            booking_available_slots.append(slot)
    if search_query:
        booking_available_slots = [slot for slot in booking_available_slots if search_query.lower() in slot.examination.name.lower()]
    return render_template('student_dashboard.html',student=student,available_slots=available_slots,booking_available_slots=booking_available_slots,evaluation=evaluation,bookings=bookings,booked_course=booked_course,search_query=search_query)

@app.route('/course')
def course():
    course=Course.query.all()
    return render_template('course.html',course=course)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/create_course',methods=['GET','POST'])
def create_course():
    if request.method=='GET':
        return render_template('create_course.html')
    else:
        course=Course(course_name=request.form.get('course_name'),course_id=request.form.get('course_id'),description=request.form.get('description'))
        db.session.add(course)
        db.session.commit()
        return redirect('/course')

@app.route('/delete_course/<course_id>')
def delete_course(course_id):
    course = Course.query.filter_by(course_id = course_id).first()
    if course is None:
        return "Course Not Found",404
    db.session.delete(course)
    db.session.commit()
    return redirect('/course')


@app.route('/delete_examination/<id>')
def delete_examination(id):
    examination = Examination.query.filter_by(id = id).first()
    if examination is None:
        return "Exam Not Found",404
    db.session.delete(examination)
    db.session.commit()
    return redirect('/examination')

@app.route('/approve_examiner/<id>')
def approve_examiner(id):
    examiner = Examiner.query.filter_by(id = id).first()
    examiner.status=('Approved')
    db.session.commit()
    return redirect('/examiner')

@app.route('/approve_course/<id>')
def approve_course(id):
    course = Course.query.filter_by(course_id = id).first()
    course.status=('APPROVED')
    db.session.commit()
    return redirect('/course')

@app.route('/deactivate_examiner/<id>')
def deactivate_examiner(id):
    examiner = Examiner.query.filter_by(id = id).first()
    examiner.status=('Deactivate')
    db.session.commit()
    return redirect('/examiner')

@app.route('/edit_course/<course_id>',methods = ["GET","POST"])
def edit_course(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method == "GET":
        return render_template('edit_course.html',course=course)
    else:
        course.course_name = request.form.get("course_name")
        course.course_id = request.form.get("course_id")
        course.description = request.form.get("description")
        db.session.commit()
        return redirect("/course")

@app.route('/edit_examination/<id>',methods = ["GET","POST"])
def edit_examination(id):
    course = Course.query.all()
    examination = Examination.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template('edit_exam.html',examination=examination,course=course)
    else:
        examination.name = request.form.get("name")
        examination.id = request.form.get("id")
        slot_open_date = request.form.get("slot_open_date")
        slot_close_date = request.form.get("slot_close_date")
        booking_open_date = request.form.get("booking_open_date")
        booking_close_date = request.form.get("booking_close_date")
        examination.slot_open_date = datetime.strptime(slot_open_date,'%Y-%m-%d').date()
        examination.slot_close_date = datetime.strptime(slot_close_date,'%Y-%m-%d').date()
        examination.booking_open_date = datetime.strptime(booking_open_date,'%Y-%m-%d').date()
        examination.booking_close_date = datetime.strptime(booking_close_date,'%Y-%m-%d').date()
        examination.status = request.form.get("status")
        db.session.commit()
        return redirect("/examination")
@app.route('/examination')
def examination():
    examination = Examination.query.all()
    available_examination = Examination.query.filter_by(status = 'slot creation').all()
    examiner = Examiner.query.all()
    return render_template('examination.html',examination=examination,examiner=examiner,available_examination=available_examination)

@app.route('/create_examination',methods=['GET','POST'])
def create_examination():
    course = Course.query.all()
    if request.method=='GET':
        return render_template('create_examination.html',course=course)
    else:
        name = request.form.get('name')
        id = request.form.get('id')
        type = request.form.get('type')
        duration = request.form.get('duration')
        slot_open_date = request.form.get('slot_open_date')
        slot_close_date = request.form.get('slot_close_date')
        booking_open_date = request.form.get('booking_open_date')
        booking_close_date = request.form.get('booking_close_date')

        slot_open_date = datetime.strptime(slot_open_date,'%Y-%m-%d').date()
        slot_close_date = datetime.strptime(slot_close_date,'%Y-%m-%d').date()
        booking_open_date = datetime.strptime(booking_open_date,'%Y-%m-%d').date()
        booking_close_date = datetime.strptime(booking_close_date,'%Y-%m-%d').date()
        status = request.form.get('status')
        course_id = request.form.get('course_id')
        examiner_id = request.form.get('examiner_id')
        
        examination=Examination(name=name,id=id,type = type,duration= duration,slot_open_date = slot_open_date,slot_close_date=slot_close_date,booking_open_date=booking_open_date,booking_close_date=booking_close_date,status=status,course_id=course_id,examiner_id=examiner_id)
        db.session.add(examination)
        db.session.commit()
        return redirect('/examination')


@app.route('/create_examiner',methods=['GET','POST'])
def create_examiner():
    if request.method=='GET':
        return render_template('create_examiner.html')
    else:
        id = request.form.get('id')
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        department = request.form.get('department')
        email_id = request.form.get('email_id')
        contact_no = request.form.get('contact_no')   
        examiner = Examiner(id=id,name=name,username=username,password=password,department=department,email_id=email_id,contact_no=contact_no)
        db.session.add(examiner)
        db.session.commit()
        return redirect('/examiner')


@app.route('/examiner')
def examiner():
    examiner=Examiner.query.all()
    examination=Examination.query.all()
    return render_template('examiner.html',examiner=examiner,examination=examination)


#@app.route('/assign_examination/<id>',methods=['GET','POST'])
#def assign_examination(id):
 #   examiner = Examiner.query.filter_by(id=id).first()
  #  examination_id = request.form.get('examination_id')
   # examination = Examination.query.filter_by(id=examination_id).first()
    #if examination is None:
     #   return "Examination not found"
    #examination.examiner_id = examiner.id
    #db.session.commit()
    #return redirect('/examiner')

@app.route('/assign_examiner/<id>',methods=['GET','POST'])
def assign_examiner(id):
    examination = Examination.query.filter_by(id=id).first()
    examiner_id = request.form.get('examiner_id')
    examiner = Examiner.query.filter_by(id=examiner_id).first()
    if examiner is None:
        return "Examiner not found"
    examination.examiner_id = examiner.id
    db.session.commit()
    return redirect('/examination')


@app.route('/assign_rubrics/<id>',methods=['GET','POST'])
def assign_rubrics(id):
    examination = Examination.query.filter_by(id=id).first()
    examination_rubric = examination.examination_rubrics
    if request.method == 'GET':
        return render_template('assign_rubrics.html',examination=examination,examination_rubric=examination_rubric)
    else:
        #if examination_rubric:
         #   examination_rubric.criterion = request.form.get('criterior')
          #  examination_rubric.Weightage = request.form.get('Weightage')
           # examination_rubric.maximum_marks = request.form.get('maximum_marks')
            #examination_rubric.description  =request.form.get('description')
            #db.session.commit()
            #return redirect('/examination')
        
        criterion = request.form.get('criterion')
        maximum_marks=request.form.get('maximum_marks')
        weightage = request.form.get('weightage')
        remark = request.form.get('remark')
        
        rubric = ExaminationRubrics(criterion=criterion,maximum_marks=maximum_marks,weightage=weightage,remark=remark,examination_id=id)
        db.session.add(rubric)
        db.session.flush()
        total_maximum_marks = int(sum(rubric.maximum_marks for rubric in examination.examination_rubrics))
        examination.maximum_marks = int(total_maximum_marks)

        db.session.commit()
        return redirect('/examination')


@app.route('/view_rubrics/<id>',methods=['GET','POST'])
def view_rubrics(id):   
    examination = Examination.query.filter_by(id=id).first()
    examination_rubric = examination.examination_rubrics
    if request.method == 'GET':
        return render_template('view_rubrics.html',examination=examination,examination_rubric=examination_rubric)
    else:
        return redirect('/examination')


@app.route('/create_slot/<id>', methods=["GET","POST"])
def create_slot(id):
    examination = Examination.query.filter_by(id=id).first()
    if request.method == 'GET':
            return render_template('create_slot.html',examination=examination)
    else:
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        maximum_slots = request.form.get('maximum_slots')
        available_slots =maximum_slots
        status = "Available"
        date = datetime.strptime(date, '%Y-%m-%d').date()
        examiner_id = examination.examiner_id
        if 'examiner_id' in session:
            created_by = 'Examiner'
        else:
            created_by = 'Admin'

        examination_slot = ExaminationSlot(date=date,start_time=start_time,end_time=end_time,maximum_slots=maximum_slots,available_slots=available_slots,status=status,examination_id=id,examiner_id = examiner_id,created_by=created_by)
        db.session.add(examination_slot)
        db.session.commit()
        if 'examiner_id' in session:
            return redirect('/examiner_dashboard')
        elif 'admin_id' in session:
            return redirect('/examination')


@app.route('/edit_slot/<int:id>', methods=["GET","POST"])
def edit_slot(id):
    examination_slot = ExaminationSlot.query.filter_by(id=id).first()
    if request.method == 'GET':
        return render_template('edit_slot.html',examination_slot=examination_slot)
    else:
        examination_slot.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        examination_slot.start_time = request.form.get('start_time')
        examination_slot.end_time = request.form.get('end_time')
        examination_slot.maximum_slots = request.form.get('maximum_slots')
        examination_slot.available_slots = request.form.get('available_slots')
        examination_slot.status = request.form.get('status')
        db.session.commit()
        if 'examiner_id' in session:
            return redirect('/slots')
        elif 'admin_id' in session:
            return redirect('/view_all_slots')
        




@app.route('/examiner_dashboard')
def examiner_dashboard():
    examiner_id =int(session['examiner_id'])
    if 'examiner_id' not in session:
        return redirect('/login')
    examiner = Examiner.query.filter_by(id=examiner_id).first()
    pending_evaluation =Booking.query.join(ExaminationSlot).filter(ExaminationSlot.examiner_id == examiner_id,Booking.status == 'Booked').count() 
    total_bookings = db.session.query(Booking).join(ExaminationSlot,Booking.examination_slot_id == ExaminationSlot.id).filter(ExaminationSlot.examiner_id == examiner_id).count()
    assign_examination = Examination.query.filter_by(examiner_id = examiner.id).all()
    available_examination = Examination.query.filter_by(examiner_id = examiner_id,status = 'slot creation').all()
    return render_template("examiner_dashboard.html",examiner=examiner,assign_examination=assign_examination,available_examination=available_examination,total_bookings=total_bookings,pending_evaluation=pending_evaluation)

@app.route('/slots')
def slots():
    examiner_id = session['examiner_id']
    slots = ExaminationSlot.query.filter_by(examiner_id=examiner_id).all()
    return render_template('slots.html',slots=slots)


@app.route('/book_slot/<int:id>', methods=["GET","POST"])
def book_slots(id):
    student_id = session['student_id']
    examination_slot=ExaminationSlot.query.filter_by(id=id).first()
    existing_booking = Booking.query.join(ExaminationSlot).join(Examination).filter(Booking.student_id == student_id,Examination.course_id == examination_slot.examination.course_id).first()
    if existing_booking:
        flash('You have already booked this slot.', 'error')
        return redirect('/student_dashboard')
    booking = Booking(student_id=student_id,examination_slot_id=id,status='Booked')
    db.session.add(booking)
    examination_slot.available_slots = int(examination_slot.available_slots) - 1
    if examination_slot.available_slots == 0:
        examination_slot.status = 'Slot Full'
    db.session.commit()
    return redirect('/student_dashboard')


@app.route('/view_bookings/<int:id>')
def view_bookings(id):
    examination_slot = ExaminationSlot.query.filter_by(id=id).first()
    bookings = Booking.query.filter_by(examination_slot_id=id).all()
    return render_template('view_bookings.html',examination_slot=examination_slot,bookings=bookings)


@app.route('/cancel_booking/<int:id>')
def cancel_booking(id):
    booking = Booking.query.filter_by(id=id).first()

    if booking is None:
        return "Booking not found", 404

    examination_slot = ExaminationSlot.query.filter_by(id=booking.examination_slot_id).first()

    if examination_slot:
        examination_slot.available_slots = int(examination_slot.available_slots) + 1
        examination_slot.status = 'Available'

    db.session.delete(booking)
    db.session.commit()

    flash('Booking cancelled successfully.', 'success')
    return redirect('/student_dashboard')

@app.route('/view_slots/<id>')
def view_slots(id):
    examination = Examination.query.filter_by(id=id).first()
    slots = ExaminationSlot.query.filter_by(examination_id=id).all()
    return render_template('slots.html',examination=examination,slots=slots)

@app.route('/view_all_slots')
def view_all_slots():
    examination_slots = ExaminationSlot.query.all()
    return render_template('view_all_slots.html',examination_slots=examination_slots,)


@app.route('/evaluate_exam/<int:id>', methods=["GET","POST"])
def evaluate_exam(id):
    booking = Booking.query.filter_by(id=id).first()
    examination_slot = booking.examination_slot
    examination = examination_slot.examination
    rubrics = booking.examination_slot.examination.examination_rubrics

    if request.method == 'GET':
        return render_template('evaluate_exam.html', booking=booking, rubrics=rubrics, examination_slot=examination_slot, examination=examination)
    else:
        evaluation_data = {}
        for rubric in rubrics:
            score = request.form.get(f'rubric_{rubric.id}')
            evaluation_data[rubric.criterion] = score
        booking.rubrics = evaluation_data
        booking.status = 'Evaluated'
        db.session.commit()
        flash('Exam evaluated successfully.', 'success')
        return redirect(f'/view_bookings/{examination_slot.id}')

@app.route('/search_examiner', methods=['GET', 'POST'])
def search_examiner():
    if request.method == 'POST':
        search_query = request.form.get('search')
        #select * from Sponsor where username like '%search_query%'
        examiner = Examiner.query.filter(Examiner.username.ilike(f'%{search_query}%')).all()
        return render_template('examiner.html', examiner=examiner)
    else:
        return redirect('/examiner ')

@app.route('/search_examination', methods=['GET', 'POST'])
def search_examination():
    if request.method == 'POST':
        search_query = request.form.get('search')
        #select * from Sponsor where username like '%search_query%'
        examination = Examination.query.filter(Examination.name.ilike(f'%{search_query}%')).all()
        return render_template('student_dashboard.html', examination=examination)
    else:
        return redirect('/student_dashboard')

@app.route('/search_exam', methods=['GET', 'POST'])
def search_exam():
    if request.method == 'POST':
        search_query = request.form.get('search')
        #select * from Sponsor where username like '%search_query%'
        examination = Examination.query.filter(or_(Examination.id.ilike(f'%{search_query}%'),Examination.name.ilike(f'%{search_query}%'))).all()
        return render_template('examination.html', examination=examination)
    else:
        return redirect('/examination')


@app.route('/search_course', methods=['GET', 'POST'])
def search_course():
    if request.method == 'POST':
        search_query = request.form.get('search')
        #select * from Sponsor where username like '%search_query%'
        course = Course.query.filter(or_(Course.course_id.ilike(f'%{search_query}%'),Course.course_name.ilike(f'%{search_query}%'))).all()
        return render_template('course.html', course=course)
    else:
        return redirect('/course')

@app.route('/search_student', methods=['GET', 'POST'])
def search_student():
    if request.method == 'POST':
        search_query = request.form.get('search')
        #select * from Sponsor where username like '%search_query%'
        student = Student.query.filter(or_(Student.id.ilike(f'%{search_query}%'),Student.name.ilike(f'%{search_query}%'))).all()
        return render_template('student.html', student=student)
    else:
        return redirect('/student')

@app.route('/student')
def student():
    student=Student.query.all()
    return render_template('student.html',student=student)



@app.route('/view_booked_slot/<int:id>')
def view_slot_booking(id):
    examination_slot = ExaminationSlot.query.filter_by(id=id).first()
    booking = Booking.query.filter_by(student_id=id).all()
    for b in booking:
            if b.rubrics:
                b.total_marks = sum(int(score) for score in b.rubrics.values())
            else:
                b.total_marks = 'Not Evaluated'
    return render_template('view_booked_slot.html',examination_slot=examination_slot,booking=booking)


if __name__ == '__main__':
    app.run(debug=True)

