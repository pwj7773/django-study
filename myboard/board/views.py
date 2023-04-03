from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.core import serializers
from json import loads
from .models import Board, Reply
# Create your views here.

# 게시판 목록보기
def index(request):
    print('index() 실행 ')

    # 반환되는 queryset에 대해서 order_by함수 이용하면 특정 필드 기준으로 정렬
    # order_by에 들어가는 필드 이름 앞에 -를 붙이면 내림차순(DESC) 아니면 오름차순(ASC)
    result = None # 필터링된 리스트
    context = {}
    
    # request.GET : get방식으로 보낸 데이터들을 딕셔너리 타입으로 저장
    # print(request.GET)

    # 검색 조건과 검색 키워드가 있어야 필터링 실행
    if 'searchType' in request.GET and 'searchWord' in request.GET:
        search_type = request.GET['searchType'] # GET안의 문자열은
        search_word = request.GET['searchWord'] # html의 name 속성

        print('search_type: {}, search_word: {}'.format(search_type,search_word))

        # match: java switch랑 비슷
        match search_type:
            case 'title': # 검색기준이 제목일 때
                result = Board.objects.filter(title__contains = search_word)
            case 'writer': # 검색기준이 글쓴이일 때
                result = Board.objects.filter(writer__contains = search_word)
            case 'content': # 검색기준이 내용일 때
                result = Board.objects.filter(content__contains = search_word)

        # 검색을 했을때만 검색 기준과 키워드를 context에 넣는다
        context['searchType'] = search_type
        context['searchWord'] = search_word
    else : #QueryDict에 검색조건과 키워드가 없을 때
        result = Board.objects.all()

    # 검색 결과 또는 전체 목록을 id의 내림차순 정렬
    result = result.order_by('-id')  

    # 페이징 넣기
    # Paginator(목록, 목록에 보여줄 개수)
    paginator = Paginator(result, 10)
    
    # Paginator 클래스를 이용해서 자른 목록의 단위에서
    # 몇 번째 단위를 보여줄 것인지 정한다
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # context['board_list'] = result
    # 페이징한 일부 목록을 반환
    context['page_obj'] = page_obj
    
    return render(request, 'board/index.html', context)

def read(request, id):
    print('id=', id)

    board = Board.objects.get(id = id)

    # 고전적인 방법으로 댓글 가져오기
    # reply_list = Reply.objects.filter(board_obj = id).order_by('-id')

    # 조회수
    board.view_count = board.view_count + 1
    board.save()

    context = {
        'board':board,
        # 'replyList':reply_list
    }

    return render(request, 'board/read.html', context)


def home(request):
    return HttpResponseRedirect('/board/')

# 내가 따로 만든 로그인url이 있다면 
# 넘겨야 한다
@login_required(login_url='common:login')
def write(request):

    if request.method == 'GET':  # 요청 방식이 GET이면 화면 표시
        return render(request, 'board/board_form.html')
    
    else:  # 요청 방식이 POST면
        print(request.POST)
        print(request.FILES)
        # DB저장
        title = request.POST['title']
        content = request.POST['content']
        author = request.user #요청에 들어있는 User 객체
           
        # 객체.save()
        board = Board(
            title = title,
            author = author,
            content = content
        )
        # get 사용하는 이유는
        # 딕셔너리에 존재하지 않는 키를 딕셔너리[키] ㅡ> keyerror
        # 딕셔너리.get('키') -> none
        if request.FILES.get('uploadFile'):
            upload_file = request.FILES['uploadFile']
            # 요청에 들어있던 첨부파일을 모델에 설정
            board.attached_file = upload_file
            board.original_file_name = upload_file.name
        
        board.save()
        
        # 모델.object.create(값)
        # Board.objects.create(
        #     title = title,
        #     author = author,  # 유저 객체 저장
        #     content = content
        # )
        
        return HttpResponseRedirect('/board/')
    
