from importlib.resources import Package

import bcrypt
import mongoengine
import state
from flask import Flask, render_template, redirect, request, url_for, session, app
import psycopg2
import os
import datetime
import collections
import sys
import mongoengine

app = Flask(__name__)
# app.secret_key = os.urandom(24)
app.secret_key = 'apple2'

# Connecting to database
conn = psycopg2.connect(host="127.0.0.1", user="postgres",
                        password="flash", database="faculty_portal_testing")
cursor = conn.cursor()


def global_init(db_name: str):
    mongoengine.register_connection(alias='core', name=db_name)


if __name__ == '__main__':
    global_init('db')


@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'facultyId' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        if 'Update' in request.form:
            pub = request.form['infoProf']
            state.updateInfo(session['email'], str(pub))
            return redirect(url_for('home'))

    val = state.getInfo(state.active_account.email)

    return render_template('update_info.html', logged_in=1, role=session['role'], val=val)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'facultyId' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        if 'Publications' in request.form:
            pub = request.form['infoProf']
            state.addPublication(session['email'], str(pub))
            return redirect(url_for('home'))
        if 'Grants' in request.form:
            pub = request.form['infoProf']
            state.addGrants(session['email'], str(pub))
            return redirect(url_for('home'))
        if 'Awards' in request.form:
            pub = request.form['infoProf']
            state.addAwards(session['email'], str(pub))
            return redirect(url_for('home'))
        if 'Teaching' in request.form:
            pub = request.form['infoProf']
            state.addTeaching(session['email'], str(pub))
            return redirect(url_for('home'))
        if 'PublicationsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub) - 1
                pubValue = state.find_account_by_email(session['email']).publication[pubI]
                state.deletePublication(session['email'], pubValue)
            except:
                return render_template('edit.html', error='Invalid index', logged_in=1, role=session['role'])
            return redirect(url_for('home'))
        if 'GrantsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub) - 1
                pubValue = state.find_account_by_email(session['email']).grants[pubI]
                state.deleteGrants(session['email'], pubValue)
            except:
                return render_template('edit.html', error='Invalid index', logged_in=1, role=session['role'])
            return redirect(url_for('home'))
        if 'AwardsD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub) - 1
                pubValue = state.find_account_by_email(session['email']).awards[pubI]
                state.deleteAwards(session['email'], pubValue)
            except:
                return render_template('edit.html', error='Invalid index', logged_in=1, role=session['role'])
            return redirect(url_for('home'))
        if 'TeachingD' in request.form:
            pub = request.form['delete']
            try:
                pubI = int(pub) - 1
                pubValue = state.find_account_by_email(session['email']).teaching[pubI]
                state.deleteTeaching(session['email'], pubValue)
            except:
                return render_template('edit.html', error='Invalid index', logged_in=1, role=session['role'])
            return redirect(url_for('home'))
    return render_template('edit.html', logged_in=1, role=session['role'])


@app.route('/<name>', methods=['GET', 'POST'])
def profInfo(name):
    if 'facultyId' not in session:
        name = name
        cursor.execute("SELECT * from faculty r where r.name=%s", [name])
        row = cursor.fetchone()

        if cursor.rowcount == 0:
            return render_template('info.html', logged=2)

        else:

            data = {'facultyId': row[0], 'name': row[1], 'email': row[2], 'mobileNumber': row[3],
                    'departmentName': row[4]}
            val = state.getInfo(data['email'])
            return render_template('prof_info.html', name=data['name'],
                                   department=data['departmentName'], email=data['email'],
                                   mobile=data['mobileNumber'], val=val)

    if 'facultyId' in session:
        name = name
        if name != session['name']:
            cursor.execute("SELECT * from faculty r where r.name=%s", [name])
            row = cursor.fetchone()

            if cursor.rowcount == 0:
                return render_template('info.html', logged=2, logged_in=1, role=session['role'])
            else:
                data = {'facultyId': row[0], 'name': row[1], 'email': row[2], 'mobileNumber': row[3],
                        'departmentName': row[4]}
                val = state.getInfo(data['email'])
                return render_template('prof_info.html', name=data['name'],
                                       department=data['departmentName'], email=data['email'],
                                       mobile=data['mobileNumber'], role=session['role'], val=val, logged_in=1)
        else:
            cursor.execute("SELECT * from remaining_leave r where r.faculty_id=%s", [session['facultyId']])
            row = cursor.fetchone()

            if cursor.rowcount > 0:
                session['leave'] = row[1]
            else:
                session['leave'] = 0
            print(session['email'])

            val = state.getInfo(state.active_account.email)

            return render_template('home.html', role=session['role'],
                                   name=session['name'], faculty_position=session['role'],
                                   department=session['departmentName'], email=session['email'],
                                   mobile=session['mobileNumber'], remainingleave=session['leave'], val=val,
                                   logged_in=1)


