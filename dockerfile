FROM python:3.10

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID appgroup && \
    useradd -m -u $USER_ID -g appgroup appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
