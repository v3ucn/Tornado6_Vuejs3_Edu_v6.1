## 数据库：Mysql/Redis;
## 开发语言：Python3.10.4
## 前端：Vue.js3.0+Axios.js
## 数据库脚本 /scripts/init.sql

## 安装依赖
```
pip3 install -r requirements.txt
```
## 运行项目
```
python3 main.py
```

访问：http://127.0.0.1:8000

## Docker方式运行项目

修改config.py文件，mysql_host = "宿主机ip",redis_link = "宿主机ip"

```
docker build -t 'edu' .
```
```
docker run -d -p 8000:8000 edu 
```

访问：http://127.0.0.1:8000

## Docker-compose方式运行项目

修改config.py文件，mysql_host = "mysql",redis_link = "redis"

```
docker-compose up
```

访问：http://127.0.0.1:8000

## Kubernetes方式运行项目

修改config.py文件，mysql_host = "mysql",redis_link = "redis"

```
cd k8s
kubectl apply $(ls *.yaml | awk ' { print " -f " $1 } ')
```

访问：http://127.0.0.1:32143

## DockerHub
 
```
docker pull zcxey2911/tornado_edu:latest
```