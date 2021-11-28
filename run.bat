@ECHO OFF
RUN set FLASK_APP=server/app
RUN flask run
PAUSE
