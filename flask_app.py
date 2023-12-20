from flask import Flask, render_template, request, redirect # request and redirect are not in use yet but they will be used for the admin page.
from markupsafe import Markup
import sqlite3
import datetime

# Gets the current year for the footer and sets it as a global variable. This is passed to the templates.
current_date = datetime.date.today()
current_year = current_date.year

app = Flask(__name__)

# Path to the database file (The database used is SQLite and is stored in the same directory as the flask app).
db_path = 'Impact.db'


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
    return render_template('faculty.html', faculty=faculty, current_year=current_year)


@app.route('/jplResearchers')
def jplResearchers():
    """
    Renders the jpl_researchers.html template with the JPL researchers data populated from the database and the current year.
    """
    jpl = jplPopulate()
    return render_template('jpl_researchers.html', jpl=jpl, current_year=current_year)


@app.route('/students')
def student():
    """
    Renders the students.html template with the current year.
    """
    return render_template('students.html', current_year=current_year)


@app.route('/admin')
def admin():
    """
    Placeholder route for the admin page.
    """
    pass
    # return render_template('admin.html')


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

    for i in range(len(faculty)):
        factultyassembled += Markup("""
            <div class="row">
                <div class="col-md-6 col-xxl-12" style="text-align: center;background: var(--bs-body-bg);width: 100%;margin: auto;padding-bottom: 76px;">
                    <img class="rounded-circle teamprofilepictures" style="overflow: hidden;width: initial;" width="400px" height="400px" src="static/images/Faculty/Photo">
                    <a href="Link" target="_blank"><h1 class="teamprofilenames">Name</h1></a>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">Title</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">School</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);font-size: 16px;">Email</h1>
                    <p class="teamprofiledescription"><span style="color: rgb(0, 0, 0);">Bio</span></p>
                </div>
            </div>
            """.replace("Name", faculty[i][1]).replace("Title", faculty[i][2]).replace("School", faculty[i][3]).replace("Email", faculty[i][4]).replace("Bio", faculty[i][5])).replace("Photo", faculty[i][6]).replace("Link", faculty[i][7])

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

    for i in range(len(jpl)):
        jplassembled += Markup("""
            <div class="row">
                <div class="col-md-6 col-xxl-12" style="text-align: center;background: var(--bs-body-bg);width: 100%;margin: auto;padding-bottom: 76px;">
                    <img class="rounded-circle teamprofilepictures" style="overflow: hidden;width: initial;" width="400px" height="400px" src="static/images/JPL/Photo">
                    <h1 class="teamprofilenames">Name</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">Title</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);">School</h1>
                    <h1 class="teamprofileprofessions" style="color: rgb(128, 128, 128);font-size: 16px;">Email</h1>
                    <p class="teamprofiledescription"><span style="color: rgb(0, 0, 0);">Bio</span></p>
                </div>
            </div>
            """.replace("Name", jpl[i][1]).replace("Title", jpl[i][2]).replace("School", jpl[i][3]).replace("Email", jpl[i][4]).replace("Bio", jpl[i][5])).replace("Photo", jpl[i][6])

    return jplassembled


if __name__ == '__main__':
    app.run(debug=True)