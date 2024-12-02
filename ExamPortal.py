
import time
import datetime

from flask import Flask, render_template, request, session, jsonify, redirect, flash
from flask_mail import Mail, Message
from DBConnection import Db
import random


app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ""
app.config['MAIL_PASSWORD'] = ""
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.secret_key = 'hey'


staticpath = "C:\\Users\\ALBIN ROY\\PycharmProjects\\ExamPortal\\static\\"

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/login')
def login():
    return render_template('/login.html')
@app.route('/login_post', methods=['post'])
def login_post():
    user_name = request.form['textfield']
    pass_word = request.form['textfield2']
    a = Db()
    qry = "SELECT * FROM login WHERE username= %s AND passwd= %s "
    res = a.login(qry, user_name, pass_word)
    if res!=None:
        session['login_id'] = res['lid']
        type = res['type']
        if res['type'] == 'admin':
            return '''<script>window.location='/admin_home'</script>'''
        elif res['type'] == 'institution':
            return '''<script>window.location='/institution_home'</script>'''
        elif res['type'] == 'manager':
            return '''<script>window.location='/manager_home'</script>'''
        elif res['type'] == 'hod':
            return '''<script>window.location='/hod_home'</script>'''
        elif res['type'] == 'teacher':
            return '''<script>window.location='/t_home_teacher'</script>'''
        elif res['type'] == 'student':
            return '''<script>window.location='/st_home_student'</script>'''
        else:
            flash("Wrong username or password", "danger")
            return '''<script>window.location='/login</script>'''
    else:
        flash("Wrong username or password, please try again.", "danger")
        return '''<script>window.location='/login'</script>'''




    # return '''<script>alert('Login Successfull');window.location='/admin_home'</script>'''





@app.route('/df')
def df():
    return render_template('/df.html')

@app.route('/')
def home():
    return render_template("home.html")



@app.route('/admin')
def admin():
    return render_template('/admin.html')
@app.route('/institution')
def institution():
    return render_template('/institution.html')
@app.route('/manager')
def manager():
    return render_template('/manager.html')
@app.route('/hod')
def hod():
    return render_template('/hod.html')
@app.route('/teacher')
def teacher():
    return render_template('/teacher.html')
@app.route('/student')
def student():
    return render_template('/student.html')





#============================VIDEO CALL=============================

@app.route('/teacher_videocall/<s_id>')
def teacher_videocall(s_id):
    a= Db()
    qry = "SELECT student.* FROM SUBJECT INNER JOIN exam ON subject.sub_id=exam.sub_id INNER JOIN student ON student.course_id=subject.course_id INNER JOIN teacher ON student.inst_lid=teacher.inst_lid INNER JOIN sub_alloc ON sub_alloc.sub_id=subject.sub_id WHERE teacher.lid='"+str(session['login_id'])+"' AND student.stud_id='"+s_id+"' "
    print(qry)
    res = a.selectOne(qry)
    return render_template('teacher/VideoCall.html',student=res)
@app.route('/teacher_videocall_post',methods=['post'])
def teacher_videocall_post():
    mark = request.form['marks']
    stud_id = request.form['stud_id']
    # exam_id = request.form['exam_id']
    a = Db()
    qry = "INSERT INTO `results`(`exam_id`,`stud_id`,`result`) VALUES('"+str(session['examid'])+"','"+stud_id+"','"+mark+"') "
    res = a.insert(qry)
    print(qry)
    return "<script>window.location='/t_view_students/"+str(session["examid"])+"'</script>"

@app.route('/student_videocall')
def student_videocall():
    return render_template('student/VideoCall.html')


#============================================================================ADMIN===================================================================================================================================================

@app.route('/admin_home')
def admin_home():
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='institution'"
    res = a.select(qry)
    qry1 = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='pending'"
    res1 = a.select(qry1)
    return render_template('admin/home.html',accepted=res, incoming=res1)


@app.route('/incoming_requests')
def incoming_requests():
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='pending'"
    res = a.select(qry)
    return render_template('admin/incoming_requests.html',data=res)
@app.route('/incoming_req_post',methods=['post'])
def incoming_req_post():
    name = request.form['textfield']
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='pending' and institution.name LIKE '%"+name+"%'"
    res = a.select(qry)
    return render_template('admin/incoming_requests.html',data=res)
@app.route('/incoming_req_approve/<id>')
def incoming_req_approve(id):
    a = Db()
    qry= "UPDATE login SET type='institution' WHERE lid='"+id+"'"
    res = a.update(qry)

    qry1 = "SELECT * FROM institution INNER JOIN login ON login.lid=institution.lid WHERE login.lid='"+id+"' "
    res1 = a.selectOne(qry1)
    name = str(res1['name'])
    email = str(res1['email'])

    email_subject = "Registration Successful"
    msg = "Hello "+name+", verification process for your institution has completed successfully. Please do login with your credentials and enjoy the service. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[email])
    message.body = msg
    mail.send(message)
    return '''<script>window.location='/incoming_requests'</script>'''


@app.route('/incoming_req_rejected/<id>')
def incoming_req_rejected(id):
    a=Db()
    qry= "UPDATE login SET type='rejected' WHERE lid='"+id+"'"
    res = a.update(qry)

    qry1 = "SELECT * FROM institution INNER JOIN login ON login.lid=institution.lid WHERE login.lid='" + id + "' "
    res1 = a.selectOne(qry1)
    name = str(res1['name'])
    email = str(res1['email'])

    email_subject = "Registration Unsuccessful"
    msg = "Hello " + name + ", verification process for your institution has completed. Sorry, we cannot approve your institution due to some reasons. Thank you. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[email])
    message.body = msg
    mail.send(message)
    return '''<script>window.location='/incoming_requests'</script>'''
@app.route('/view_accepted')
def view_accepted():
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='institution'"
    res = a.select(qry)
    return render_template('admin/view_accepted.html', data=res)
@app.route('/view_accepted_post',methods=['post'])
def view_accepted_post():
    search = request.form['search']
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='institution' AND institution.name LIKE '%"+search+"%' "
    res = a.select(qry)
    return render_template('admin/view_accepted.html',data=res)

@app.route('/incoming_req_accepted/<id>')
def incoming_req_accepted(id):
    a=Db()
    qry= "UPDATE login SET type='rejected' WHERE lid='"+id+"'"
    res = a.update(qry)
    return '''<script>window.location='/view_accepted'</script>'''


@app.route('/view_rejected_')
def view_rejected():
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='rejected'"
    res = a.select(qry)
    return render_template('admin/view_rejected.html', data=res)
@app.route('/view_rejected_post',methods=['post'])
def view_rejected_post():
    search = request.form['search']
    a = Db()
    qry = "SELECT institution.*,login.type FROM login INNER JOIN institution ON institution.lid=login.lid WHERE login.type='rejected' AND institution.name LIKE '%"+search+"%' "
    res = a.select(qry)
    return render_template('admin/view_rejected.html',data=res)



@app.route('/reject_accepted/<id>')
def reject_accepted(id):
    a=Db()
    qry= "UPDATE login SET type='institution' WHERE lid='"+id+"'"
    res = a.update(qry)
    return '''<script>window.location='/view_rejected_'</script>'''

@app.route('/delete_institution/<lid>/<inst_id>')
def delete_institution(lid,inst_id):
    a = Db()
    qry = "DELETE FROM login WHERE lid='"+lid+"' "
    res = a.delete(qry)

    qry1 = "DELETE FROM institution WHERE inst_id='"+inst_id+"' "
    res1 = a.delete(qry1)
    return '''<script>window.location='/view_rejected_'</script>'''






@app.route('/view_review')
def view_review():
    a = Db()
    qry = "SELECT review.*,manager.name AS man_name,institution.name AS inst_name FROM manager INNER JOIN review ON review.lid=manager.lid INNER JOIN institution ON institution.lid=manager.inst_lid"
    res = a.select(qry)
    return render_template('admin/view_review.html',data=res)

@app.route('/change_password')
def change_password():

    return render_template('admin/change_password.html')

@app.route('/change_pass_post',methods=['post'])
def change_pass_post():

    old_password = request.form['old_pass']
    new_password = request.form['new_pass']
    confirm_password = request.form['confirm_pass']

    a = Db()
    qry = "SELECT * FROM login WHERE passwd='"+old_password+"'"
    res=a.selectOne(qry)
    if res!=None:

        if(new_password==confirm_password):

            qry1="UPDATE login SET passwd ='"+new_password+"' WHERE lid='"+str(session['login_id'])+"'"
            res1=a.update(qry1)

            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('admin/change_password.html')
    else:
        return render_template('admin/change_password.html')




#=========================================================================================INSTITUTION============================================================================================================================================================


@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/registration_post', methods=['post'])
def registration_post():
    inst_image = request.files['inst_img']
    inst_name = request.form['institution']
    inst_place = request.form['place']
    inst_pin = request.form['pin']
    inst_post = request.form['post']
    inst_district = request.form['district']
    inst_contact1 = request.form['contact1']
    inst_contact2 = request.form['contact2']
    inst_email = request.form['email']
    inst_website = request.form['website']
    inst_password = request.form['password']
    inst_confirm_pass = request.form['confirm_pass']

    dt = time.strftime("%Y%m%d-%H%M%S")
    inst_image.save(staticpath+"institution_img\\"+dt+".jpg")
    path = "/static/institution_img/"+dt+".jpg"

    a =Db()
    qry = "INSERT INTO login(`username`,`passwd`,`type`) VALUES('"+inst_email+"','"+str(inst_password)+"','pending')"
    res = a.insert(qry)
    print(res)
    qry1 = "INSERT INTO `institution`(`image`,`name`,`place`,`pin`,`post`,`district`,`contact1`,`contact2`,`website`,`email`,`lid`) VALUES('" + path + "','" + inst_name + "','" + inst_place + "','" + inst_pin + "','" + inst_post + "','" + inst_district + "','" + inst_contact1 + "','" + inst_contact2 + "','" + inst_website + "','" + inst_email + "','" + str(res) + "')"
    res1 = a.insert(qry1)
    print(res1)

    email_subject = "Request successfully sent"
    msg = "Hello " + inst_name + ", your request for the registration to ExamIn have been recieved successfully. After completing the verification process we will notify you. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[inst_email])
    message.body = msg
    mail.send(message)
    return '''<script>alert('Registration request successfully send to admin'); window.location='/login'</script> '''


