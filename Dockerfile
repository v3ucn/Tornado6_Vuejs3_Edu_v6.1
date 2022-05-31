FROM mirekphd/python3.10-ubuntu20.04
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update --fix-missing -o Acquire::http::No-Cache=True
RUN apt install -y supervisor
RUN mkdir /root/tornado_edu
WORKDIR /root/tornado_edu
COPY requirements.txt ./
RUN yes | apt-get install gcc
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .
ENV LANG C.UTF-8

# supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN echo user=root >>  /etc/supervisor/supervisord.conf
# run
CMD ["/usr/bin/supervisord","-n"]