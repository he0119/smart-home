# Smart Home

智慧家庭

需配合 [客户端](https://github.com/he0119/smart-home-flutter/releases) 使用

## 物品管理

管理物品的各种信息（存放位置，数量，价格，保质期）

## 留言板

发起话题和在对应话题下回复

## 小爱同学

支持小爱同学自定义技能（当前仅支持查询物品位置）

## 物联网

配合 [单片机](https://github.com/he0119/smart-home-device) 可以实现智能控制家庭设备

## 部署

首先克隆项目

```bash
git clone https://github.com/he0119/smart-home.git
```

重命名 `.example.env` 为 `.env` 并按照注释填写内容

利用 Docker 运行网站

```bash
sudo docker-compose up web -d
sudo docker exec -it smart-home sh
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
# 先配置好数据库，管理员之后再启动 Celery
sudo docker-compose up -d
```

## 备份与还原

### Django import / export

通过管理页面导出数据或导入数据

### [PostgreSQL](https://www.postgresql.org/docs/12/backup.html)

通过命令来备份或还原

```bash
sudo docker exec postgres pg_dump -U postgres postgres > backup.sql
# 这样可以排除设备数据表的内容
sudo docker exec postgres pg_dump --exclude-table-data=iot_*data -U postgres postgres > backup.sql
# --set ON_ERROR_STOP=on: 一旦出错便停止
# --single-transaction: 把整个输入当成一个单独数据库事务，要么全部成功，要么全部失败
sudo docker exec -i postgres psql --set ON_ERROR_STOP=on --single-transaction -U postgres postgres < backup.sql
```