@app.route('/institution_home')
def institution_home():
    a= Db()
    qry = "SELECT * FROM institution WHERE lid='"+str(session['login_id'])+"' "
    res = a.selectOne(qry)
    a = Db()
    qry1 = "SELECT * FROM notifications"
    res1 = a.select(qry1)
    qry2 = "SELECT * FROM department "
    res2 = a.select(qry2)
    qry3 = " SELECT * FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id INNER JOIN course ON course.course_id=subject.course_id "
    res3 = a.select(qry3)
    return render_template('institution/institution_home.html',inst=res, notif=res1, dept=res2, exam=res3)


@app.route('/course_management')
def course_management():
    a = Db()
    qry = "SELECT * FROM department"
    res = a.select(qry)
    return render_template('institution/course_management.html',dept=res)
@app.route('/course_mang_post', methods=['post'])
def course_mang_post():
    course_name = request.form['Course']
    dept_id = request.form['Department']
    a = Db()
    qry = "INSERT INTO course(course_name,dept_id) VALUES('"+course_name+"','"+dept_id+"') "
    res = a.insert(qry)
    return '''<script> window.location='/course_management'</script> '''


@app.route('/department_management')
def department_management():
    return render_template('institution/department_management.html')
@app.route('/dept_mang_post', methods=['post'])
def dept_mang_post():
    dept_name = request.form['Department']
    a = Db()
    qry = "INSERT INTO department(dname) VALUES('"+dept_name+"')"
    res = a.insert(qry)
    return '''<script>window.location='/department_management'</script> '''


@app.route('/hod_management')
def hod_management():
    a= Db()
    qry = "SELECT * FROM department"
    res = a.select(qry)
    qry1 = "SELECT * FROM teacher WHERE inst_lid='"+str(session['login_id'])+"'"
    res1 = a.select(qry1)
    return render_template('institution/hod_management.html',dept=res,teacher=res1)
@app.route('/hod_mang_post', methods=['post'])
def hod_mang_post():
    department = request.form['Department']
    hod_name = request.form['hod']
    a= Db()

    qry3 = "SELECT * FROM teacher WHERE teach_id='" + hod_name + "'"
    res3 = a.selectOne(qry3)
    print(qry3)
    hod_email = res3['email']
    hodname = res3['name']


    qry1 = "SELECT username FROM login WHERE lid ='"+str(session['login_id'])+"' "
    res1 = a.selectOne(qry1)

    uname= "hod"+res3['email']
    password= random.randint(1000,2000)

    qry2= "INSERT INTO login(`username`,`passwd`,`type`) VALUES('"+uname+"','"+str(password)+"','hod')"
    res2= a.insert(qry2)

    qry = "INSERT INTO `hod`(`dept_id`,`teach_id`,`lid`,`hod_lid`) VALUES('" + department + "','" + hod_name + "','" + str(session['login_id']) + "','"+str(res2)+"')"
    res = a.insert(qry)

    email_subject = "Login details"
    msg = "Hello " + hodname + ", welcome to ExamIn online examination portal. Your username is " + uname + " and password is " + str(password) + ". Use these credentials to login as HOD. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[hod_email])
    message.body = msg
    mail.send(message)
    return '''<script> window.location='/hod_management'</script> '''

@app.route('/view_hod')
def view_hod():
    a =Db()
    qry = "SELECT * FROM `department` INNER JOIN `hod` ON `department`.`dept_id`=`hod`.`dept_id` INNER JOIN `teacher` ON `teacher`.`teach_id`=`hod`.`teach_id` WHERE teacher.inst_lid='"+str(session['login_id'])+"'"
    print(qry)
    res = a.select(qry)
    return render_template('institution/view_hod.html', teacher=res)
@app.route('/view_hod_post',methods = ['post'])
def view_hod_post():
    search = request.form['text']
    a = Db()
    qry = "SELECT * FROM `department` INNER JOIN `hod` ON `department`.`dept_id`=`hod`.`dept_id` INNER JOIN `teacher` ON `teacher`.`teach_id`=`hod`.`teach_id` WHERE teacher.name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('institution/view_hod.html',teacher = res)
@app.route('/delete_hod/<h_id>/<l_id>')
def delete_hod(h_id,l_id):
    a = Db()
    qry1 = "DELETE FROM login WHERE lid='"+l_id+"'"
    res1 = a.delete(qry1)
    qry = "DELETE FROM hod WHERE hod_id='"+h_id+"' "
    res = a.delete(qry)
    return '''<script>window.location='/view_hod'</script>'''



@app.route('/manager_management')
def manager_management():
    return render_template('institution/manager_management.html')

@app.route('/mangr_mang_post', methods=['post'])
def mangr_mang_post():
    image = request.files['filefield']
    mangr_name = request.form['manager']
    dob = request.form['textfield2']
    gender = request.form['radio']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email =  request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    password = random.randint(1000,2000)

    dt = time.strftime("%Y%m%d-%H%M%S")
    image.save(staticpath +"manager_img\\"+dt+".jpg" )
    path = "/static/manager_img/"+dt+".jpg"
    a = Db()
    qry = "INSERT INTO login(`username`,`passwd`,`type`) VALUES('"+email+"','"+str(password)+"','manager')"
    res = a.insert(qry)
    qry1 = "INSERT INTO manager(`name`,`dob`,`gender`,`qualification`,`contact1`,`contact2`,`email`,`place`,`post`,`district`,`pin`,`image`,`lid`,`inst_lid`) VALUES('"+mangr_name+"','"+dob+"','"+gender+"','"+qualification+"','"+contact1+"','"+contact2+"','"+email+"','"+place+"','"+post+"','"+district+"','"+pincode+"','"+path+"','"+str(res)+"','"+str(session['login_id'])+"')"
    res1 = a.insert(qry1)

    email_subject = "Login details"
    msg = "Hello " + mangr_name + ", welcome to ExamIn online examination portal. Your username is " + email + " and password is " + str(password) + ". Use these credentials to login as manager. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[email])
    message.body = msg
    mail.send(message)
    return '''<script>window.location='/manager_management'</script>'''

@app.route('/teacher_management')
def teacher_mangement():
    a = Db()
    qry = "SELECT * FROM department"
    res = a.select(qry)
    return render_template('institution/teacher_management.html', dept=res)
@app.route('/teacher_mang_post',methods=['post'])
def teacher_mang_post():
    image = request.files['filefield']
    teacher_name = request.form['teacher']
    dob = request.form['textfield2']
    gender = request.form['radio']
    department = request.form['dept']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email =  request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    password = random.randint(1000,2000)

    dt = time.strftime("%Y%m%d-%H%M%S")
    image.save(staticpath + "teacher_img\\" + dt + ".jpg")
    path = "/static/teacher_img/"+dt+".jpg"

    a = Db()
    qry = "INSERT INTO login(`username`,`passwd`,`type`) VALUES('" + email + "','" + str(password) + "','teacher')"
    res = a.insert(qry)
    qry1 = "INSERT INTO teacher(`name`,`dept_id`,`dob`,`qualification`,`contact1`,`contact2`,`email`,`image`,`gender`,`place`,`post`,`district`,`pin`,`lid`,`inst_lid`) VALUES('"+teacher_name+"','"+department+"','"+dob+"','"+qualification+"','"+contact1+"','"+contact2+"','"+email+"','"+path+"','"+gender+"','"+place+"','"+post+"','"+district+"','"+pincode+"','"+str(res)+"','"+str(session['login_id'])+"')"
    print(qry1)
    res1 = a.insert(qry1)

    email_subject = "Login details"
    msg = "Hello " + teacher_name + ", welcome to ExamIn online examination portal. Your username is " + email + " and password is " + str(password) + ". Login with these credentials. "
    message = Message(email_subject, sender="examin06@gmail.com", recipients=[email])
    message.body = msg
    mail.send(message)
    return '''<script>window.location='/teacher_management'</script>'''

@app.route('/view_teachers')
def view_teachers():
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id WHERE inst_lid='"+str(session['login_id'])+"'"
    res = a.select(qry)
    return render_template('institution/view_teachers.html',teacher =res)
@app.route('/view_teacher_post',methods = ['post'])
def view_teacher_post():
    search = request.form['text']
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id WHERE teacher.name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('institution/view_teachers.html',teacher = res)
@app.route('/edit_teacher/<t_id>')
def edit_teacher(t_id):
    a = Db()
    qry = "SELECT * FROM teacher WHERE teach_id='"+t_id+"'"
    res = a.selectOne(qry)
    qry1= "SELECT * FROM department"
    res1 = a.select(qry1)
    return render_template('institution/edit_teacher.html',teacher=res, dept=res1)
@app.route('/edit_teacher_post',methods=['post'])
def edit_teacher_post():
    image = request.files['filefield']
    teacher_name = request.form['teacher']
    dob = request.form['textfield2']
    gender = request.form['radio']
    department = request.form['dept']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email = request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    teacher_id = request.form['t_id']

    a = Db()

    if 'filefield' in request.files:
        image = request.files['filefield']
        if image.filename != "":
            dt = time.strftime("%Y%m%d-%H%M%S")
            image.save(staticpath + "teacher_img\\" + dt + ".jpg")
            path = "/static/teacher_img/" + dt + ".jpg"

            qry = "UPDATE `teacher` SET `name`='"+teacher_name+"',`dept_id`='"+department+"',`dob`='"+dob+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`image`='"+path+"',`gender`='"+gender+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"' WHERE teach_id='"+teacher_id+"' "
            res = a.update(qry)
            return '''<script> window.location='/view_teachers'</script>'''
        else:
            qry ="UPDATE `teacher` SET `name`='"+teacher_name+"',`dept_id`='"+department+"',`dob`='"+dob+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`gender`='"+gender+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"' WHERE teach_id='"+teacher_id+"' "
            res = a.update(qry)
            return '''<script> window.location='/view_teachers'</script>'''
    else:
        qry = "UPDATE `teacher` SET `name`='"+teacher_name+"',`dept_id`='"+department+"',`dob`='"+dob+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`gender`='"+gender+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"' WHERE teach_id='"+teacher_id+"'"
        res = a.update(qry)
        return '''<script> window.location='/view_teachers'</script>'''