@app.route('/info', methods=['GET', 'POST'])
def inform():
    if request.method == 'POST':
        name = request.form['name']
    return render_template('info.html')


def logged_in():
    if session.get('logged_in') is None:
        return False
    return session['logged_in']


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'facultyId' in session:
        return redirect(url_for('home'))

    error = None
    session.clear()
    if request.method == 'POST':
        # session.clear()
        usrname = request.form['username']
        password = request.form['password']

        print(type(usrname))

        cursor.execute("SELECT * from login_data l where  l.username=%s and l.password=%s", (usrname, password))
        row = cursor.fetchone()

        if cursor.rowcount == 0:
            error = 'Invalid Credentials. Please try again.'
        else:
            facultyid = row[3]
            # getting details og logged in faculty
            cursor.execute("SELECT * from faculty f where  f.faculty_id=%s", [facultyid])
            row = cursor.fetchone()
            # error = row

            session['facultyId'] = facultyid
            session['logged_in'] = True
            session['name'] = row[1]
            session['email'] = row[2]
            session['mobileNumber'] = row[3]
            session['departmentName'] = row[4]

            # Now check for the update of remaining_leave table
            # and update it (if required)
            try:
                cursor.execute("CALL check_for_year_change();")
                conn.commit()
            except Exception as e:
                conn.rollback()

            hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

            ss = session['email']
            name = session['name']
            state.active_account = state.create_account(str(name), ss, hashed.decode('utf-8'))

            cursor.execute("SELECT * from director d where  d.faculty_id=%s", [facultyid])
            if cursor.rowcount > 0:
                # Pass function name
                session['role'] = 'director'
                return redirect(url_for('home'));

            cursor.execute("SELECT * from cross_cutting_faculty c where  c.faculty_id=%s", [facultyid])
            if cursor.rowcount > 0:
                # Pass function name
                session['role'] = 'dean'
                return redirect(url_for('home'));

            cursor.execute("SELECT * from hod h where  h.faculty_id=%s", [facultyid])
            if cursor.rowcount > 0:
                # Pass function name
                session['role'] = 'hod'
                return redirect(url_for('home'));

            session['role'] = 'faculty'

            return redirect(url_for('home'))

    return render_template('index.html', error=error)


@app.route('/logout')
def log_out():
    session.clear()

    error = "you've been logged out"
    return redirect(url_for('login_page'))


@app.route('/')
@app.route('/home')
def home():
    if 'facultyId' in session:
        try:
            cursor.execute("CALL auto_reject_bydate();")
            conn.commit()
        except Exception as e:
            conn.rollback()
            return render_template("test_page.html", error=e)

        # now get the remaining leave for current faculty
        cursor.execute("SELECT * from remaining_leave r where r.faculty_id=%s", [session['facultyId']])
        row = cursor.fetchone()

        if cursor.rowcount > 0:
            session['leave'] = row[1]
        else:
            session['leave'] = 0
        print(session['email'])

        val = state.getInfo(state.active_account.email)

        return render_template('home.html', role=session['role'],
                               name=session['name'], faculty_position=session['role'],
                               department=session['departmentName'], email=session['email'],
                               mobile=session['mobileNumber'], remainingleave=session['leave'], val=val, logged_in=1)
    else:
        return redirect(url_for('login_page'))


