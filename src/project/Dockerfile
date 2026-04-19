FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY .streamlit/ .streamlit/
COPY core/ core/
COPY pages/ pages/
COPY app.py ./

EXPOSE 7777

CMD ["streamlit", "run", "app.py", "--server.port=7777", "--server.address=0.0.0.0"]
