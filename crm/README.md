# CRM Application Setup

This application uses Celery and Celery Beat to generate scheduled reports.

### Prerequisites

- A running Redis server. You can run one using Docker:
  `docker run -d -p 6379:6379 redis`

### Installation

1. Install project dependencies:
   `pip install -r requirements.txt`

2. Run Django migrations:
   `python manage.py migrate`

### Running the Application

To run the application with Celery, you'll need three separate terminals:

1. **Start the Django development server:**
   `python manage.py runserver`

2. **Start the Celery worker:**
   `celery -A crm worker -l info`

3. **Start the Celery Beat scheduler:**
   `celery -A crm beat -l info`

### Verification

- The report will be logged to `/tmp/crm_report_log.txt` every Monday at 6:00 AM.
- You can manually test the task by running:
  `python manage.py shell -c "from crm.tasks import generate_crm_report; generate_crm_report.delay()"`