@app.route('/hire', methods=['GET', 'POST'])
def hire():
    hire_mssg = None
    if 'facultyId' in session:

        valid_authority = ['director']
        if session['role'] not in valid_authority:
            return redirect(url_for('home'))

        hire_for = request.args.get('hire_for')
        cursor.execute("SELECT dept_name from department")
        department_list = cursor.fetchall()
        department_list = [i[0] for i in department_list]

        if request.method == 'POST':

            if hire_for == 'Faculty':
                # insert into faculty and login_data table
                # check for duplicate key
                """
                cursor.execute("SELECT * FROM faculty f where f.faculty_id = %s", [request.form['facultyid']])
                if cursor.rowcount>0:
                    hire_mssg = "Choose different Faculty ID"
                    exit()
                """
                # insert into faculty table
                success = True
                try:
                    cursor.execute("INSERT INTO faculty(faculty_id, name, email, mobile_no, dept_name) \
                        VALUES (%s, %s, %s, %s, %s)", (request.form['facultyid'], request.form['name'],
                                                       request.form['email'], request.form['mobile'],
                                                       request.form['department']))
                    conn.commit()

                except Exception as err:
                    hire_mssg = "Choose different Faculty ID"
                    conn.rollback()
                    success = False

                if success == True:
                    # Now insert into login_data table
                    # let's create username
                    first_name = request.form['name']
                    first_name = first_name.split(" ")
                    first_name = first_name[0].lower()
                    username = first_name + str(request.form['facultyid'])

                    cursor.execute("INSERT INTO login_data(username, password, faculty_id) VALUES\
                        (%s, %s, %s)", (username, request.form['password'], request.form['facultyid']))
                    conn.commit()

                    hire_mssg = "Faculty has been successfully added. " + username
                    hire_mssg = hire_mssg + " is username for faculty " + request.form['name']


            else:
                # check if faculty exists in faculty table
                cursor.execute("SELECT * FROM faculty f where f.faculty_id = %s", [request.form['facultyid']])
                if cursor.rowcount > 0:
                    # hire for HoD

                    if hire_for == 'HoD':
                        # check if HoD already exists for selected department
                        # it it existed then we will call update else call insert
                        cursor.execute("SELECT dept_name FROM hod h where h.dept_name = %s",
                                       [request.form['department']])
                        hire_mssg = "successfully appointed new " + hire_for + " for " + request.form['department']
                        hire_mssg = hire_mssg + " department."

                        if cursor.rowcount > 0:
                            # hod existed for this department
                            try:
                                cursor.execute("UPDATE hod set faculty_id = %s where hod.dept_name = %s",
                                               (request.form['facultyid'], request.form['department']))
                                conn.commit()
                            except Exception as err:
                                conn.rollback()
                                hire_mssg = str(err)
                                hire_mssg = hire_mssg.split("CONTEXT")[0]
                        else:
                            # hod didi not existed for that department
                            try:
                                cursor.execute("INSERT INTO hod (faculty_id, dept_name, start_date,\
                                    end_date) Values (%s, %s, %s, %s)", (request.form['facultyid'],
                                                                         request.form['department'],
                                                                         request.form['startdate'],
                                                                         request.form['enddate']));
                                conn.commit()
                            except Exception as e:
                                conn.rollback()
                                hire_mssg = str(e)
                                hire_mssg = hire_mssg.split("CONTEXT")[0]
                    # hire for Dean
                    else:
                        # check if HoD already exists for selected department
                        # it it existed then we will call update else call insert
                        cursor.execute("SELECT * FROM cross_cutting_faculty c where c.cross_role = %s",
                                       [request.form['cross_role']])
                        hire_mssg = "successfully appointed new " + request.form['cross_role']

                        if cursor.rowcount > 0:
                            # do update operation
                            try:
                                cursor.execute("UPDATE cross_cutting_faculty  set \
                                    faculty_id=%s where \
                                    cross_cutting_faculty.cross_role=%s", (request.form['facultyid'],
                                                                           request.form['cross_role']))
                                conn.commit()
                            except Exception as e:
                                conn.rollback()
                                hire_mssg = str(e)
                                # hire_mssg = hire_mssg.split("CONTEXT")[0]

                        else:
                            # do insert operation
                            try:
                                cursor.execute("INSERT INTO cross_cutting_faculty (faculty_id, cross_role,\
                                    start_date, end_date) values (%s, %s, %s, %s)", (request.form['facultyid'],
                                                                                     request.form['cross_role'],
                                                                                     request.form['startdate'],
                                                                                     request.form['enddate']))
                                conn.commit()
                            except Exception as e:
                                conn.rollback()
                                hire_mssg = str(e)
                                # hire_mssg = hire_mssg.split("CONTEXT")[0]


                else:
                    hire_mssg = "Faculty does not exists."

        today = datetime.date.today()
        enddate = today + datetime.timedelta(days=730)

        cursor.execute("SELECT cross_role from cross_faculty_role")
        cross_role_list = cursor.fetchall()
        cross_role_list = [i[0] for i in cross_role_list]
        # redirect to hire page
        return render_template('hire.html', role=session['role'],
                               hire_mssg=hire_mssg, hire_tag="Hire " + hire_for,
                               hire=hire_for, department=department_list, startdate=today,
                               enddate=enddate, cross_role=cross_role_list, logged_in=1)

    else:
        return redirect(url_for('login_page'))


