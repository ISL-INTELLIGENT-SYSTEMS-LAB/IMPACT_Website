from flask import Flask, render_template, request, redirect, session, url_for
from markupsafe import Markup
import sqlite3
import datetime
import hashlib
import re

# Gets the current year for the footer and sets it as a global variable. This is passed to the templates.
current_date = datetime.date.today()
current_year = current_date.year

app = Flask(__name__)
app.secret_key = 'super secret key'

# Path to the database file (The database used is SQLite and is stored in the same directory as the flask app).
db_path = 'Impact.db'

# Get the user's device type and assign it to a global variable.
@app.before_request
def get_device_type():
    global user_device_type
    user_agent = request.user_agent.string.lower()
    if "android" in user_agent or "iphone" in user_agent or "ipad" in user_agent:
        user_device_type = "mobile"
    elif "windows" in user_agent or "macos" in user_agent:
        user_device_type = "desktop"
    else:
        user_device_type = "unknown"

# filter acceptable image file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@app.route('/')
def index():
    """
    Renders the index.html template with the current year.
    """
    return render_template('index.html', current_year=current_year)


@app.route('/faculty')
def faculty():
    """
    Renders the faculty.html template with the faculty data populated from the database and the current year.
    """
    faculty = facultyPopulate()
    if user_device_type == "mobile":
        return render_template('faculty.html', faculty=faculty, current_year=current_year, TitleFontSize="65px")
    else:
        return render_template('faculty.html', faculty=faculty, current_year=current_year, TitleFontSize="105px")


@app.route('/jplResearchers')
def jplResearchers():
    """
    Renders the jpl_researchers.html template with the JPL researchers data populated from the database and the current year.
    """
    jpl = jplPopulate()
    if user_device_type == "mobile":
        return render_template('jpl_researchers.html', jpl=jpl, current_year=current_year, TitleFontSize="45px")
    else:
        return render_template('jpl_researchers.html', jpl=jpl, current_year=current_year, TitleFontSize="105px")


@app.route('/students')
def students():
    """
    Renders the students.html template with the student data populated from the database based on the school and the current year.
    """
    FSU = populateStudents("FSU")
    NCCU = populateStudents("NCCU")
    WSSU = populateStudents("WSSU")
    if user_device_type == "mobile":
        return render_template('students.html', current_year=current_year, TitleFontSize="65px", FSU=FSU, NCCU=NCCU, WSSU=WSSU)
    else:
        return render_template('students.html', current_year=current_year, TitleFontSize="105px", FSU=FSU, NCCU=NCCU, WSSU=WSSU) 


@app.route('/admin')
def admin():
    """
    Renders the admin.html template if the admin is logged in.
    """
    if 'admin' in session:
        facultyRows = facultyPopulateTable()
        jplRows = jplPopulateTable()
        studentsRows = populateStudentsTable()

        sessionID = session['adminID']

        return render_template('admin.html', current_year=current_year, facultyRows=facultyRows, jplRows=jplRows, studentsRows=studentsRows, sessionID=sessionID)
    else:
        return redirect(url_for('adminLogin'))


@app.route('/adminLogin', methods=['POST', 'GET'])
def adminLogin():
    """
    Logs the admin into the admin page if the username and password are correct.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        bool,modal = adminLogin(username, password)
        if bool:
            return redirect(url_for('admin'))
        else:
            return render_template('adminLogin.html', current_year=current_year, modal=modal)
    else:
        return render_template('adminLogin.html', current_year=current_year)
    

@app.route('/adminLogout')
def adminLogout():
    """
    Logs the admin out of the admin page.
    """
    session.pop('admin', None)
    return redirect(url_for('adminLogin'))


@app.route('/addProfile', methods=['GET', 'POST'])
def addProfile():
    """
    Renders the add_profile.html template and handles the form submission for adding faculty, JPL researchers, and students.
    """
    if request.method == 'POST':
        if request.form['profileType'] == "faculty":
            name = request.form['name']
            title = request.form['title']
            school = request.form['school']
            email = request.form['email']
            bio = request.form['bio']
            photo = request.files['photo']
            link = request.form['link']
            if photo and allowed_file(photo.filename):
                insertFaculty(name, title, school, email, bio, photo.filename, link)
                saveFacultyPhoto(photo, name)
                return redirect(url_for('faculty'))
        elif request.form['profileType'] == "jpl":
            name = request.form['name']
            title = request.form['title']
            location = request.form['location']
            email = request.form['email']
            bio = request.form['bio']
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                insertJPL(name, title, location, email, bio, photo.filename)
                saveJPLPhoto(photo, name)
                return redirect(url_for('jplResearchers'))
        elif request.form['profileType'] == "student":
            name = request.form['name']
            tier = request.form['tier']
            photo = request.files['photo']
            school = request.form['school']
            if photo and allowed_file(photo.filename):
                insertStudent(name, tier, photo.filename, school)
                saveStudentPhoto(photo, name)
                return redirect(url_for('students'))
    return redirect(url_for('admin'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Methods~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def resizeImage(photo):
    """
    Makes the image square and resizes it to the specified width and height.
    """
    photo = photo.resize((500, 500))
    return photo


def saveFacultyPhoto(photo, name):
    """
    Saves the faculty photo to the static/images/Faculty directory.
    """
    photo = resizeImage(photo)
    photo.save(f'static/images/Faculty/{name}.jpg')


def saveJPLPhoto(photo, name):
    """
    Saves the JPL photo to the static/images/JPL directory.
    """
    photo = resizeImage(photo)
    photo.save(f'static/images/JPL/{name}.jpg')


def saveStudentPhoto(photo, name):
    """
    Saves the student photo to the static/images/Students directory.
    """
    photo = resizeImage(photo)
    photo.save(f'static/images/Students/{name}.jpg')


def adminLogin(username, password):
    """
    Logs the admin into the admin page if the username and password are correct.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username=?", (username,))
    data = cursor.fetchone()
    conn.close()

    # Compare the hashed password with the password in the database
    if data:
        if data[2] == hashlib.sha3_512(password.encode()).hexdigest():
            session['admin'] = True
            session['adminID'] = data[1]
            return (True, "")
        else:
            modal = populateErrorModal("The password or email you have entered is incorrect")
            return (False, modal)
    else:
        modal = populateErrorModal("The password or email you have entered is incorrect")
        return (False, modal)


