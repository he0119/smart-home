# Smart Home

智慧家庭

## 物品管理

管理物品存放位置

## 部署

```bash
sudo docker exec -it smart-home sh
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
```