@app.route('/delete_teacher/<t_id>')
def delete_teacher(t_id):
    a = Db()
    qry = "DELETE FROM teacher WHERE lid='"+t_id+"' "
    res = a.delete(qry)
    qry1 = "DELETE FROM login WHERE lid='"+t_id+"' "
    res1 = a.delete(qry1)
    return '''<script> window.location='/view_teachers'</script>'''


@app.route('/change_password_inst')
def change_password_inst():
    return render_template('institution/change_password.html')
@app.route('/change_pass_inst_post',methods=['post'])
def change_pass_inst_post():
    old_pass = request.form['old_pass']
    new_pass = request.form['new_pass']
    confirm_pass = request.form['confirm_pass']
    a = Db()
    qry =  "SELECT * FROM login WHERE passwd='"+old_pass+"'"
    res = a.selectOne(qry)
    if res!=None:
        if (new_pass == confirm_pass):
            qry1 = "UPDATE login SET passwd ='" + new_pass + "' WHERE lid='" + str(session['login_id']) + "'"
            res1 = a.update(qry1)
            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('institution/change_password.html')
    else:
        return render_template('institution/change_password.html')





@app.route('/subject_management')
def subject_management():
     a = Db()
     qry = "SELECT * FROM course"
     res = a.select(qry)
     return render_template('institution/subject_management.html',subject=res)

@app.route('/sub_mang_post', methods=['post'])
def sub_mang_post():
    course_id = request.form['course']
    sub_name = request.form['subject']
    semester = request.form['sem']
    a = Db()
    qry = "INSERT INTO subject(sub_name,course_id,semester) VALUES('"+sub_name+"','"+course_id+"',"+semester+")"
    res = a.insert(qry)
    return '''<script> window.location='/subject_management'</script> '''


@app.route('/upload_notification')
def upload_notification():
    return render_template('institution/upload_notification.html')
@app.route('/upload_notif_post', methods=['post'])
def upload_notif_post():
    notification = request.form['text']
    a = Db()
    qry = "INSERT INTO notifications(`notification`,`date`,`time`,`inst_lid`) VALUES('"+notification+"',curdate(),curtime(),'"+str(session['login_id'])+"')"
    res = a.insert(qry)
    return '''<script>window.location='/upload_notification'</script> '''
@app.route('/view_uploaded_notif')
def view_uploaded_notif():
    a = Db()
    qry = "SELECT * FROM notifications"
    res = a.select(qry)
    return render_template('institution/view_uploaded_notif.html', notif =res)
@app.route('/delete_notification/<n_id>')
def delete_notification(n_id):
    a = Db()
    qry = "DELETE FROM notifications WHERE notf_id='"+n_id+"'"
    res = a.delete(qry)
    return '''<script>window.location='/view_uploaded_notif'</script>'''


@app.route('/view_complaint')
def view_complaint():
    a = Db()
    qry = "SELECT * FROM hod INNER JOIN complaint ON hod.hod_lid=complaint.lid INNER JOIN teacher ON hod.teach_id=teacher.teach_id WHERE teacher.inst_lid='"+str(session['login_id'])+"'"
    res= a.select(qry)
    return render_template('institution/view_complaint.html',complaint=res)
@app.route('/view_teacher_complaint')
def view_teacher_complaint():
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN complaint ON teacher.lid=complaint.lid WHERE teacher.inst_lid='"+str(session['login_id'])+"'"
    res= a.select(qry)
    return render_template('institution/view_teacher_complaint.html',complaint=res)
@app.route('/view_student_complaint')
def view_student_complaint():
    a = Db()
    qry = "SELECT * FROM student INNER JOIN complaint ON student.lid=complaint.lid WHERE student.inst_lid='"+str(session['login_id'])+"'"
    res= a.select(qry)
    return render_template('institution/view_student_complaint.html',complaint=res)
@app.route('/send_complaint_reply/<cid>')
def send_complaint_reply(cid):
    a = Db()
    qry = "SELECT * FROM complaint WHERE comp_id='"+cid+"'"
    res = a.selectOne(qry)
    return render_template('institution/send_reply.html', reply=res)
@app.route('/send_comp_reply_post', methods=['post'])
def send_comp_reply_post():
    comp_id = request.form['comp_id']
    reply = request.form['text']
    a = Db()
    qry = "UPDATE `complaint` SET `reply`='"+reply+"',`status`='replied' WHERE `comp_id`='"+comp_id+"'"
    res = a.update(qry)
    qry1 = "SELECT type FROM complaint WHERE comp_id='"+comp_id+"' "
    res1 = a.selectOne(qry1)
    if str(res1['type']) == "hod":
        return '''<script>window.location='/view_complaint'</script>'''
    elif str(res1['type']) == "teacher":
        return '''<script>window.location='/view_teacher_complaint'</script>'''
    else:
        return '''<script>window.location='/view_student_complaint'</script>'''




# @app.route('/view_complaint_post', methods=['post'])
# def view_complaint_post():
#     complaint_reply = request.form['text']
#     return '''<script> window.location='/view_complaint'</script> '''

@app.route('/view_profile')
def view_profile():
    a = Db()
    qry = " SELECT * FROM institution WHERE lid='"+str(session['login_id'])+"' "
    res = a.selectOne(qry)
    return render_template('institution/view_profile.html',profile = res)
@app.route('/edit_profile')
def edit_profile():
    a = Db()
    qry = " SELECT * FROM institution WHERE lid='" +str(session['login_id'])+ "' "
    res = a.selectOne(qry)
    return render_template('institution/edit_profile.html',profile=res)
@app.route('/edit_profile_post',methods=['post'])
def edit_profile_post():

        inst_name = request.form['institution']
        inst_place = request.form['place']
        inst_pin = request.form['pin']
        inst_post = request.form['post']
        inst_district = request.form['district']
        inst_contact1 = request.form['contact1']
        inst_contact2 = request.form['contact2']
        inst_email = request.form['email']
        inst_website = request.form['website']
        lid=str(session["login_id"])
        a = Db()

        if 'filefield' in request.files:
            inst_image = request.files['filefield']
            if inst_image.filename != "":
                dt = time.strftime("%Y%m%d-%H%M%S")
                inst_image.save(staticpath + "institution_img\\" + dt + ".jpg")
                path = "/static/institution_img/" + dt + ".jpg"

                qry ="UPDATE `institution` SET `image`='"+path+"',`name`='"+inst_name+"',`place`='"+inst_place+"',`pin`='"+inst_pin+"',`post`='"+inst_post+"',`district`='"+inst_district+"',`contact1`='"+inst_contact1+"',`contact2`='"+inst_contact2+"',`website`='"+inst_website+"',`email`='"+inst_email+"' WHERE lid='"+lid+"'"
                res = a.update(qry)
                print("1")
                return '''<script>window.location="/view_profile"</script>'''
            else:
                qry = "UPDATE `institution` SET `name`='" + inst_name + "',`place`='" + inst_place + "',`pin`='" + inst_pin + "',`post`='" + inst_post + "',`district`='" + inst_district + "',`contact1`='" + inst_contact1 + "',`contact2`='" + inst_contact2 + "',`website`='" + inst_website + "',`email`='" + inst_email + "' WHERE lid='" + lid + "'"
                res = a.update(qry)
                print("2")
                return '''<script>window.location='/view_profile'</script>'''
        else:
            qry = "UPDATE `institution` SET `name`='" + inst_name + "',`place`='" + inst_place + "',`pin`='" + inst_pin + "',`post`='" + inst_post + "',`district`='" + inst_district + "',`contact1`='" + inst_contact1 + "',`contact2`='" + inst_contact2 + "',`website`='" + inst_website + "',`email`='" + inst_email + "' WHERE lid='" + lid + "'"
            res = a.update(qry)
            print("3")
            return '''<script> window.location='/view_profile'</script>'''

@app.route('/i_view_students')
def i_view_students():
    a = Db()
    qry = "SELECT * FROM `student` INNER JOIN `parent` ON `parent`.`par_id`=`student`.`par_id` INNER JOIN course ON `course`.`course_id`=`student`.`course_id` WHERE inst_lid='"+str(session['login_id'])+"'"
    res = a.select(qry)
    print(qry)
    print(str(session['login_id']))
    print(res)
    return render_template('institution/students_list.html', student= res)
@app.route('/i_view_stud_post',methods=['post'])
def i_view_stud_post():
    search = request.form['text']
    a = Db()
    qry = "SELECT * FROM `student` INNER JOIN `parent` ON `parent`.`par_id`=`student`.`par_id` INNER JOIN course ON `course`.`course_id`=`student`.`course_id` WHERE inst_lid='"+str(session['login_id'])+"' AND student.name LIKE '%"+search+"%' "
    res = a.select(qry)
    return render_template('institution/students_list.html',student=res)



@app.route('/view_departments')
def view_departments():
    a = Db()
    qry= "SELECT * FROM department "
    res = a.select(qry)
    return render_template('institution/view_departments.html',dept= res)
@app.route('/view_dept_post',methods=['post'])
def view_dept_post():
    search=request.form['text']
    a=Db()
    qry="SELECT * FROM department WHERE department.dname LIKE '%"+search+"%'"
    res=a.select(qry)
    return render_template('institution/view_departments.html',dept =res)
@app.route('/edit_department/<d_id>')
def edit_department(d_id):
    a= Db()
    qry = "SELECT * FROM department WHERE dept_id='"+d_id+"'"
    res = a.selectOne(qry)
    return render_template('institution/edit_department.html', dept=res)
@app.route('/edit_dept_post', methods=['post'])
def edit_dept_post():
    dept_id = request.form['d_id']
    department = request.form['Department']
    a= Db()
    qry = "UPDATE department SET dname='"+department+"' WHERE department.dept_id='"+dept_id+"'"
    res= a.update(qry)
    return '''<script>window.location='/view_departments'</script>'''

@app.route('/delete_department/<d_id>')
def delete_department(d_id):
    a = Db()
    qry = "DELETE FROM department WHERE dept_id='"+d_id+"'"
    res = a.delete(qry)
    return '''<script> window.location='/view_departments'</script>'''


@app.route('/view_course')
def view_course():
    a= Db()
    qry = "SELECT * FROM course INNER JOIN department ON course.dept_id=department.dept_id"
    res = a.select(qry)
    return render_template('institution/view_course.html',course = res)
@app.route('/view_course_post',methods=['post'])
def view_course_post():
    search = request.form['TEXT']
    a = Db()
    qry = "SELECT * FROM course INNER JOIN department ON course.dept_id=department.dept_id WHERE course.course_name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('institution/view_course.html', course = res)