@login_required(login_url='common:login')
def update(request, id):
    
    board = Board.objects.get(id = id)

    # 글쓴이와 현재 접속한 사용자의 username이 다르면 목록으로 
    if board.author.username != request.user.username:
        return HttpResponseRedirect('/board/')
    
    if request.method == 'GET':
        context = {'board': board }
        return render(request, 'board/board_update.html', context)
    else:
        board.title = request.POST['title']
        board.content = request.POST['content']

        # 첨부파일이 있으면 
        if request.FILES.get('uploadFile'):
            upload_file = request.FILES['uploadFile']
            # 요청에 들어있던 첨부파일을 모델에 설정
            board.attached_file = upload_file
            board.original_file_name = upload_file.name
        else: # 파일이 없으면
            board.attached_file = None
            board.original_file_name = None

        board.save()
    return HttpResponseRedirect('/board/')

@login_required(login_url='common:login')
def delete(request, id):
    print(id)
    # 해당 객체를 가져와서 삭제
    board = Board.objects.get(id = id)

    # 글 작성자의 id와 접속한 사람의 id가 같을 때
    if board.author.username == request.user.username:
        board.delete()
    # 다를 때
    return HttpResponseRedirect('/board/')

def write_reply(request, id):
    print(request.POST)
    
    user = request.user
    reply = loads(request.body) #요청의 body를 해석
    print(reply)

    reply_text = reply['replyText']

    # Reply.objects.create(
    #     user = user,
    #     reply_content = reply_text,
    #     board_obj = Board.objects.get(id = id)
    # )

    # queryset 이용
    board = Board.objects.get(id=id)
    board.reply_set.create(
        reply_content = reply_text,
        user = user
    )

    # return HttpResponseRedirect('/board/'+ str(id))
    return JsonResponse({'reault': 'success'})

def delete_reply(request, id):
    # print(f'id:{id} rid:{rid}')
  
    rid = (loads(request.body))['rid']

    Board.objects.get(id=id).reply_set.get(id=rid).delete()
    # Reply.objects.get(id = rid).delete() 위에 코드랑 같은 내용

    # return HttpResponseRedirect('/board/'+ str(id))
    return JsonResponse({"result" : "success"})

def update_reply(request, id):

    if request.method == 'GET':
        rid = request.GET['rid']

        reply = Board.objects.get(id = id).reply_set.get(id = rid)

        context = {
            # rid에 해당하는 reply 객체의 id, replyText
            'rid': rid,
            'replyText': reply.reply_content
        }
        
        return JsonResponse(context)
    
    else :
        # rid = request.POST['rid']
        request_body = loads(request.body)

        rid = request_body['rid']
        reply_text = request_body['replyText']

        reply = Board.objects.get(id = id).reply_set.get(id = rid)

        # 폼에 들어있던 새로운 댓글로 수정
        reply.reply_content = reply_text
        reply.save() # 이외의 정보가 바뀌는게 없으므로 바로 저장

        # return HttpResponseRedirect('/board/'+ str(id))
        return JsonResponse({'result': 'success'})

def call_ajax(request):
    print('성공?')
    print(request.POST)

    # JSON.stringify 하면 아래 표현 사용 불가
    # print(request.POST['txt'])
    
    data = loads(request.body)
    print('템플릿에서 보낸 데이터',data)
    print(data['txt'])
    print(type(data))
    return JsonResponse({'result': 'ㅊㅋ'})

def load_reply(request, id):
    
    reply_list = Board.objects.get(id = id).reply_set.all()

    reply_dict_list = []
    # reply_list 정보를 가지고 dictionary 만들기
    for reply in reply_list:
        reply_dict = {
            'id': reply.id,
            'username': reply.user.username,
            'replyText': reply.reply_content,
            'inputDate': reply.input_date
        }
    
        reply_dict_list.append(reply_dict)

    context = {'replyList': reply_dict_list}

    return JsonResponse(context)

def download(request,id):
    print('download/',id)
    
    board = Board.objects.get(id = id)
    attached_file = board.attached_file
    original_file_name = board.original_file_name
    
    # 글 번호에 달려있던 첨부파일로 파일형식 응답 객체 생성
    response = FileResponse(attached_file)
    response["Content-Disposition"] = 'attachment; filename=%s' %original_file_name

    return response