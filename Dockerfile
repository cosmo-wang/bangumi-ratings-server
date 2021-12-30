FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /bangumi-ratings-server
COPY . /bangumi-ratings-server

RUN pip install -r requirements.txt

CMD ["/bin/sh", "-c", "python3 manage.py migrate && python3 manage.py collectstatic --noinput && ./create_super_user.sh && uwsgi uwsgi.ini"]
