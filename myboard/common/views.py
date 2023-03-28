from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
# 장고가 제공하는 기본 회원가입 폼
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def index(request):

    return render(request, 'common/index.html')

def signup(request):
    if request.method == 'POST':
        #요청 객체가 담고있는 정보로 사용자 생성 폼 만든다
        print(request.POST)
        form = UserCreationForm(request.POST)

        if form.is_valid(): #폼의 내용이 유효하다면
            form.save() #db에 폼 정보 저장

            # 폼에 입력한 값 가져오기
            username = form.cleaned_data.get('username')
            row_password = form.cleaned_data.get('password1')

            # 사용자 인증
            user = authenticate(username = username, password = row_password)
            # 로그인
            login(request, user)

            return redirect('/')
    else:
        # get방식으로 요청이오면 비어있는 사용자 생성 폼을 만든다
        form = UserCreationForm
    return render(request, 'common/signup.html', {'form':form})