@app.route('/applyforleave', methods=['GET', 'POST'])
def applyForLeave():
    leave_mssg = None
    if 'facultyId' in session:
        try:
            cursor.execute("CALL auto_reject_bydate();")
            conn.commit()
        except Exception as e:
            conn.rollback()
            return render_template("test_page.html", error=e)

        not_access_to_leave = ['director']
        if session['role'] in not_access_to_leave:
            return redirect(url_for('home'))

        if request.method == 'POST':
            # get remaining leave for this faculty
            cursor.execute("SELECT * from remaining_leave r where r.faculty_id = %s;",
                           [session['facultyId']]);
            remainingLeave = cursor.fetchone()[1]

            endDate = datetime.datetime.strptime(request.form['enddate'], '%Y-%m-%d').date()
            startDate = datetime.datetime.strptime(request.form['startdate'], '%Y-%m-%d').date()

            if endDate < startDate:
                return render_template('apply_leave.html', role=session['role'],
                                       leave_mssg="end date cannot be lower than start date", show_form=1, logged_in=1)

            requestedLeave = endDate - startDate
            requestedLeave = requestedLeave.days + 1

            allowedLeave = min(requestedLeave, remainingLeave);

            endDate = startDate + datetime.timedelta(days=allowedLeave - 1)

            today = datetime.date.today()
            type = 'n'
            if startDate < today:
                type = 'r'

            # return render_template('apply_leave.html', role=session['role'],
            # leave_mssg="" + str(requestedLeave) + "---" + str(endDate) + " -- " + type,  show_form= 1)

            try:
                cursor.execute("INSERT INTO leave_application(faculty_id, subject, description, start_date\
                    , end_date, type) VALUES (%s, %s, %s, %s, %s, %s)", (session['facultyId'],
                                                                         request.form['subject'],
                                                                         request.form['description'], startDate,
                                                                         endDate, type));
                conn.commit();
            except Exception as e:
                conn.rollback();
                return render_template('apply_leave.html', role=session['role'],
                                       leave_mssg=e, show_form=1, logged_in=1)

            try:
                cursor.execute("CALL auto_reject_bydate();")
                conn.commit()
            except Exception as e:
                conn.rollback()
                return render_template("test_page.html", error=e)

            return render_template('apply_leave.html', role=session['role'],
                                   leave_mssg="successfully applied for leave", show_form=0, logged_in=1)

        # check if this faculty's leave application is already in process
        # or if he has currently ongoing vacation
        today = datetime.date.today()
        show_form = 1

        cursor.execute("select * from check_for_ongoing_leave_application(%s);",
                       [session['facultyId']]);
        show_form = cursor.fetchone()[0];

        if show_form == 1:
            show_form = 0
        else:
            show_form = 1

        if show_form == 0:
            leave_mssg = 'You have already applied for leave or You have ongoing vacation.'
            return render_template('apply_leave.html', role=session['role'],
                                   leave_mssg=leave_mssg, show_form=show_form, logged_in=1)
        else:
            return render_template('apply_leave.html', role=session['role'],
                                   leave_mssg=leave_mssg, show_form=show_form, logged_in=1)

    else:
        return redirect(url_for('login_page'))


