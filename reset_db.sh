source venv/bin/activate
python manage.py recreate_db
python manage.py setup_dev
python manage.py add_fake_data