def populateErrorModal(message):
    modal = Markup("""
                    <div class="modal fade" role="dialog" id="errorModal">
                            <div class="modal-dialog modal-dialog-centered" role="document">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h4 class="modal-title">Oh No!</h4>
                                            <form>
                                                <button class="btn-close" type="button" aria-label="Close" data-bs-dismiss="modal" onclick="history.back()"></button>
                                            </form>
                                    </div>
                                    <div class="modal-body">
                                        <p>"""+ message +"""</p>
                                    </div>
                                    <div class="modal-footer">
                                    <form>
                                        <button class="btn btn-light" type="button" data-bs-dismiss="modal" onclick="history.back()">Close</button>
                                    </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """)
    return modal


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Methods for populating data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def facultyPopulate():
    """
    Retrieves faculty data from the database and assembles the HTML markup for each faculty member.
    Returns the assembled HTML markup as a string.
    """
    faculty = []
    factultyassembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    for row in cursor.fetchall():
        faculty.append(row)
    conn.close()

    if user_device_type == "mobile":
        width = "250px"
        height = "250px"
    else:
        width = "400px"
        height = "400px"

    for i in range(len(faculty)):
        factultyassembled += Markup("""
            <div class="row">
                <div class="col-md-6 col-xxl-12" style="text-align: center;background: var(--bs-body-bg);width: 100%;margin: auto;padding-bottom: 76px;">
                    <img class="rounded-circle teamprofilepictures" style="overflow: hidden;width: initial;" width="Width" height="Height" src="static/images/Faculty/Photo">
                    <a href="Link" target="_blank"><h1 class="teamprofilenames">Name</h1></a>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">Title</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">School</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);font-size: 16px;">Email</h1>
                    <p class="teamprofiledescription"><span style="color: rgb(0, 0, 0);">Bio</span></p>
                </div>
            </div>
        """.replace("Name", faculty[i][1]).replace("Title", faculty[i][2]).replace("School", faculty[i][3]).replace("Email", faculty[i][4]).replace("Bio", faculty[i][5])).replace("Photo", faculty[i][6]).replace("Link", faculty[i][7]).replace("Width", width).replace("Height", height)

    return factultyassembled

def facultyPopulateTable():
    """
    Retrieves faculty data from the database and assembles the HTML markup for each faculty member.
    Returns the assembled HTML markup as a string.
    """
    faculty = []
    factultyassembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty")
    for row in cursor.fetchall():
        faculty.append(row)
    conn.close()

    count = 0

    for i in range(len(faculty)):
        if count % 2 == 0:
            factultyassembled += Markup("""<tr style="background: #262a38;">""")
        else:
            factultyassembled += Markup("""<tr style="background: #212430;">""")

        factultyassembled += Markup("""
                <td style="color: var(--bs-table-color);">Name<br></td>
                <td style="color: var(--bs-table-color);">Title</td>
                <td style="color: var(--bs-table-color);">School</td>
                <td style="color: var(--bs-table-color);">Email</td>
                <td style="color: var(--bs-table-color);font-size: 10px;">Bio</td>
                <td style="color: var(--bs-table-color);">Image</td>
                <td style="color: var(--bs-table-color);font-size: 10px;">Link</td>
                <td class="text-center align-middle" style="max-height: 60px;height: 60px;width: 100px;">
                    <a class="btn btnMaterial btn-flat success semicircle" role="button" href="#" style="color: rgb(0,197,179);"><i class="fas fa-pen"></i></a>
                    <a class="btn btnMaterial btn-flat accent btnNoBorders checkboxHover" role="button" style="margin-left: 5px;" data-bs-toggle="modal" data-bs-target="#delete-modal" href="#">
                        <i class="fas fa-trash btnNoBorders" style="color: #DC3545;"></i></a></td>
            </tr>
        """.replace("Name", faculty[i][1]).replace("Title", faculty[i][2]).replace("School", faculty[i][3]).replace("Email", faculty[i][4]).replace("Bio", faculty[i][5])).replace("Image", faculty[i][6]).replace("Link", faculty[i][7])
        count += 1

    return factultyassembled