@app.route('/edit_course/<c_id>')
def edit_course(c_id):
    a = Db()

    qry1 = "SELECT * FROM `department`"
    res1 = a.select(qry1)
    qry = "SELECT * FROM course INNER JOIN department ON course.dept_id=department.dept_id  WHERE course_id='"+c_id+"'"
    res = a.selectOne(qry)
    return render_template('institution/edit_course.html', course=res, dept=res1)

@app.route('/edit_course_post', methods=['post'])
def edit_course_post():
    department = request.form['Department']
    course = request.form['Course']
    course_id = request.form['c_id']
    a = Db()
    qry = "UPDATE course SET `course_name`='"+course+"',`dept_id`='"+department+"' WHERE `course_id`='"+course_id+"'"
    print(qry)
    res = a.update(qry)
    print(res)
    return '''<script> window.location='/view_course'</script>'''

@app.route('/delete_course/<c_id>')
def delete_course(c_id):
    a = Db()
    qry = "DELETE FROM course WHERE course_id='"+c_id+"'"
    res = a.delete(qry)
    return '''<script>window.location='/view_course'</script>'''




@app.route('/view_subjects')
def view_subjects():
    a= Db()
    qry = "SELECT * FROM subject INNER JOIN course ON subject.course_id=course.course_id "
    res = a.select(qry)
    return render_template('institution/view_subjects.html',subject=res)
@app.route('/view_subj_post',methods=['post'])
def view_subj_post():
    search = request.form['TEXT']
    a =Db()
    qry = "SELECT * FROM subject INNER JOIN course ON subject.course_id=course.course_id WHERE subject.sub_name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('institution/view_subjects.html', subject =res)
@app.route('/edit_subject/<s_id>/<c_id>')
def edit_subject(s_id,c_id):
    a = Db()
    qry = "SELECT * FROM SUBJECT WHERE sub_id='"+s_id+"' "
    res = a.selectOne(qry)
    qry1 = "SELECT * FROM course "
    res1 = a.select(qry1)
    return render_template('institution/edit_subject.html',subject=res,course=res1)


@app.route('/edit_subj_post',methods=['post'])
def edit_subj_post():
    id = request.form['idd']
    course_id = request.form['course']
    subject_id = request.form['sub_id']
    subject_name = request.form['subject']
    sem = request.form['sem']
    a = Db()
    qry = "UPDATE SUBJECT SET `sub_name`='"+subject_name+"',`course_id`='"+course_id+"',semester='"+sem+"' WHERE sub_id='"+subject_id+"' "
    print(qry)
    res = a.update(qry)
    return '''<script>window.location='/view_subjects'</script>'''
@app.route('/delete_subject/<s_id>')
def delete_subject(s_id):
    a = Db()
    qry = "DELETE FROM subject WHERE sub_id='"+s_id+"'"
    res = a.delete(qry)
    return '''<script> window.location='/view_subjects'</script>'''


@app.route('/view_manager')
def view_manager():
    a= Db()
    qry = "SELECT * FROM manager"
    res= a.select(qry)
    return render_template('institution/view_manager.html',manager=res)
@app.route('/view_mang_post',methods=['post'])
def view_mang_post():
    search = request.form['text']
    a= Db()
    qry = "SELECT * FROM manager WHERE manager.name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('institution/view_manager.html',manager=res)
@app.route('/edit_manager/<m_id>')
def edit_manager(m_id):
    a = Db()
    qry = "SELECT * FROM manager WHERE manager_id='"+m_id+"'"
    res = a.selectOne(qry)
    return render_template('institution/edit_manager.html', manager=res)

@app.route('/edit_mang_post',methods=['post'])
def edit_mang_post():

    mangr_name = request.form['manager']
    dob = request.form['textfield2']
    gender = request.form['radio']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email = request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    manager_id = request.form['m_id']
    a = Db()

    if 'filefield' in request.files:
        image = request.files['filefield']
        if image.filename !="":
            dt = time.strftime("%Y%m%d-%H%M%S")
            image.save(staticpath + "manager_img\\" + dt + ".jpg")
            path = "/static/manager_img/" + dt + ".jpg"

            qry = "UPDATE `manager` SET `name`='"+mangr_name+"',`dob`='"+dob+"',`gender`='"+gender+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"',`image`='"+path+"' WHERE `manager_id`='"+manager_id+"'"
            res = a.update(qry)
            return '''<script> window.location='/view_manager'</script>'''
        else:
            qry = "UPDATE `manager` SET `name`='"+mangr_name+"',`dob`='"+dob+"',`gender`='"+gender+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"' WHERE `manager_id`='"+manager_id+"'"
            res = a.update(qry)
            return '''<script> window.location='/view_manager'</script>'''
    else:
        qry = "UPDATE `manager` SET `name`='"+mangr_name+"',`dob`='"+dob+"',`gender`='"+gender+"',`qualification`='"+qualification+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+email+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pincode+"' WHERE `manager_id`='"+manager_id+"'"
        res = a.update(qry)
        return '''<script> window.location='/view_manager'</script>'''

@app.route('/delete_manager/<m_id>')
def delete_manager(m_id):
    a = Db()
    qry = "DELETE FROM manager WHERE lid='"+m_id+"'"
    res = a.delete(qry)
    qry1 = "DELETE FROM login WHERE lid='"+m_id+"'"
    res1 = a.delete(qry1)
    return '''<script>window.location='/view_manager'</script>'''


#======================================================================MANAGER=============================================================================================================================================
@app.route('/manager_home')
def manager_home():
    a=Db()
    qry= "SELECT * FROM manager WHERE lid='"+str(session['login_id'])+"' "
    res = a.selectOne(qry)
    qry1 = "SELECT * FROM notifications"
    res1 = a.select(qry1)

    return render_template('manager/manager_home.html',manager=res, notif=res1)

@app.route('/register_student')
def register_student():
    a = Db()
    qry = "SELECT * FROM department "
    res = a.select(qry)
    qry1 = "SELECT * FROM course"
    res1 = a.select(qry1)
    return render_template('manager/register_student.html',dept=res, course=res1)
@app.route('/register_student_post',methods=['post'])
def register_student_post():
    name = request.form['textfield']
    gender = request.form['RadioGroup1']
    dob = request.form['textfield2']
    image = request.files['fileField']
    semester = request.form['Semester']
    course = request.form['course']
    place = request.form['place']
    post = request.form['post']
    district = request.form['district']
    pin = request.form['pin']
    stud_email = request.form['email2']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    parent_name = request.form['parent']
    parent_email = request.form['email']
    parent_contact = request.form['contact']
    password = random.randint(1000,2000)

    dt = time.strftime("%Y%m%d-%H%M%S")
    image.save(staticpath + "student_img\\" + dt + ".jpg")
    path = "/static/student_img/" + dt + ".jpg"

    a = Db()
    qry = "INSERT INTO login(`username`,`passwd`,`type`) VALUES('" + stud_email + "','" + str(password) + "','student')"
    res = a.insert(qry)

    qry1 =" INSERT INTO parent(`par_name`,`par_email`,`phone`) VALUES('"+parent_name+"','"+parent_email+"','"+parent_contact+"')"
    res1 = a.insert(qry1)

    mlid=str(session['login_id'])
    qry="SELECT inst_lid FROM `manager` WHERE `lid`='"+str(mlid)+"'"
    resm=a.selectOne(qry)





    qry2 = "INSERT INTO student(`name`,`image`,`gender`,`dob`,`semester`,`course_id`,`lid`,`inst_lid`,`contact1`,`contact2`,`email`,`place`,`post`,`district`,`pin`,`par_id`) VALUES('"+name+"','"+path+"','"+gender+"','"+dob+"','"+semester+"','"+course+"','"+str(res)+"','"+str(resm['inst_lid'])+"','"+contact1+"','"+contact2+"','"+stud_email+"','"+place+"','"+post+"','"+district+"','"+pin+"','"+str(res1)+"')"
    res2 = a.insert(qry2)

    email_subject = "Login details"
    msg = "Hello "+name+", welcome to ExamIn online examination portal. Your username is "+stud_email+" and password is "+str(password)+". Login with these credentials. "
    message = Message(email_subject, sender="examin06@gmail.com",recipients=[stud_email])
    message.body = msg
    mail.send(message)

    return '''<script>window.location='/register_student'</script>'''


@app.route('/m_view_students')
def m_view_students():


    a = Db()
    mlid = str(session['login_id'])
    qry = "SELECT inst_lid FROM `manager` WHERE `lid`='" + str(mlid) + "'"
    resm = a.selectOne(qry)



    qry = "SELECT * FROM `student` INNER JOIN `parent` ON `parent`.`par_id`=`student`.`par_id` INNER JOIN course ON `course`.`course_id`=`student`.`course_id` WHERE student.inst_lid='"+str(resm['inst_lid'])+"'"
    res = a.select(qry)
    return render_template('manager/view_students.html', student= res)

@app.route('/m_view_stud_post',methods=['post'])
def m_view_stud_post():
    search = request.form['text']
    a = Db()
    mlid = str(session['login_id'])
    qrym = "SELECT inst_lid FROM `manager` WHERE `lid`='" + str(mlid) + "'"
    resm = a.selectOne(qrym)
    qry = "SELECT * FROM `student` INNER JOIN `parent` ON `parent`.`par_id`=`student`.`par_id` INNER JOIN course ON `course`.`course_id`=`student`.`course_id` WHERE inst_lid='"+str(resm['inst_lid'])+"' AND student.name LIKE '%"+search+"%' "
    res = a.select(qry)
    return render_template('manager/view_students.html',student=res)
@app.route('/m_edit_student/<s_id>')
def m_edit_student(s_id):
    a= Db()
    qry1 = "SELECT * FROM course"
    res1 = a.select(qry1)
    qry = "SELECT student.*,course.course_name,parent.* FROM `student` INNER JOIN `parent` ON `parent`.`par_id`=`student`.`par_id` INNER JOIN course ON `course`.`course_id`=`student`.`course_id` WHERE stud_id='"+s_id+"'"
    res = a.selectOne(qry)
    return render_template('manager/edit_student.html',student= res,res1=res1)
