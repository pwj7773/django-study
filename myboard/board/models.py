from django.db import models
from django.utils import timezone  # 시간 정보에 관한 모듈

# auth_user 테이블과 매핑되는 모델
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    # 번호는 pk설정 안하면 장고가 자동으로 id부여해줌
    #### 필드와 필드 사이에 ','금지 ####
    title = models.CharField(max_length= 100)  # 제목
    content = models.TextField(null=False, blank=False)  # 내용
    # writer = models.CharField(max_length=10)  # 작성자
    input_date = models.DateTimeField(default=timezone.now)  # 작성일
    view_count = models.IntegerField(default=0)  # 조회수
    # db에는 필드이름_기본키 로 열이 생성됨
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # java의 toString이랑 비슷하게
    # 객체 정보를 문자열로 돌려줌
    def __str__(self):
        return f'{self.id}: {self.title}'
    


class Reply(models.Model):
    # pk 자동 생성(id)
    # 게시글번호(fk)
    board_obj = models.ForeignKey(Board, on_delete=models.CASCADE)
    # 사용자(fk)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 댓글 내용
    reply_content = models.TextField(blank=False, null=False)
    # 작성시간
    input_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.reply_content