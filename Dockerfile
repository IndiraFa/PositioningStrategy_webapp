FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/src
RUN adduser --disabled-password myuser
USER myuser

EXPOSE 8501

CMD ["streamlit", "run", "src/Homepage.py"]
