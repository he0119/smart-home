# Smart Home

[![CI](https://github.com/he0119/smart-home/actions/workflows/main.yml/badge.svg)](https://github.com/he0119/smart-home/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/he0119/smart-home/branch/main/graph/badge.svg?token=N8K81G7A0Q)](https://codecov.io/gh/he0119/smart-home)

智慧家庭

需配合 [客户端](https://github.com/he0119/smart-home-flutter/releases) 使用

支持在网页，安卓和 Windows 上运行

## 主要功能

### 物品管理

管理物品的各种信息（存放位置，数量，价格，保质期）

### 留言板

发起话题和在对应话题下回复

### 博客

设置博客网址，在应用内直接访问和管理任意的博客网站

### 物联网

配合 [单片机](https://github.com/he0119/smart-home-device) 可以实现智能控制家庭设备

### 小爱同学

支持小爱同学自定义技能（当前仅支持查询物品位置）

## 部署

```bash
# 首先克隆代码到本地
git clone https://github.com/he0119/smart-home.git
# 复制并填写配置
cp .example.env .env
vim .env
# 下载 GeoIP 文件
# https://docs.djangoproject.com/zh-hans/5.1/ref/contrib/gis/geoip2/
# 并将下载好的文件放入 geoip 文件夹中
mv *.mmdb ./geoip
# 启动项目
sudo docker compose up -d
```
