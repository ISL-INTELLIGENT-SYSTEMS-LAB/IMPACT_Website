from flask import Flask, render_template, request, redirect
from markupsafe import Markup
import sqlite3
import datetime

# Gets the current year for the footer and sets it as a global variable. This is passed to the templates.
current_date = datetime.date.today()
current_year = current_date.year

app = Flask(__name__)

# Path to the database file (The database used is SQLite and is stored in the same directory as the flask app).
# If hosting on a server, the path will need to be changed to the absolute path of the database file.
db_path = 'Impact.db'

# Get the user's device type and assign it to a global variable.
@app.before_request
def get_device_type():
    """
    Determines the user's device type based on the user agent and assigns it to a global variable.
    """
    global user_device_type
    user_agent = request.user_agent.string.lower()
    if "android" in user_agent or "iphone" in user_agent or "ipad" in user_agent:
        user_device_type = "mobile"
    elif "windows" in user_agent or "macos" in user_agent:
        user_device_type = "desktop"
    else:
        user_device_type = "unknown"

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
    # FSU = populate_students("FSU")
    # NCCU = populate_students("NCCU")
    # WSSU = populate_students("WSSU")
    if user_device_type == "mobile":
        return render_template('students.html', current_year=current_year, TitleFontSize="65px")  # FSU=FSU, NCCU=NCCU, WSSU=WSSU
    else:
        return render_template('students.html', current_year=current_year, TitleFontSize="105px")  # FSU=FSU, NCCU=NCCU, WSSU=WSSU


@app.route('/admin')
def admin():
    """
    Placeholder route for the admin page.
    """
    pass
    # return render_template('admin.html')


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
            """.replace("Name", faculty[i][1]).replace("Title", faculty[i][2]).replace("School", faculty[i][3]).replace(
            "Email", faculty[i][4]).replace("Bio", faculty[i][5])).replace("Photo", faculty[i][6]).replace("Link",
                                                                                                        faculty[i][
                                                                                                            7]).replace(
            "Width", width).replace("Height", height)

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
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">School</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);font-size: 16px;">Email</h1>
                    <p class="teamprofiledescription"><span style="color: rgb(0, 0, 0);">Bio</span></p>
                </div>
            </div>
            """.replace("Name", jpl[i][1]).replace("Title", jpl[i][2]).replace("School", jpl[i][3]).replace("Email",
                                                                                                         jpl[i][
                                                                                                             4]).replace(
            "Bio", jpl[i][5])).replace("Photo", jpl[i][6]).replace("Width", width).replace("Height", height)

    return jplassembled


def populate_students(school):
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

    for i in range(len(students)):
        students_assembled += Markup("""
            <div class="row gy-4 row-cols-2 row-cols-md-4">
                    <div class="col">
                        <div class="card border-0 shadow-none">
                            <div class="card-body text-center d-flex flex-column align-items-center p-0"><img class="rounded-circle mb-3 fit-cover" width="130" height="130" src="static/images/Students/Photo" alt="https://cdn.bootstrapstudio.io/placeholders/1400x800.png">
                                <h5 class="fw-bold text-primary card-title mb-0"><strong>Name</strong></h5>
                                <p class="text-muted card-text mb-2">Tier</p>
                            </div>
                        </div>
                    </div>
                </div>
            """.replace("Name", students[i][1]).replace("Tier", students[i][2])).replace("Photo", students[i][3])

    return students_assembled


if __name__ == '__main__':
    app.run(debug=True)