def jplPopulate():
    """
    Retrieves JPL data from the database and assembles the HTML markup for each JPL researcher.
    Returns the assembled HTML markup as a string.
    """
    jpl = []
    jplassembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jpl")
    for row in cursor.fetchall():
        jpl.append(row)
    conn.close()

    if user_device_type == "mobile":
        width = "250px"
        height = "250px"
    else:
        width = "400px"
        height = "400px"

    for i in range(len(jpl)):
        jplassembled += Markup("""
            <div class="row">
                <div class="col-md-6 col-xxl-12" style="text-align: center;background: var(--bs-body-bg);width: 100%;margin: auto;padding-bottom: 76px;">
                    <img class="rounded-circle teamprofilepictures" style="overflow: hidden;width: initial;" width="Width" height="Height" src="static/images/JPL/Photo">
                    <h1 class="teamprofilenames">Name</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">Title</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">Location</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);font-size: 16px;">Email</h1>
                    <p class="teamprofiledescription"><span style="color: rgb(0, 0, 0);">Bio</span></p>
                </div>
            </div>
        """.replace("Name", jpl[i][1]).replace("Title", jpl[i][2]).replace("Location", jpl[i][3]).replace("Email", jpl[i][4]).replace("Bio", jpl[i][5])).replace("Photo", jpl[i][6]).replace("Width", width).replace("Height", height)

    return jplassembled

def jplPopulateTable():
    """
    Retrieves JPL data from the database and assembles the HTML markup for each JPL researcher.
    Returns the assembled HTML markup as a string.
    """
    jpl = []
    jplassembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jpl")
    for row in cursor.fetchall():
        jpl.append(row)
    conn.close()

    count = 0

    for i in range(len(jpl)):
        if count % 2 == 0:
            jplassembled += Markup("""<tr style="background: #262a38;">""")
        else:
            jplassembled += Markup("""<tr style="background: #212430;">""")

        jplassembled += Markup("""
            <td style="color: var(--bs-table-color);">Name<br></td>
            <td style="color: var(--bs-table-color);">Title</td>
            <td style="color: var(--bs-table-color);">Location</td>
            <td style="color: var(--bs-table-color);">Email</td>
            <td style="color: var(--bs-table-color);font-size: 12px;">Bio</td>
            <td style="color: var(--bs-table-color);">Image</td>
            <td class="text-center align-middle" style="max-height: 60px;height: 60px;width: 100px;">
                <a class="btn btnMaterial btn-flat success semicircle" role="button" href="#" style="color: rgb(0,197,179);"><i class="fas fa-pen"></i></a>
                <a class="btn btnMaterial btn-flat accent btnNoBorders checkboxHover" role="button" style="margin-left: 5px;" data-bs-toggle="modal" data-bs-target="#delete-modal" href="#">
                    <i class="fas fa-trash btnNoBorders" style="color: #DC3545;"></i></a></td>
        </tr>
        """.replace("Name", jpl[i][1]).replace("Title", jpl[i][2]).replace("Location", jpl[i][3]).replace("Email", jpl[i][4]).replace("Bio", jpl[i][5])).replace("Image", jpl[i][6])
        count += 1
    
    return jplassembled