# leave aplication history for a faculty
@app.route('/history')
def history():
    if 'facultyId' in session:
        not_access_to_leave_history = ['director']
        if session['role'] in not_access_to_leave_history:
            return redirect(url_for('home'))

        # if request.method == 'POST':
        # leaveApplicationDetail(request.args.get('post_id'));

        cursor.execute("SELECT * from leave_application l where l.faculty_id = %s \
            order by applied_on desc;", [session['facultyId']]);
        row_data = cursor.fetchall()
        leave_application = []

        for row in row_data:
            row_dict = {}
            row_dict['application_id'] = row[1]
            row_dict['subject'] = row[2]
            row_dict['description'] = row[3]
            # row_dict['start_date'] = row[4]
            # row_dict['end_date'] = row[5]
            row_dict['applied_on'] = row[6].date()
            row_dict['status'] = row[7]

            if row_dict['status'] == 'pending':
                cursor.execute("SELECT * from pending_leave_application p where p.faculty_id = %s \
                    and p.application_id = %s and p.status = 'pending' ", (session['facultyId'],
                                                                           row_dict['application_id']));
                temp = cursor.fetchone()
                row_dict['pending_at'] = temp[3]

            if row_dict['status'] == 'rejected':
                cursor.execute("SELECT * from leave_application_hist l where l.faculty_id = %s \
                    and l.application_id = %s and l.status = 'rejected' ", (session['facultyId'],
                                                                            row_dict['application_id']));
                temp = cursor.fetchone()
                row_dict['rejected_at'] = temp[3]

            leave_application.append(row_dict)

        return render_template('application_summary.html', posts=leave_application,
                               role=session['role'], logged_in=1);


    else:
        return redirect(url_for('login_page'))


def allow_comment(applicationid):
    # check if the logged in person is same as person who initiated this application
    cursor.execute("SELECT * from leave_application l where l.application_id = %s;",
                   [applicationid]);
    row = cursor.fetchone()

    if row[0] == session['facultyId']:
        if row[7] == 'pending':
            return 1;
        else:
            return 0;
    else:
        # Now check if application is pending approval at logged in faculty
        # If yes he will be able to add comment else not
        cursor.execute("SELECT * from pending_leave_application p where \
            p.application_id=%s and p.faculty_id = %s and \
            p.current_level_faculty_id = %s and p.status = 'pending';", (applicationid,
                                                                         row[0], session['facultyId']));
        if cursor.rowcount > 0:
            return 1;
        return 0;

    return 0


def find_faculty_name(facultyid):
    cursor.execute("SELECT * from faculty f where f.faculty_id = %s", [facultyid]);
    if cursor.rowcount > 0:
        # return render_template("test_page.html", error = cursor.fetchall()[1])
        return cursor.fetchone()[1]

    cursor.execute("SELECT * from old_faculty f where f.faculty_id = %s", [facultyid]);
    return cursor.fetchone()[1]


def can_approve(initiator, applicationid):
    cursor.execute("SELECT * from pending_leave_application p where p.faculty_id=%s and \
        p.application_id=%s and p.current_level_faculty_id=%s and p.status = 'pending';",
                   (initiator, applicationid, session['facultyId']));
    if cursor.rowcount > 0:
        return 1;
    return 0


