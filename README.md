1 create your environment
2 _**activate your environment**_
3 pip install -r requirements.txt _to install all packages_
4 add the following following variables



SECRET_KEY=sxlbrbw4*e5b)eq%$)tj-3(_9)jv8li+!uki0)5p04ruz47us#
DEBUG=True
EMAIL_HOST=kartexample.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=support@kartoexample.com
EMAIL_HOST_PASSWORD=#refffdd
DEFAULT_FROM_EMAIL=EMAIL_HOST_USER
DEFAULT_FROM_EMAIL=Oftmart Support <sss@example.com>

5 create migrations through _python manage.py makemigrations_
6 create database tables with _python manage.py migrate_
7 run the project with _python manage.py runserver_
8 add data with coordinates in the admin page