@app.route('/m_edit_student_post',methods=['post'])
def m_edit_student_post():
    name = request.form['textfield']
    gender = request.form['RadioGroup1']
    dob = request.form['textfield2']
    semester = request.form['Semester']
    course_id = request.form['course']
    place = request.form['place']
    post = request.form['post']
    district = request.form['district']
    pin = request.form['pin']
    stud_email = request.form['email2']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    stud_id = request.form['s_id']
    parent_id = request.form['p_id']
    parent_name = request.form['parent']
    parent_email = request.form['email']
    parent_contact = request.form['contact']
    a = Db()
    if 'fileField' in request.files:
        image = request.files['fileField']
        if image.filename !="":
            dt = time.strftime("%Y%m%d-%H%M%S")
            image.save(staticpath + "student_img\\" + dt + ".jpg")
            path = "/static/student_img/" + dt + ".jpg"

            qry = "UPDATE parent SET `par_name`='"+parent_name+"',`par_email`='"+parent_email+"',`phone`='"+parent_contact+"' WHERE par_id='"+parent_id+"'"
            res= a.update(qry)
            qry1 = "UPDATE `student` SET `name`='"+name+"',`image`='"+path+"',`gender`='"+gender+"',`dob`='"+dob+"',`semester`='"+semester+"',`course_id`='"+course_id+"',`contact1`='"+contact1+"',`contact2`='"+contact2+"',`email`='"+stud_email+"',`place`='"+place+"',`post`='"+post+"',`district`='"+district+"',`pin`='"+pin+"',`par_id`='"+parent_id+"' WHERE stud_id='"+stud_id+"'"
            res1 = a.update(qry1)
            return '''<script> window.location='/m_view_students'</script> '''
        else:
            qry = "UPDATE parent SET `par_name`='" + parent_name + "',`par_email`='" + parent_email + "',`phone`='" + parent_contact + "' WHERE par_id='" + parent_id + "'"
            res = a.update(qry)
            qry1 = "UPDATE `student` SET `name`='" + name + "',`gender`='" + gender + "',`dob`='" + dob + "',`semester`='" + semester + "',`course_id`='" + course_id + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + stud_email + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pin + "',`par_id`='" + parent_id + "' WHERE stud_id='" + stud_id + "'"
            res1 = a.update(qry1)
            return '''<script> window.location='/m_view_students'</script> '''
    else:
        qry = "UPDATE parent SET `par_name`='" + parent_name + "',`par_email`='" + parent_email + "',`phone`='" + parent_contact + "' WHERE par_id='" + parent_id + "'"
        res = a.update(qry)
        qry1 = "UPDATE `student` SET `name`='" + name + "',`gender`='" + gender + "',`dob`='" + dob + "',`semester`='" + semester + "',`course_id`='" + course_id + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + stud_email + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pin + "',`par_id`='" + parent_id + "' WHERE stud_id='" + stud_id + "'"
        res1 = a.update(qry1)
        return '''<script> window.location='/m_view_students'</script> '''

@app.route('/m_delete_student/<s_id>/<p_id>/<l_id>')
def m_delete_student(s_id,p_id,l_id):
    a = Db()
    qry = "DELETE FROM student WHERE stud_id='"+s_id+"' "
    res = a.delete(qry)

    qry1 = " DELETE FROM parent WHERE par_id='"+p_id+"' "
    res1 = a.delete(qry1)

    qry2 = "DELETE FROM login WHERE lid='"+l_id+"' "
    res2 = a.delete(qry2)
    return '''<script> window.location='/m_view_students'</script>'''






@app.route('/m_view_hod')
def m_view_hod():
    a =Db()
    qry = "SELECT teacher.*,department.* FROM `department` INNER JOIN `hod` ON `department`.`dept_id`=`hod`.`dept_id` INNER JOIN `teacher` ON `teacher`.`teach_id`=`hod`.`teach_id` INNER JOIN manager ON manager.inst_lid=hod.lid WHERE manager.lid='"+str(session['login_id'])+"'"
    print(qry)
    res = a.select(qry)
    return render_template('manager/view_hod.html', teacher=res)
@app.route('/m_view_hod_post',methods = ['post'])
def m_view_hod_post():
    search = request.form['text']
    a = Db()
    qry = "SELECT * FROM `department` INNER JOIN `hod` ON `department`.`dept_id`=`hod`.`dept_id` INNER JOIN `teacher` ON `teacher`.`teach_id`=`hod`.`teach_id` WHERE teacher.name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('manager/view_hod.html',teacher = res)


@app.route('/m_view_teachers')
def m_view_teachers():
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id"
    res = a.select(qry)
    return render_template('manager/view_teachers.html',teacher =res)
@app.route('/m_view_teacher_post',methods = ['post'])
def m_view_teacher_post():
    search = request.form['text']
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id WHERE teacher.name LIKE '%"+search+"%'"
    res = a.select(qry)
    return render_template('manager/view_teachers.html',teacher = res)

@app.route('/m_notification')
def m_notification():
    a= Db()
    qry = "SELECT * FROM notifications WHERE inst_lid IN(SELECT `inst_lid` FROM manager WHERE `lid`='"+str(session['login_id'])+"'  )"
    res = a.select(qry)
    return render_template('manager/notification.html',notification=res)

@app.route('/m_send_review')
def m_send_review():
    return render_template('manager/review.html')
@app.route('/m_send_rev_post',methods=['post'])
def m_send_rev_post():
    review = request.form['textarea']
    a =Db()
    qry = "INSERT INTO review(`lid`,`review`,`date`,`time`) VALUES('"+str(session['login_id'])+"','"+review+"',curdate(),curtime())"
    res = a.insert(qry)
    return '''<script> window.location='/m_send_review'</script>'''
@app.route('/m_view_profile')
def m_view_profile():
    a = Db()
    qry = "SELECT * FROM manager WHERE lid ='"+str(session['login_id'])+"'"
    res = a.selectOne(qry)
    return render_template('manager/manager_view_profile.html',profile=res)
@app.route('/m_edit_profile')
def m_edit_profile():
    a = Db()
    qry = "SELECT * FROM manager WHERE lid='"+str(session['login_id'])+"'"
    res= a.selectOne(qry)
    return render_template('manager/manager_edit_profile.html', manager = res)
@app.route('/m_edit_profile_post',methods=['post'])
def m_edit_profile_post():
    mangr_name = request.form['manager']
    dob = request.form['textfield2']
    gender = request.form['radio']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email = request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    a =Db()

    if 'filefield' in request.files:
        image = request.files['filefield']
        if image.filename != "":
            dt = time.strftime("%Y%m%d-%H%M%S")
            image.save(staticpath + "manager_img\\" + dt + ".jpg")
            path = "/static/manager_img/" + dt + ".jpg"

            qry = "UPDATE `manager` SET `name`='" + mangr_name + "',`dob`='" + dob + "',`gender`='" + gender + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "',`image`='" + path + "' WHERE `lid`='" + str(session['login_id']) + "'"
            res = a.update(qry)
            return '''<script> window.location='/m_view_profile'</script>'''
        else:
            qry = "UPDATE `manager` SET `name`='" + mangr_name + "',`dob`='" + dob + "',`gender`='" + gender + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "' WHERE `lid`='" + str(session['login_id']) + "'"
            res = a.update(qry)
            return '''<script> window.location='/m_view_profile'</script>'''
    else:
        qry = "UPDATE `manager` SET `name`='" + mangr_name + "',`dob`='" + dob + "',`gender`='" + gender + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "' WHERE `lid`='" + str(session['login_id']) + "'"
        res = a.update(qry)
        return '''<script> window.location='/m_view_profile'</script>'''


@app.route('/m_change_password')
def m_change_password():
    return render_template('manager/change_password.html')
@app.route('/m_change_pass_post',methods=['post'])
def m_change_pass_post():

    old_password = request.form['old_pass']
    new_password = request.form['new_pass']
    confirm_password = request.form['confirm_pass']

    a = Db()
    qry = "SELECT * FROM login WHERE passwd='"+old_password+"'"
    res= a.selectOne(qry)
    if res!=None:

        if(new_password==confirm_password):

            qry1="UPDATE login SET passwd ='"+new_password+"' WHERE lid='"+str(session['login_id'])+"'"
            res1=a.update(qry1)

            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('manager/change_password.html')
    else:
        return render_template('manager/change_password.html')








#========================================================================================================HOD======================================================================================================================
@app.route('/hod_home')
def hod_home():
    a=Db()
    qry = " SELECT * FROM hod INNER JOIN teacher ON hod.teach_id=teacher.teach_id WHERE hod_lid='"+str(session['login_id'])+ "' "
    res = a.selectOne(qry)
    qry1 = "SELECT * FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id"
    res1 = a.select(qry1)
    qry2 = "SELECT * FROM notifications"
    res2 = a.select(qry2)
    return render_template('hod/hod_home.html',hod=res, exam=res1, notif=res2)

@app.route('/hod_view_profile')
def hod_view_profile():
    a = Db()
    qry = "SELECT * FROM teacher INNER JOIN hod ON hod.teach_id=teacher.teach_id INNER JOIN department ON teacher.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    print(qry)
    res = a.selectOne(qry)
    return render_template('hod/view_profile.html',hod= res)

@app.route('/hod_edit_profile')
def hod_edit_profile():
    a = Db()
    qry1 = "SELECT * FROM department"
    res1=a.select(qry1)
    qry = "SELECT * FROM teacher INNER JOIN hod ON hod.teach_id=teacher.teach_id INNER JOIN department ON teacher.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    res = a.selectOne(qry)
    return render_template('hod/edit_profile.html',teacher=res,dept=res1)
