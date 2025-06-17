## 项目概述

这是一个基于Vue的智能家居前端，支持用户登录，注册，设备管理，场景控制等功能。

# 项目启动

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

### 完成了前后端对接，前端启动只需要运行：
```
npm run  serve
```

## 项目架构

### 目录结构

```

在views中定义了添加设备，创建场景，登录，房间管理，用户主界面的vue文件。其中，添加设备和场景创建使用连接跳转，房间管理则作为用户主界面的子组件显示在主界面中。


#在components中定义了设备卡片的vue文件，在主界面中调用。

#在router中定义了路由，包括登录，注册，房间管理，设备
管理，场景管理等页面。

#store作为全局状态管理，保存了包括用户登录状态，设备列表，场景列表等信息。

#api中定义了与后端服务器的交互接口，包括登录，注册，获取设备列表，创建场景，控制设备等。

```
