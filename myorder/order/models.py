from django.db import models
from django.utils import timezone # 시간정보 모듈

class Order(models.Model):
    # 번호는 pk 설정 안하면 장고가 자동으로 id 부여해줌
    ### 필드와 필드 사이에 컴마 금지 ###
    order_time = models.DateTimeField(default = timezone.now) # 주문일시
    order_text = models.TextField(null=False) # 주문내역
    price = models.IntegerField(default=0, null=False) # 금액
    address = models.TextField(default="포장") # 배달주소

class User(models.Model):
    user_id = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
