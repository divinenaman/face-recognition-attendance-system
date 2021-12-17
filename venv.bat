@ECHO OFF
CALL .\venv\Scripts\activate
set FLASK_APP=server/app
flask run
