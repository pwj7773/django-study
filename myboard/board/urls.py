from django.urls import path

from.import views

urlpatterns = [
    # board/라면
    path('', views.index, name='index'),
    # 글읽기 주소 /board/0
    path('<int:id>/', views.read, name='detail'),
    # 글쓰기 주소
    path('write/', views.write, name='write'),
    # 수정 주소
    path('<int:id>/update/', views.update, name='update'),
    # 삭제 주소
    path('<int:id>/delete/', views.delete, name='delete'),

]