@app.route('/hod_edit_profile_post',methods=['post'])
def hod_edit_profile_post():
    teacher_name = request.form['teacher']
    dob = request.form['textfield2']
    gender = request.form['radio']
    department = request.form['dept']
    qualification = request.form['qualification']
    contact1 = request.form['contact1']
    contact2 = request.form['contact2']
    email = request.form['email']
    place = request.form['adrs1']
    post = request.form['adr2']
    district = request.form['adr3']
    pincode = request.form['adrs4']
    teacher_id = request.form['t_id']

    a = Db()

    if 'filefield' in request.files:
        image = request.files['filefield']
        if image.filename != "":
            dt = time.strftime("%Y%m%d-%H%M%S")
            image.save(staticpath + "teacher_img\\" + dt + ".jpg")
            path = "/static/teacher_img/" + dt + ".jpg"

            qry = "UPDATE `teacher` SET `name`='" + teacher_name + "',`dept_id`='" + department + "',`dob`='" + dob + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`image`='" + path + "',`gender`='" + gender + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "' WHERE teach_id='" + teacher_id + "' "
            res = a.update(qry)
            return '''<script>window.location='/hod_view_profile'</script>'''
        else:
            qry = "UPDATE `teacher` SET `name`='" + teacher_name + "',`dept_id`='" + department + "',`dob`='" + dob + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`gender`='" + gender + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "' WHERE teach_id='" + teacher_id + "' "
            res = a.update(qry)
            return '''<script> window.location='/hod_view_profile'</script>'''
    else:
        qry = "UPDATE `teacher` SET `name`='" + teacher_name + "',`dept_id`='" + department + "',`dob`='" + dob + "',`qualification`='" + qualification + "',`contact1`='" + contact1 + "',`contact2`='" + contact2 + "',`email`='" + email + "',`gender`='" + gender + "',`place`='" + place + "',`post`='" + post + "',`district`='" + district + "',`pin`='" + pincode + "' WHERE teach_id='" + teacher_id + "'"
        res = a.update(qry)
        return '''<script> window.location='/hod_view_profile'</script>'''


@app.route('/hod_subject_allocation')
def hod_subject_allocation():
    a= Db()
    qry = "SELECT * FROM department INNER JOIN course ON department.dept_id=course.dept_id INNER JOIN hod ON hod.dept_id=department.dept_id WHERE `hod`.`hod_lid`='"+str(session['login_id'])+"' "
    res = a.select(qry)
    qry1= "SELECT * FROM SUBJECT INNER JOIN course ON course.course_id=subject.course_id INNER JOIN department ON department.dept_id=course.dept_id INNER JOIN hod ON hod.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    res1= a.select(qry1)
    qry2= "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id INNER JOIN hod ON hod.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    res2= a.select(qry2)
    qry3 = "SELECT * FROM course INNER JOIN department ON department.dept_id=course.dept_id INNER JOIN hod ON hod.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    print(qry3)
    res3 = a.select(qry3)
    return render_template('hod/subject_allocation.html',alloc=res,subject=res1,teacher=res2,course=res3)
@app.route('/hod_sub_alloc_post', methods=['post'])
def hod_sub_alloc_post():
    subject_id=request.form['subject']
    teach_id=request.form['teacher']
    a= Db()
    qry = "INSERT INTO sub_alloc(`teach_id`,`sub_id`) VALUES('"+teach_id+"','"+subject_id+"')"
    res = a.insert(qry)
    return '''<script>window.location='/hod_subject_allocation'</script>'''

@app.route('/hod_view_allocated_subject')
def hod_view_allocated_subject():
    a=Db()
    qry = "SELECT * FROM sub_alloc INNER JOIN SUBJECT ON sub_alloc.sub_id=subject.sub_id INNER JOIN teacher ON teacher.teach_id=sub_alloc.teach_id INNER JOIN course ON course.course_id=subject.course_id WHERE subject.course_id IN(SELECT course_id FROM course WHERE dept_id IN (SELECT dept_id FROM hod WHERE hod_lid='"+str(session['login_id'])+"' ))"
    res = a.select(qry)
    return render_template('hod/view_allocated_subject.html',alloc=res)
@app.route('/hod_edit_allocated_sub/<a_id>')
def hod_edit_allocated_sub(a_id):
    a = Db()
    qry = "SELECT * FROM sub_alloc INNER JOIN SUBJECT ON sub_alloc.sub_id=subject.sub_id INNER JOIN teacher ON teacher.teach_id=sub_alloc.teach_id INNER JOIN course ON course.course_id=subject.course_id WHERE subject.course_id IN(SELECT course_id FROM course WHERE dept_id IN (SELECT dept_id FROM hod WHERE hod_lid='"+str(session['login_id'])+"' ))  AND sub_alloc.alloc_id='"+a_id+"' "
    res = a.selectOne(qry)
    print(qry)
    qry3= "SELECT * FROM course"
    res3=a.select(qry3)

    qry1 = "SELECT * FROM subject"
    res1 = a.select(qry1)
    qry2 = "SELECT * FROM teacher"
    res2 = a.select(qry2)
    return render_template('hod/edit_allocated_subject.html',res=res,alloc =a_id,subject=res1,teacher=res2,course=res3)
@app.route('/hod_sub_alloc_edit_post', methods=['post'])
def hod_sub_alloc_edit_post():
    id = request.form['idd']
    subject_id=request.form['subject']
    teach_id=request.form['teacher']
    a= Db()
    qry = "UPDATE sub_alloc SET `teach_id`='"+teach_id+"',`sub_id`='"+subject_id+"' WHERE `alloc_id`='"+str(id)+"' "
    res = a.update(qry)
    return '''<script>window.location='/hod_view_allocated_subject'</script>'''
@app.route('/hod_delete_allocated_sub/<a_id>')
def hod_delete_allocated_sub(a_id):
    a = Db()
    qry = "DELETE FROM sub_alloc WHERE alloc_id='"+a_id+"'"
    res = a.delete(qry)
    return '''<script>window.location='/hod_view_allocated_subject'</script>'''

@app.route('/hod_view_teachers')
def hod_view_teachers():
    a= Db()
    qry1 = "SELECT hod.dept_id AS dept FROM department INNER JOIN hod ON hod.dept_id=department.dept_id WHERE hod.hod_lid='"+str(session['login_id'])+"'"
    res1 = a.selectOne(qry1)

    qry = "SELECT * FROM teacher INNER JOIN department ON department.dept_id=teacher.dept_id WHERE department.dept_id='"+str(res1['dept'])+"'"
    res =a.select(qry)
    return render_template('hod/view_teachers.html',teacher=res)
@app.route('/hod_view_teacher_post',methods=['post'])
def hod_view_teacher_post():
    search = request.form['search']
    a = Db()
    qry = "SELECT * FROM teacher WHERE teacher.name LIKE '%"+search+"%' "
    res= a.select(qry)
    return render_template('hod/view_teachers.html',teacher=res)

@app.route('/hod_scheduled_exams')
def hod_scheduled_exams():
    a= Db()
    qry = "SELECT * FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id"
    res = a.select(qry)
    return render_template('hod/scheduled_exams.html',exam=res)

@app.route('/hod_view_result/<examid>')
def hod_view_result(examid):
    a= Db()
    qry = "SELECT * FROM exam INNER JOIN results ON exam.exam_id=results.exam_id INNER JOIN student ON student.stud_id=results.stud_id INNER JOIN SUBJECT ON subject.sub_id=exam.sub_id WHERE results.exam_id='"+examid+"'"
    res = a.select(qry)
    return render_template('hod/view_results.html',result=res)

@app.route('/hod_send_complaint')
def hod_send_complaint():
    return render_template('hod/complaint.html')
@app.route('/hod_complaint_post',methods=['post'])
def hod_complaint_post():
    complaint = request.form['text']
    a = Db()
    qry = "INSERT INTO `complaint` (`lid`,`type`,`complaint`,`reply`,`date`,`time`,`status`) VALUES ('"+str(session['login_id'])+"','hod','"+complaint+"','pending',CURDATE(),CURTIME(),'pending')"
    res= a.insert(qry)
    return '''<script>window.location='/hod_send_complaint'</script>'''

@app.route('/hod_view_reply')
def hod_view_reply():
    a=Db()
    qry = "SELECT * FROM complaint WHERE lid='" + str(session['login_id']) + "'"
    res=a.select(qry)
    print(qry)
    return render_template('hod/view_reply.html',reply=res)


@app.route('/hod_view_notif')
def hod_view_notif():
    a = Db()
    qry = "SELECT * FROM notifications"
    res = a.select(qry)
    return render_template('hod/view_notification.html', notif=res)

@app.route('/hod_change_password')
def hod_change_password():
    return render_template('hod/change_password.html')
@app.route('/hod_change_pass_post',methods=['post'])
def hod_change_pass_post():

    old_password = request.form['old_pass']
    new_password = request.form['new_pass']
    confirm_password = request.form['confirm_pass']

    a = Db()
    qry = "SELECT * FROM login WHERE lid='"+str(session['login_id'])+"' AND passwd='"+old_password+"'"
    print(qry)
    res= a.selectOne(qry)
    if res is not None:

        if(new_password==confirm_password):

            qry1="UPDATE login SET passwd ='"+new_password+"' WHERE lid='"+str(session['login_id'])+"'"
            res1=a.update(qry1)

            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('hod/change_password.html')
    else:
        return render_template('hod/change_password.html')


#============================================================================================================TEACHER================================================================================================================


@app.route('/t_home_teacher')
def t_home_teacher():
    a=Db()
    qry="SELECT * FROM teacher WHERE lid='"+str(session['login_id'])+"' "
    res = a.selectOne(qry)
    qry1 = "SELECT * FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id"
    res1 = a.select(qry1)
    qry2 = "SELECT * FROM notifications"
    res2 = a.select(qry2)
    return render_template('teacher/home_teacher.html',teacher=res, exam=res1, notif=res2)






@app.route('/t_upload_exam/<examid>')
def t_upload_exam(examid):

    session["examid"]=examid


    return render_template('teacher/upload_exam.html')

@app.route('/t_upload_exam_post', methods=['post'])
def t_upload_exam_post():
    Question = request.form["textfield2"]
    Option1 = request.form["textfield3"]
    Option2 = request.form["textfield4"]
    Option3 = request.form["textfield6"]
    Option4 = request.form["textfield7"]
    Answer = request.form["textfield8"]
    examid= session["examid"]


    qry = "INSERT INTO `questions`(`question`,`option1`,`option2`,`option3`,`option4`,`answer`,examid) VALUES('"+Question+"','"+Option1+"','"+Option2+"','"+Option3+"','"+Option4+"','"+Answer+"','"+examid+"')"

    db = Db()
    res = db.insert(qry)
    return "<script>window.location='/t_upload_exam/"+examid+"'</script>"






@app.route('/t_view_exam_question/<id>')
def t_view_exam_question(id):

    qry = "SELECT * FROM questions where examid='"+id+"'"

    db = Db()
    res = db.select(qry)
    return render_template('teacher/view_exam.html', res=res)


@app.route('/t_delete_exam_question/<id>')
def t_delete_exam_question(id):

    qry = "DELETE  FROM `questions` WHERE qid='"+id+"'"

    db = Db()
    res = db.delete(qry)

    return '''<script>window.location='t_view_exam_question'</script>'''




