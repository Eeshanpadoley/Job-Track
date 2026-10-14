# JobTrack — Job Application Analytics & Skill Intelligence System

**JobTrack** is a Django-based web application designed to help job seekers manage job applications, track recruitment progress, and analyze application outcomes through data-driven insights.

## Overview

JobTrack brings job application tracking and analytics into one place. It helps users organize applications, monitor interview progress, identify skill gaps, and maintain their resume library.

## Key Features

- **User Authentication:** Secure registration and login.
- **Application Management:** Add, view, search, filter, edit, and delete job applications.
- **Analytics Dashboard:** Track application statuses, interview progress, and recruitment outcomes.
- **Data Analysis:** Generate insights using Python and Pandas.
- **Skill Gap Analysis:** Compare saved skills with job requirements.
- **Resume Library:** Upload and manage resumes.
- **Follow-up Tracking:** Maintain recruiter notes, interview notes, and follow-up dates.
- **CSV Export:** Export application analytics for further analysis.
- **Responsive Interface:** Navigate the application across different screen sizes.

## Technology Stack

- **Backend:** Python, Django
- **Data Analysis:** Pandas
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git and GitHub

## Run Locally

1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Create and activate a virtual environment.
4. Install the dependencies from `requirements.txt`.
5. Apply database migrations.
6. Start the Django development server.

```bash
python manage.py migrate
python manage.py check
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser after the development server starts.

## Project Purpose

This project demonstrates practical application development using Django, database management, and data analysis to solve a real-world job-search organization problem.

## Future Improvements

- Advanced application trend analysis
- More detailed skill-demand insights
- Enhanced analytics visualizations
- Deployment to a production hosting platform

---

**Developer:** Eeshan Padoley  
**GitHub:** [Eeshanpadoley](https://github.com/Eeshanpadoley)
