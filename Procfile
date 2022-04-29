release: chmod u+x reset_db.sh && ./reset_db.sh
web: gunicorn manage:app
worker: python -u manage.py run_worker
