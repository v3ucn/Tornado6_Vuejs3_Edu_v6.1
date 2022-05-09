FROM mirekphd/python3.10-ubuntu20.04

RUN mkdir /root/edu
WORKDIR /root/edu
COPY requirements.txt ./
RUN apt-get update --fix-missing -o Acquire::http::No-Cache=True
RUN yes | apt-get install gcc
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .
ENV LANG C.UTF-8

CMD ["python3","/root/blog/main.py"]