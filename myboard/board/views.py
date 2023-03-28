from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from .models import Board
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

    # 조회수
    board.view_count = board.view_count + 1
    board.save()

    context = {
        'board':board
    }

    return render(request, 'board/read.html', context)


def home(request):
    return HttpResponseRedirect('/board/')


def write(request):

    if request.method == 'GET':  # 요청 방식이 GET이면 화면 표시
        return render(request, 'board/board_form.html')
    
    else:  # 요청 방식이 POST면
        # DB저장
        title = request.POST['title']
        content = request.POST['content']
        
        # 현재 세션 정보에서 writer라는 키를 가진 데이ㅣ터 취득
        session_writer = request.session.get('writer')
        if not session_writer:  # 세션에 정보가 없는 경우
            # 폼에서 가져온 writer값 세션에 저장
            request.session['writer'] = request.POST['writer']

        print(session_writer)
        
        # 객체.save()
        # board = Board(
        #     title = title,
        #     writer = writer,
        #     content = content
        # )
        # board.save()
        
        # 모델.object.create(값)
        Board.objects.create(
            title = title,
            writer = request.session.get('writer'),  # 세션에 있는 값 저장
            content = content
        )
        return HttpResponseRedirect('/board/')
    

def update(request, id):
    
    board = Board.objects.get(id = id)

    if request.method == 'GET':
        context = {'board': board }
        return render(request, 'board/board_update.html', context)
    else:
        board.title = request.POST['title']
        board.writer = request.POST['writer']
        board.content = request.POST['content']
        board.save()

    return HttpResponseRedirect('/board/')


def delete(request, id):
    print(id)
    # 해당 객체를 가져와서 삭제
    Board.objects.get(id = id).delete()

    return HttpResponseRedirect('/board/')