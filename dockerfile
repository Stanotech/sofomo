FROM python:3.10

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt-get update && apt-get install -y netcat-openbsd

RUN groupadd -g $GROUP_ID appgroup && \
    useradd -m -u $USER_ID -g appgroup appuser

WORKDIR /app

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .
RUN chown -R appuser:appgroup /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]