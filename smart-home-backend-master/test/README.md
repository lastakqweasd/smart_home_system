### 功能测试

test_function.py ：测试所有的功能

```
python test_function.py
```

### 性能测试

1、test_locust.py：locust测试，测试一定规模的用户数量下系统表现

2、test_load.py：测试在不同数量用户下的系统性能表现情况（用到了test_locust.py，然后画图）

画图的程序draw.py：如果test_load.py运行失败直接运行画图程序

```
locust -f test_locust.py

python test_load.py
python draw.py
```

### 安全性测试

test_jwt.py：测试身份认证

test_safety.py：测试其他安全问题

```
python test_jwt.py -v
python test_safety.py -v
```

### 兼容性测试
