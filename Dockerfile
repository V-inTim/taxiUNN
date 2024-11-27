FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
RUN pip install --upgrade pip


WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY /taxiunn /app/

EXPOSE 8000

# CMD ["python", "taxiunn/manage.py", "runserver", "localhost:8000"]