def populateStudents(school):
    """
    Retrieves student data from the database based on the school and assembles the HTML markup for each student.
    Returns the assembled HTML markup as a string.
    """
    students = []
    students_assembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE school=?", (school,))
    for row in cursor.fetchall():
        students.append(row)
    conn.close()

    if user_device_type == "mobile":
        for i in range(len(students)):
            students_assembled += Markup("""
                        <div class="col">
                            <div class="card border-0 shadow-none">
                                <div class="card-body text-center d-flex flex-column align-items-center p-0">
                                    <img class="rounded-circle mb-3 fit-cover" width="130" height="130" src="static/images/Students/Photo" alt="https://cdn.bootstrapstudio.io/placeholders/1400x800.png">
                                    <h5 class="fw-bold text-primary card-title mb-0"><strong>Name</strong></h5>
                                    <p class="text-muted card-text mb-2" style="font-size:8px;">Email<br>Tier</p>
                                </div>
                            </div>
                        </div>
            """.replace("Name", students[i][1]).replace("Tier", students[i][2])).replace("Photo", students[i][3]).replace("Email", students[i][5])
    else:
        for i in range(len(students)):
            students_assembled += Markup("""
                        <div class="col">
                            <div class="card border-0 shadow-none">
                                <div class="card-body text-center d-flex flex-column align-items-center p-0">
                                    <img class="rounded-circle mb-3 fit-cover" width="130" height="130" src="static/images/Students/Photo" alt="https://cdn.bootstrapstudio.io/placeholders/1400x800.png">
                                    <h5 class="fw-bold text-primary card-title mb-0"><strong>Name</strong></h5>
                                    <p class="text-muted card-text mb-2">Email<br>Tier</p>
                                </div>
                            </div>
                        </div>
            """.replace("Name", students[i][1]).replace("Tier", students[i][2])).replace("Photo", students[i][3]).replace("Email", students[i][5])
    
    return students_assembled

def populateStudentsTable():
    """
    Retrieves student data from the database based on the school and assembles the HTML markup for each student.
    Returns the assembled HTML markup as a string.
    """
    students = []
    students_assembled = ""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        students.append(row)
    conn.close()

    count = 0

    for i in range(len(students)):
        if count % 2 == 0:
            students_assembled += Markup("""<tr style="background: #262a38;">""")
        else:
            students_assembled += Markup("""<tr style="background: #212430;">""")

        students_assembled += Markup("""
            <td style="color: var(--bs-table-color);">Name<br></td>
            <td style="color: var(--bs-table-color);">Tier</td>
            <td style="color: var(--bs-table-color);">Image</td>
            <td style="color: var(--bs-table-color);">School</td>
            <td style="color: var(--bs-table-color);">Email</td>
            <td class="text-center align-middle" style="max-height: 60px;height: 60px;width: 100px;">
                <a class="btn btnMaterial btn-flat success semicircle" role="button" href="#" style="color: rgb(0,197,179);"><i class="fas fa-pen"></i></a>
                <a class="btn btnMaterial btn-flat accent btnNoBorders checkboxHover" role="button" style="margin-left: 5px;" data-bs-toggle="modal" data-bs-target="#delete-modal" href="#">
                    <i class="fas fa-trash btnNoBorders" style="color: #DC3545;"></i></a></td>
        </tr>
        """.replace("Name", students[i][1]).replace("Tier", students[i][2])).replace("Image", students[i][3]).replace("School", students[i][4]).replace("Email", students[i][5])
        count += 1

    return students_assembled


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Methods for inserting/updating data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def insertFaculty(name, title, school, email, bio, photo, link):
    """
    Inserts faculty data into the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faculty (FID, name, title, school, email, bio, image, link) VALUES (NULL,?, ?, ?, ?, ?, ?, ?)", (name, title, school, email, bio, photo, link))
    conn.commit()
    conn.close()


def updateFaculty(name, title, school, email, bio, photo, link, id):
    """
    Updates faculty data in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE faculty SET name=?, title=?, school=?, email=?, bio=?, image=?, link=? WHERE id=?", (name, title, school, email, bio, photo, link, id))
    conn.commit()
    conn.close()


def insertJPL(name, title, location, email, bio, photo):
    """
    Inserts JPL data into the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jpl (RID, name, title, school, email, bio, image) VALUES (NULL,?, ?, ?, ?, ?, ?)", (name, title, location, email, bio, photo))
    conn.commit()
    conn.close()


def updateJPL(name, title, location, email, bio, photo, id):
    """
    Updates JPL data in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE jpl SET name=?, title=?, school=?, email=?, bio=?, image=? WHERE id=?", (name, title, location, email, bio, photo, id))
    conn.commit()
    conn.close()


def insertStudent(name, tier, photo, school):
    """
    Inserts student data into the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (SID, name, tier, image, school) VALUES (NULL,?, ?, ?, ?)", (name, tier, photo, school))
    conn.commit()
    conn.close()


def updateStudent(name, tier, photo, school, id):
    """
    Updates student data in the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, tier=?, image=?, school=? WHERE id=?", (name, tier, photo, school, id))
    conn.commit()
    conn.close()


def createAdmin(username, password):
    """
    Creates an admin account in the database.
    """
    password = hashlib.sha3_512(password.encode()).hexdigest()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admin (AID, username, password) VALUES (NULL,?, ?)", (username, password))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # This is used to create the admin account. It should be commented out after the admin account is created.
    #createAdmin("admin", "password")
    app.debug = True
    app.run()