@app.route('/t_edit_exam/<id>')
def t_edit_exam(id):

    qry = "SELECT * FROM exam WHERE exam_id='"+id+"'"

    db = Db()
    res = db.selectOne(qry)
    return render_template('teacher/edit_exam.html', res=res)



@app.route('/t_edit_exam_question/<id>')
def t_edit_exam_question(id):

    session["exam_id"]=id

    qry = "SELECT * FROM questions WHERE qid='"+id+"'"

    db = Db()
    res = db.selectOne(qry)
    return render_template('teacher/edit_exam_questions.html', res=res)


@app.route('/t_edit_exam_post', methods=['post'])
def t_edit_exam_post():
        Question = request.form["textfield2"]
        Option1 = request.form["textfield3"]
        Option2 = request.form["textfield4"]
        Option3 = request.form["textfield6"]
        Option4 = request.form["textfield7"]
        Answer = request.form["textfield8"]
        examid = session["exam_id"]
        q_id = request.form["qid"]

        qry = "UPDATE questions SET `question`='"+Question+"',`option1`='"+Option1+"',`option2`='"+Option2+"',`option3`='"+Option3+"',`option4`='"+Option4+"',`answer`='"+Answer+"' WHERE qid='"+q_id+"'"

        db = Db()
        res = db.update(qry)

        return "<script>window.location='/t_edit_exam_question/"+examid+"'</script>"
        #return render_template('teacher/upload_exam.html')



@app.route('/t_upload_viva_result')
def t_upload_viva_result():
    return render_template('teacher/upload_viva_result.html')

@app.route('/t_upload_viva_result_post', methods=['post'])
def t_upload_viva_result_post():
    upload = request.form["Upload"]
    reset = request.form["Reset"]
    return '''<script>window.loaction='t_upload_viva_result'/</script>'''



@app.route('/t_change_password')
def t_change_password():
    return render_template('teacher/change_password.html')

@app.route('/teacher_change_pass_post',methods=['post'])
def teacher_change_pass_post():

    old_password = request.form['old']
    new_password = request.form['new']
    confirm_password = request.form['retype_new']

    a = Db()
    qry = "SELECT * FROM login WHERE lid='"+str(session['login_id'])+"' AND passwd='"+old_password+"'"
    print(qry)
    res= a.selectOne(qry)
    if res is not None:

        if(new_password==confirm_password):

            qry1="UPDATE login SET passwd ='"+new_password+"' WHERE lid='"+str(session['login_id'])+"'"
            res1=a.update(qry1)

            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('teacher/change_password.html')
    else:
        return render_template('teacher/change_password.html')




@app.route('/t_change_password_post', methods=['post'])
def t_change_password_post():
    newpassword = request.form["new"]
    retypepassword = request.form["retype_new"]
    change = request.form["change"]
    reset = request.form["reset"]
    return '''<script>alert('password changed');window.loaction='/login'</script>'''



# @app.route('/t_view_complaint')
# def t_view_complaint():
#     return render_template('teacher/view_complaint.html')



@app.route('/view_allocated_subject')
def view_allocated_subject():
    a= Db()
    qry ="SELECT subject.* ,department.dname  FROM SUBJECT,`course`,`department`,`teacher`,`sub_alloc` WHERE `sub_alloc`.`sub_id`=`subject`.`sub_id` AND `sub_alloc`.`teach_id`=`teacher`.`teach_id`  AND `subject`.`course_id`=`course`.`course_id` AND `course`.`dept_id`=`department`.`dept_id`  AND `teacher`.`lid`='"+str(session["login_id"])+"'"
    res = a.select(qry)
    return render_template('teacher/view_allocated_subject.html',res=res)



@app.route('/view_notification')
def view_notification():
    qry="SELECT * FROM notifications WHERE `inst_lid` IN (SELECT `inst_lid` FROM `teacher` WHERE `lid`='"+str(session['login_id'])+"')"
    db=Db()
    res=db.select(qry)
    return render_template('teacher/view_notification.html',res=res)



@app.route('/teacher_view_profile')
def teacher_view_profile():
    qry="SELECT teacher.*,`department`.`dname` FROM teacher,department  WHERE lid='"+str(session["login_id"])+"' and `department`.`dept_id`=`teacher`.`dept_id`"
    db=Db()
    res=db.selectOne(qry)
    return render_template('teacher/view_teacher_profile.html',res=res)





@app.route('/t_send_complaint')
def t_send_complaint():
    return render_template('teacher/send_student_complaint.html')

@app.route('/t_send_complaint_post', methods=['post'])
def t_send_complaint_post():
    complaint = request.form["Complaint"]
    qry = "INSERT INTO `complaint` (`lid`,`type`,`complaint`,`reply`,`date`,`time`,`status`) VALUES ('"+str(session['login_id'])+"','teacher','"+complaint+"','pending',CURDATE(),CURTIME(),'pending')"
    db = Db()
    res = db.insert(qry)

    return "<script>window.location='/t_send_complaint'</script>"



@app.route('/t_view_complaint')
def t_view_complaint():
    db = Db()
    qry = "SELECT * FROM complaint WHERE lid='"+str(session['login_id'])+"'"
    resa = db.select(qry)
    return render_template('teacher/view_complaint.html', a=resa)



@app.route('/view_results/<examid>')
def view_results(examid):
    a = Db()
    qry = "SELECT * FROM exam INNER JOIN results ON exam.exam_id=results.exam_id INNER JOIN student ON student.stud_id=results.stud_id WHERE results.exam_id='"+examid+"'"
    print(qry)
    res = a.select(qry)
    return render_template('teacher/view_results.html',result =res)

@app.route('/indiv_results')
def indiv_results():
    a = Db()
    qry = " SELECT student.name AS name,stud_id FROM student INNER JOIN course ON course.course_id=student.course_id INNER JOIN teacher ON course.dept_id=teacher.dept_id WHERE teacher.lid='"+str(session['login_id'])+"' "
    res = a.select(qry)
    return render_template('teacher/indiv_results.html', student=res)

@app.route('/indiv_results_sub/<stud_id>')
def indiv_results_sub(stud_id):
    a = Db()
    qry = "SELECT * FROM results INNER JOIN student ON results.stud_id=student.stud_id INNER JOIN exam ON exam.exam_id=results.exam_id INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id WHERE student.stud_id='"+stud_id+"'"
    res = a.select(qry)
    return render_template('teacher/indiv_results_sub.html', result=res)


@app.route('/t_exam_notification')
def t_exam_notification():

    qry = "SELECT subject.* FROM SUBJECT,`teacher`,`sub_alloc` WHERE `sub_alloc`.`sub_id`=`subject`.`sub_id` AND `sub_alloc`.`teach_id`=`teacher`.`teach_id` AND `teacher`.`lid`='"+str(session["login_id"])+"'"
    db = Db()
    res = db.select(qry)
    return render_template('teacher/exam_notification.html',res=res)


@app.route('/t_exam_notif_post', methods=['post'])
def t_exam_notif_post():
    subject = request.form["select"]
    exam = request.form["textfield3"]
    date = request.form["textfield4"]
    time = request.form["textfield5"]
    portions = request.form["textarea"]
    type = request.form["type"]

    qry = "INSERT INTO exam (`sub_id`,`exam_name`,`exam_date`,`exam_time`,`portions`,`teach_lid`,`type`) VALUES ('"+subject+"','"+exam+"','"+date+"','"+time+"','"+portions+"','"+str(session['login_id'])+"','"+type+"')"
    db = Db()
    res = db.insert(qry)

    qry1 = " SELECT course.course_id AS course_id FROM teacher INNER JOIN sub_alloc ON teacher.teach_id=sub_alloc.teach_id INNER JOIN course ON teacher.dept_id=course.dept_id INNER JOIN SUBJECT ON subject.course_id=course.course_id WHERE teacher.lid='"+str(session['login_id'])+"' "
    res1 = db.selectOne(qry1)
    qry2 = " SELECT email FROM student WHERE course_id='"+str(res1['course_id'])+"' "
    res2 = db.select(qry2)
    qry3 = "SELECT sub_name FROM subject WHERE sub_id='"+subject+"'"
    res3 = db.selectOne(qry3)
    emails = []
    for dic in res2:
        for val in dic.values():
            emails.append(val)
            print(val)
    print(emails)

    for i in emails:
        email_subject = "Exam Notification"
        msg = "You have "+type+" type "+exam+" exam for "+str(res3['sub_name'])+" on "+date+" at "+time+". Portions for the exam will be "+portions+". Prepare for the exam and attend them on time. "
        message = Message(email_subject, sender="examin06@gmail.com", recipients=[i])
        message.body = msg
        mail.send(message)

    return '''<script>window.location='/t_exam_notification'</script>'''


@app.route('/t_exam_notification_view')
def t_exam_notification_view():
    qry = "SELECT exam.*,subject.* FROM exam,SUBJECT,sub_alloc ,`teacher` WHERE `exam`.`sub_id`=`subject`.`sub_id` AND `subject`.`sub_id`=`sub_alloc`.`sub_id`  AND `sub_alloc`.`teach_id`=`teacher`.`teach_id` AND `teacher`.`lid`='" + str(session["login_id"]) + "'"
    db = Db()
    res = db.select(qry)
    return render_template('teacher/exam_notification_view.html', res=res)



@app.route('/t_edit_exam_notification_view/<id>')
def t_edit_exam_notification_view(id):
    db = Db()
    qry = "SELECT * FROM exam,subject WHERE exam_id='"+id+"' "
    res = db.selectOne(qry)
    qry1 = "SELECT exam.*,subject.sub_name FROM exam,SUBJECT,sub_alloc ,`teacher` WHERE `exam`.`sub_id`=`subject`.`sub_id` AND `subject`.`sub_id`=`sub_alloc`.`sub_id`  AND `sub_alloc`.`teach_id`=`teacher`.`teach_id` AND `teacher`.`lid`='" + str(session["login_id"]) + "'"
    db = Db()
    resa = db.select(qry1)

    return render_template('teacher/edit_exam_notification.html', data=res, subject=resa)