@app.route('/leaveApplicationDetail', methods=['GET', 'POST'])
def leaveApplicationDetail():
    if 'facultyId' in session:
        """
        not_access_to_leave_history = ['director']
        if session['role'] in not_access_to_leave_history:
            return redirect(url_for('home'))
        """

        applicationid = request.args.get("post_id")

        # find faculty who initiated this application
        cursor.execute("SELECT * from leave_application l where l.application_id = %s",
                       [applicationid]);
        initiator_faculty = cursor.fetchone()[0]

        if request.method == 'POST':
            if session['facultyId'] == initiator_faculty:
                designation = 'self'
            else:
                designation = session['role']

            # insert comment into comment table
            try:
                cursor.execute("INSERT into comment(application_id, comment, faculty_id, \
                    designation) values (%s, %s, %s, %s)", (applicationid,
                                                            request.form['commenttext'], session['facultyId'],
                                                            designation));
                conn.commit()
            except Exception as e:
                conn.rollback();
                return render_template("test_page.html", error=e)
                print('Insert into comment table failed', file=sys.stderr)
            return redirect(url_for('leaveApplicationDetail', post_id=applicationid))

        # Get application detail
        cursor.execute("SELECT * from leave_application l where l.faculty_id=%s and \
            l.application_id=%s", (initiator_faculty, applicationid));
        row = cursor.fetchone()

        # application detail
        post = {}
        post['application_id'] = row[1]
        post['subject'] = row[2]
        post['description'] = row[3]
        post['start_date'] = row[4]
        post['end_date'] = row[5]
        post['applied_on'] = row[6].date()
        post['status'] = row[7]
        post['type'] = row[8]

        if session['facultyId'] != initiator_faculty:
            post['initiated_by'] = find_faculty_name(initiator_faculty)

            cursor.execute("SELECT c.cross_role from cross_cutting_faculty c where \
                c.faculty_id = %s", [initiator_faculty]);
            if cursor.rowcount > 0:
                post['initiator_designation'] = cursor.fetchone()[0][0]
            else:
                cursor.execute("SELECT h.dept_name from hod h where h.faculty_id=%s",
                               [initiator_faculty])
                if cursor.rowcount > 0:
                    post['initiator_designation'] = 'HoD of department ' + cursor.fetchone()[0]
                else:
                    post['initiator_designation'] = 'Faculty'

        # get all the comment made on this application
        cursor.execute("SELECT * from comment c where c.application_id = %s ;", [applicationid]);
        comments = cursor.fetchall();

        comment_dict = {}
        for comment in comments:
            temp_dict = {}
            temp_dict['type'] = 'comment'
            temp_dict['commented_by'] = find_faculty_name(comment[4])
            temp_dict['commented_on'] = comment[2].date()
            temp_dict['text'] = comment[3]
            temp_dict['designation'] = comment[5]

            comment_dict[comment[2]] = temp_dict

        p = 1
        # Now add approval/rejection text from pending_leave_application or leave_application_hist
        if post['status'] == 'pending':
            cursor.execute("SELECT * from pending_leave_application p where p.faculty_id = %s\
                and p.application_id = %s and p.status='approved';", (initiator_faculty,
                                                                      applicationid))
        else:
            cursor.execute("SELECT * from leave_application_hist l where l.faculty_id = %s\
                and l.application_id = %s;", (initiator_faculty, applicationid))
            p = 2

        rows = cursor.fetchall()

        for row in rows:
            temp_dict = {}
            temp_dict['type'] = 'info'
            temp_dict['status'] = row[5]
            # approved/reject by MR X (HoD) on YYYY-MM-DD
            # lets find faculty name
            cursor.execute("SELECT * from faculty f where f.faculty_id = %s; ",
                           [row[4]]);
            if cursor.rowcount > 0:
                temp_dict['name'] = cursor.fetchone()[1]
            else:
                cursor.execute("SELECT * from old_faculty f where f.faculty_id = %s; ",
                               [row[4]])
                temp_dict['name'] = cursor.fetchone()[1]
            temp_dict['designation'] = row[3]
            if p == 1:
                message_time = row[6]
            else:
                message_time = row[7]
            temp_dict['commented_on'] = message_time.date()

            comment_dict[message_time] = temp_dict

            # getting remark if any
            if p == 2 and row[6] != ' ':
                post['remark'] = row[6]

        comment_dict = collections.OrderedDict(sorted(comment_dict.items()))
        # return render_template("test_page.html", error = comment_dict)
        comments = comment_dict.values()
        comments = list(comments)
        # return render_template("test_page.html", error=comments)

        isComment = 0
        if len(comments) > 0:
            isComment = 1

        return render_template('history_detail.html', post=post, role=session['role'],
                               is_comment=isComment, comments=comments, allow_comment=allow_comment(applicationid)
                               , approve=can_approve(initiator_faculty, applicationid),
                               applicationid=applicationid, logged_in=1);


    else:
        return redirect(url_for('login_page'))


@app.route('/pendingapproval')
def pendingApproval():
    if 'facultyId' in session:
        not_access_to_pending_approval = ['faculty']
        if session['role'] in not_access_to_pending_approval:
            return redirect(url_for('home'))

        cursor.execute("SELECT l.faculty_id, l.application_id, l.subject, l.description, \
            l.applied_on, l.status from pending_leave_application p, leave_application l where \
            (l.faculty_id, l.application_id)=(p.faculty_id, p.application_id) and \
             p.current_level_faculty_id = %s and p.status='pending' order by p.date desc;",
                       [session['facultyId']]);
        row_data = cursor.fetchall()
        leave_application = []

        for row in row_data:
            row_dict = {}
            row_dict['application_id'] = row[1]
            row_dict['subject'] = row[2]
            row_dict['description'] = row[3]
            # row_dict['start_date'] = row[4]
            # row_dict['end_date'] = row[5]
            row_dict['applied_on'] = row[4].date()
            row_dict['status'] = row[5]
            row_dict['pending_at'] = 'your level'

            leave_application.append(row_dict)

        return render_template('application_summary.html', posts=leave_application,
                               role=session['role'], logged_in=1);

    else:
        return redirect(url_for('login_page'))


