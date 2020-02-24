# Smart Home

智慧家庭

## 物品管理

管理物品存放位置

## 部署

首先克隆项目

```bash
git clone https://github.com/he0119/smart-home.git
```

利用 Docker 运行网站

```bash
sudo docker-compose up -d
sudo docker exec -it smart-home sh
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
```