@app.route('/t_exam_notif_view_post', methods=['post'])
def t_exam_notif_view_post():
    exam_id = request.form['exam_id']
    subject = request.form["textfield"]
    exam = request.form["textfield2"]
    time = request.form["textfield3"]
    date = request.form["textfield4"]
    portions = request.form["textfield5"]

    qry = "UPDATE exam SET `sub_id`='"+subject+"', `exam_name`='"+exam+"',`exam_date`='"+date+"',`exam_time`='"+time+"',`portions`='"+portions+"' WHERE `exam_id`='"+exam_id+"'"


    db = Db()
    res = db.update(qry)
    return redirect('/t_exam_notification_view')

@app.route('/delete_exam/<eid>')
def delete_exam(eid):
    a = Db()
    qry = " DELETE FROM exam WHERE exam_id='"+eid+"' "
    res = a.delete(qry)
    return redirect('/t_exam_notification_view')



@app.route('/t_review')
def t_review():
    return render_template('teacher/review.html')

@app.route('/t_review_post', methods=['post'])
def t_review_post():
    review = request.form["textarea"]
    qry="INSERT INTO review (`lid`,`review`,`date`,`time`) VALUES ('"+str(session['login_id'])+"','"+review+"',curdate(),curtime())"
    db = Db()
    res = db.insert(qry)
    return '''<script> window.location='/t_review'</script>'''

@app.route('/t_view_students/<examid>')
def t_view_students(examid):

    session["examid"]=examid


    a = Db()
    mlid = str(session['login_id'])
    qry = "SELECT inst_lid,teach_id FROM `teacher` WHERE `lid`='" + str(mlid) + "'"
    resm = a.selectOne(qry)

    qry2 = "SELECT sub_id FROM teacher INNER JOIN sub_alloc ON sub_alloc.teach_id=teacher.teach_id WHERE teacher.teach_id='"+str(resm['teach_id'])+"'"
    res2 = a.selectOne(qry2)



    qry1 = "SELECT * FROM student INNER JOIN course ON course.course_id=student.course_id INNER JOIN SUBJECT ON subject.course_id=student.course_id WHERE subject.sub_id='"+str(res2['sub_id'])+"' "
    print(qry1)
    res = a.select(qry1)
    return render_template('teacher/view_students.html', student= res)




#=====================================================================================================STUDENT============================================================================================================================================



@app.route('/st_home_student')
def st_home_student():
    a= Db()
    qry = "SELECT * FROM student WHERE lid='"+str(session['login_id'])+"' "
    res = a.selectOne(qry)
    qry1 = "SELECT * FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id"
    res1 = a.select(qry1)
    qry2 = "SELECT * FROM notifications"
    res2 = a.select(qry2)
    return render_template('student/student_home.html',student=res, exam=res1, notif=res2)



@app.route('/st_view_profile')
def st_view_profile():
    qry="SELECT `student`.*,`parent`.`par_name`,`parent`.`par_email`,`parent`.`phone`,`department`.`dname`,`course`.`course_name`  FROM student,parent,department,course  WHERE `course`.`course_id`=`student`.`course_id` AND `department`.`dept_id`=`course`.`dept_id` AND `parent`.`par_id`=`student`.`par_id` and student.lid='"+str(session['login_id'])+"'"
    print(qry)
    db = Db()
    res = db.selectOne(qry)
    return render_template('student/view_student_profile.html', res=res)



@app.route('/st_send_complaint')
def st_send_complaint():
    return render_template('student/send_student_complaint.html')

@app.route('/st_send_complaint_post', methods=['post'])
def st_send_complaint_post():
    complaint = request.form["Complaint"]
    qry = "INSERT INTO `complaint` (`lid`,`type`,`complaint`,`reply`,`date`,`time`,`status`) VALUES ('"+str(session['login_id'])+"','student','"+complaint+"','pending',CURDATE(),CURTIME(),'pending')"
    db = Db()
    res = db.insert(qry)

    return "<script>window.location='/st_send_complaint'</script>"



@app.route('/st_view_complaint')
def st_view_complaint():
    db = Db()
    qry = "SELECT * FROM complaint WHERE lid='"+str(session['login_id'])+"'"
    resa = db.select(qry)


    return render_template('student/view_complaint.html', a=resa)



@app.route('/st_view_notification')
def st_view_notification():

    db = Db()


    qry = "SELECT `notifications`.* FROM `notifications` INNER JOIN `student` ON `notifications`.`inst_lid`=`student`.`inst_lid` WHERE `student`.`lid`='"+str(session["login_id"])+"'"
    res = db.select(qry)

    return render_template('student/view_notification.html', res=res)



@app.route('/st_view_subjects')
def st_view_subjects():
    a= Db()
    qry = "SELECT * FROM student INNER JOIN SUBJECT ON student.course_id=subject.course_id WHERE lid='"+str(session['login_id'])+"'"
    res=a.select(qry)
    return render_template('student/view_subjects.html' ,subject=res)

@app.route('/st_attend_exam')
def st_attend_exam():
    a= Db()
    qry = "SELECT exam_id,exam_name,sub_name,type,exam_date,exam_time,subject.semester AS sub_sem FROM exam INNER JOIN SUBJECT ON exam.sub_id=subject.sub_id INNER JOIN sub_alloc ON sub_alloc.sub_id=subject.sub_id INNER JOIN teacher ON teacher.teach_id=sub_alloc.teach_id INNER JOIN student ON student.course_id=subject.course_id WHERE student.lid='"+str(session['login_id'])+"'"
    res= a.select(qry)
    return render_template('student/attend_exam.html',exam=res)

@app.route('/st_exam/<e_id>')
def st_exam(e_id):

    session["score"]="0"
    a = Db()
    qry = "SELECT * FROM questions WHERE examid='"+e_id+"' order by qid ASC"
    res =a.select(qry)

    session['ab']= len(res)


    qry1 = "SELECT stud_id FROM student WHERE student.lid='"+str(session['login_id'])+"'"
    res1 = a.selectOne(qry1)
    if len(res)>0:
        m=res[0]




        return render_template('student/exam.html',m=m,stud=res1)

@app.route('/st_exam_post',methods=['post'])
def st_exam_post():
    exam_id = request.form['examid']
    stud_id = request.form['stud_id']
    question_id=request.form['question_id']
    answer = request.form['radio']
    a = Db()
    qry1 = "SELECT answer FROM questions WHERE qid='"+question_id+"' "

    resanswer = a.selectOne(qry1)
    print(resanswer['answer'])
    print(answer)

    session['ab']= int(session['ab'])-1


    if resanswer['answer']==answer:

        scr=int(session["score"])
        scr=scr+1
        session["score"]=str(scr)







    a= Db()
    qry="SELECT * FROM questions WHERE examid='"+exam_id+"' and  qid>"+question_id
    res = a.select(qry)
    qry1 = "SELECT stud_id FROM student WHERE student.lid='" + str(session['login_id']) + "'"
    res1 = a.selectOne(qry1)
    if len(res)>0:

        m=res[0]
        return render_template('student/exam.html', m=m,stud=res1)

    else:
        qry = " INSERT INTO results(`exam_id`,`stud_id`,`result`) VALUES('" + exam_id + "','" + stud_id + "','" + session["score"] + "')"
        res = a.insert(qry)

        return '''<script>window.location='/st_attend_exam'</script>'''




@app.route('/st_view_exam_status')
def st_view_exam_status():
    return render_template('student/view_exam_status.html')



@app.route('/st_view_exam_result')
def st_view_exam_result():
    a= Db()
    qry = "SELECT exam_name,sub_name,type,result,subject.semester AS sub_sem FROM results INNER JOIN exam ON results.exam_id=exam.exam_id INNER JOIN SUBJECT ON subject.sub_id=exam.sub_id INNER JOIN student ON results.stud_id=student.stud_id WHERE student.lid='"+str(session['login_id'])+"'"
    print(qry)
    res= a.select(qry)
    return render_template('student/view_exam_results.html',result=res)





@app.route('/st_review')
def st_review():
    return render_template('student/review.html')

@app.route('/st_review_post', methods=['post'])
def st_review_post():
    review = request.form["textarea"]
    qry="INSERT INTO review (`lid`,`review`,`date`,`time`) VALUES ('"+str(session['login_id'])+"','"+review+"',curdate(),curtime())"
    db = Db()
    res = db.insert(qry)
    return render_template('student/review.html')






@app.route('/st_change_password')
def st_change_password():
    return render_template('student/change_password.html')

@app.route('/student_change_pass_post',methods=['post'])
def student_change_pass_post():

    old_password = request.form['old']
    new_password = request.form['new']
    confirm_password = request.form['retype_new']

    a = Db()
    qry = "SELECT * FROM login WHERE lid='"+str(session['login_id'])+"' AND passwd='"+old_password+"'"
    print(qry)
    res= a.selectOne(qry)
    if res is not None:

        if(new_password==confirm_password):

            qry1="UPDATE login SET passwd ='"+new_password+"' WHERE lid='"+str(session['login_id'])+"'"
            res1=a.update(qry1)

            return '''<script>alert('Password changed Successfully');window.location='/login'</script>'''
        else:
            return render_template('student/change_password.html')
    else:
        return render_template('student/change_password.html')



@app.route('/sample/<eid>')
def sample(eid):
    session["examid"]=eid

    return render_template("student/sample.html",eid=eid)


@app.route('/image',methods=['post'])
def analysis():


    a= Db()
    qry = "SELECT image FROM student WHERE lid='"+str(session['login_id'])+"'"
    res = a.selectOne(qry)

    myimage= "C:/Users/ALBIN ROY/PycharmProjects/ExamPortal"+ res['image']






    import base64
    a=request.data
    # # print(a)
    # for m in request.form:
    #     print("image 6")

    s = base64.b64decode(a)
    print(s)
    #
    #
    print(len(s))
    with open("C:\\Users\\ALBIN ROY\\PycharmProjects\\ExamPortal\\static\\imageToSave.png",
            "wb") as fh:
        fh.write(s)
    # print("ok")



    import face_recognition
    known_image = face_recognition.load_image_file(myimage)
    unknown_image = face_recognition.load_image_file("C:\\Users\\ALBIN ROY\\PycharmProjects\\ExamPortal\\static\\imageToSave.png")

    biden_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
    print(results)




    if results[0]==True:
        return  jsonify(status="ok")


    else:
        print("no")
        return jsonify(status="No")
        # return "<Script>alert('Failed to recognize person');window.location='/login'</script>"






    return jsonify(status="ok")
if __name__ == '__main__':
    app.run(debug=True)
