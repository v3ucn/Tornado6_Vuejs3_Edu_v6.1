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
```
docker build -t 'edu' .
```
```
docker run -d -p 8000:8000 edu 
```

访问：http://127.0.0.1:8000