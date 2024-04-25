
# IMPACT Website

The IMPACT Website is designed as an interactive platform to visualize our current projects and the students, faculty, and JPL staff that are currently working on said projects. This project is developed by the ISL INTELLIGENT SYSTEMS LAB.

## Overview

This repository contains the source files for the IMPACT Website, including design files, database, and Flask application code. The website is built using Flask, a lightweight WSGI web application framework.

## Project Structure

- `IMPACT.bsdesign` - Website design file compatible with Bootstrap Studio.
- `IMPACT.drawio` - Diagram file illustrating the website architecture.
- `IMPACT.svg` - SVG file containing vector graphics related to the project.
- `Impact.db` - SQLite database file for the project.
- `flask_app.py` - Main Flask application that runs the website.
- `static/` - Directory containing static files like CSS, JS, and images.
- `templates/` - Directory containing HTML templates for the website.

## Getting Started

### Prerequisites

Before running the website, ensure you have the following installed:
- Python 3
- Flask
- SQLite3

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/ISL-INTELLIGENT-SYSTEMS-LAB/IMPACT_Website.git
cd IMPACT_Website
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Running the Application

To run the Flask application locally:

```bash
python flask_app.py
```

Navigate to `http://127.0.0.1:5000/` in your web browser to view the website.

## Contributing

Contributions to the IMPACT Website are welcome. Please fork the repository and submit pull requests to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/ISL-INTELLIGENT-SYSTEMS-LAB/IMPACT_Website/blob/main/LICENSE) file for details.

## Acknowledgments

- ISL INTELLIGENT SYSTEMS LAB team members
- All contributors who have participated in this project.