@app.route('/approvedapplication')
def approvedApplication():
    if 'facultyId' in session:
        not_access_to_pending_approval = ['faculty']
        if session['role'] in not_access_to_pending_approval:
            return redirect(url_for('home'))

        cursor.execute("SELECT * from \
            ((SELECT l.faculty_id, l.application_id, l.subject, l.description, \
            l.applied_on, p.status, p.date from pending_leave_application p, leave_application l where \
            (l.faculty_id, l.application_id)=(p.faculty_id, p.application_id) and \
             p.current_level_faculty_id = %s and (p.status='approved' or p.status='rejected'))\
             union \
             (SELECT l2.faculty_id, l2.application_id, l2.subject, l2.description, \
            l2.applied_on, l1.status, l1.date from leave_application_hist l1, leave_application l2 where \
            (l2.faculty_id, l2.application_id)=(l1.faculty_id, l1.application_id) and \
             l1.current_level_faculty_id = %s )) as tb \
             order by date desc", (session['facultyId'], session['facultyId']))

        """
        cursor.execute("SELECT l.faculty_id, l.application_id, l.subject, l.description, \
            l.applied_on, l.status from pending_leave_application p, leave_application l where \
            (l.faculty_id, l.application_id)=(p.faculty_id, p.application_id) and \
             p.current_level_faculty_id = %s and p.status<>'pending' order by p.date desc;",
             [session['facultyId']]);
        """
        row_data = cursor.fetchall()
        leave_application = []

        for row in row_data:
            row_dict = {}
            row_dict['application_id'] = row[1]
            row_dict['subject'] = row[2]
            row_dict['description'] = row[3]
            row_dict['applied_on'] = row[4].date()
            row_dict['status'] = row[5]

            leave_application.append(row_dict)

        return render_template('application_summary.html', posts=leave_application,
                               role=session['role'], logged_in=1);
    else:
        return redirect(url_for('login_page'))


@app.route('/approveleave')
def approveLeaveApplication():
    if 'facultyId' in session:
        not_access_to_pending_approval = ['faculty']
        if session['role'] in not_access_to_pending_approval:
            return redirect(url_for('home'))

        applicationid = request.args.get("application")
        cursor.execute("SELECT * from pending_leave_application p where p.application_id = %s\
            and p.current_level_faculty_id=%s and p.status='pending';", (applicationid,
                                                                         session['facultyId']));
        if cursor.rowcount > 0:
            try:
                cursor.execute("UPDATE pending_leave_application set status = 'approved'\
                    where current_level_faculty_id=%s and application_id=%s and status='pending';",
                               (session['facultyId'], applicationid))
                conn.commit()
            except Exception as e:
                conn.rollback()
                return render_template("test_page.html", error=e)

        return redirect(url_for('pendingApproval'));
    else:
        return redirect(url_for('login_page'))


@app.route('/rejectleave')
def rejectLeaveApplication():
    if 'facultyId' in session:
        not_access_to_pending_approval = ['faculty']
        if session['role'] in not_access_to_pending_approval:
            return redirect(url_for('home'))

        applicationid = request.args.get("application")
        cursor.execute("SELECT * from pending_leave_application p where p.application_id = %s\
            and p.current_level_faculty_id=%s and p.status='pending';", (applicationid,
                                                                         session['facultyId']));
        if cursor.rowcount > 0:
            try:
                cursor.execute("UPDATE pending_leave_application set status = 'rejected'\
                    where current_level_faculty_id=%s and application_id=%s and status='pending';",
                               (session['facultyId'], applicationid))
                conn.commit()
            except Exception as e:
                conn.rollback()
                return render_template("test_page.html", error=e)

        return redirect(url_for('pendingApproval'));
    else:
        return redirect(url_for('login_page'))


#############################################################################
# testing part

@app.route('/summary')
def summary_test():
    cursor.execute("SELECT * from faculty f where f.faculty_id = %s", [3]);
    # if cursor.rowcount() > 0:
    return render_template("test_page.html", error=cursor.rowcount)


@app.route('/faculty')
def faculty():
    return render_template('faculty.html')


@app.route('/hod')
def hod():
    return render_template(('hod_home.html'))


@app.route('/dean')
def dean():
    return render_template(('hod_home.html'))


@app.route('/director')
def director():
    return render_template(('base.html'))


if __name__ == '__main__':
    app.run(debug=True)
