FROM python:3.8
WORKDIR /soft

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

COPY . .

CMD ["gunicorn", "run:app", "-c", "./gunicorn.conf.py"] 