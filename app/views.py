from random import randrange, choice, shuffle

from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import mixins, viewsets, filters
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from app.filters import MovieFilter
from app.models import Movie, Tv, Shows, Animation, Fuli, TvList, ShowList, AnimationList
from app.serializers import MovieSerializer, TvSerializer, ShowsSerializer, AnimationSerializer, FuliSerializer, \
    TvListSerializer, ShowListSerializer, AnimationListSerializer


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if not all([username, email, password, password2]):
            return render(request, 'register.html', {'hint': '填写信息不完整,请重新填写'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'hint': '用户名已存在,请重新填写'})
        if password != password2:
            return render(request, 'register.html', {'hint': '两次密码不一样,请重新填写'})
        if len(password) < 8:
            return render(request, 'register.html', {'hint': '密码至少8位'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'hint': '邮箱已被使用,请重新填写'})
        User.objects.create_user(username=username, password=password, email=email)
        return HttpResponseRedirect(reverse('video:login'))


class CustomBackend(ModelBackend):
    """邮箱也能登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('video:index'))
        else:
            if not all([username, password]):
                return render(request, 'login.html', {'hint': '请填写完整的信息'})
            else:
                return render(request, 'login.html', {'hint': '用户名或密码错误'})


def logout(request):
    if request.method == 'GET':
        auth.logout(request)
        return HttpResponseRedirect(reverse('video:login'))


def index(request):
    if request.method == 'GET':
        user = request.user
        if user.id:
            user_token = Token.objects.filter(user=user).first()
            token = user_token.key
            return render(request, 'index.html', {'token': token})
        return render(request, 'index.html')


def manual(request):
    if request.method == 'GET':
        return render(request, 'manual.html')


def test(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        pages = []
        n = 1
        for _ in movies[::30]:
            pages.append(n)
            n += 1
        return render(request, 'test.html', {'pages': pages})


class MySourcePageNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 30
    # 默认每页显示3个，可以通过url传入?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    # 最大页数不超过10
    max_page_size = None
    # 获取页码数的
    page_query_param = "page"


class MyViewPageNumberPagination(PageNumberPagination):
    # 每页显示多少个
    page_size = 100
    # 默认每页显示3个，可以通过url传入?page=2&size=4,改变默认每页显示的个数
    page_size_query_param = "size"
    # 最大页数不超过10
    max_page_size = 10
    # 获取页码数的
    page_query_param = "page"


# 重写ListModelMixin
class MyListModelMixin(mixins.ListModelMixin):
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        # 自定义随机获取参数rand
        rand = request.GET.get('rand')
        if rand:
            # 先过滤(列表不支持框架自带过滤)
            queryset = self.filter_queryset(self.get_queryset())
            # 然后随机获取
            queryset = list(queryset)
            shuffle(queryset)

        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MovieSource(MyListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = MySourcePageNumberPagination
    # 使用搜索功能后，过滤失效，可以注释掉相关代码
    # filter_class = MovieFilter
    filter_backends = [filters.SearchFilter]
    search_fields = ['movie_name', 'movie_type', 'release_time']


class TvSource(MyListModelMixin,
               viewsets.GenericViewSet):
    queryset = Tv.objects.all()
    serializer_class = TvSerializer
    pagination_class = MySourcePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['tv_name', 'tv_type', 'release_time']


class ShowsSource(MyListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Shows.objects.all()
    serializer_class = ShowsSerializer
    pagination_class = MySourcePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['show_name', 'show_type', 'release_time']


class AnimationSource(MyListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Animation.objects.all()
    serializer_class = AnimationSerializer
    pagination_class = MySourcePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['animation_name', 'animation_type', 'release_time']


class FuliSource(MyListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Fuli.objects.all()
    serializer_class = FuliSerializer
    pagination_class = MySourcePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['fuli_name', 'fuli_type', 'release_time']


class TvListView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        # 自定义一个电视剧name参数
        name = request.GET.get('name')
        rand = randrange(TvList.objects.all().count())
        if name:
            # 获取电视剧名为name的所有集数
            tv_list = TvList.objects.filter(tv_name=name)
            # 如果找不到则随机获取一集电视剧
            if not tv_list:
                tv_list = TvList.objects.filter(id=rand)
        else:
            # 随机获取一集电视剧
            tv_list = TvList.objects.filter(id=rand)
        # 创建分页对象，这里是自定义的MyPageNumberPagination
        page = MyViewPageNumberPagination()
        # 获取分页的数据
        tv_list_page = page.paginate_queryset(queryset=tv_list, request=request, view=self)
        # 对数据进行序列化
        ser = TvListSerializer(instance=tv_list_page, many=True)
        # return Response(ser.data)  # 不含上一页下一页
        return page.get_paginated_response(ser.data)


class ShowListView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        # 自定义一个综艺name参数
        name = request.GET.get('name')
        rand = randrange(ShowList.objects.all().count())
        if name:
            # 获取电视剧名为name的所有集数
            show_list = ShowList.objects.filter(show_name=name)
            # 如果找不到则随机获取一集电视剧
            if not show_list:
                show_list = ShowList.objects.filter(id=rand)
        else:
            # 随机获取一期综艺
            show_list = ShowList.objects.filter(id=rand)
        # 创建分页对象，这里是自定义的MyPageNumberPagination
        page = MyViewPageNumberPagination()
        # 获取分页的数据
        show_list_page = page.paginate_queryset(queryset=show_list, request=request, view=self)
        # 对数据进行序列化
        ser = ShowListSerializer(instance=show_list_page, many=True)
        # return Response(ser.data)  # 不含上一页下一页
        return page.get_paginated_response(ser.data)


class AnimationListView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        # 自定义一个动漫name参数
        name = request.GET.get('name')
        rand = randrange(AnimationList.objects.all().count())
        if name:
            animation_list = AnimationList.objects.filter(animation_name=name)
            if not animation_list:
                animation_list = AnimationList.objects.filter(id=rand)
        else:
            # 获取所有数据
            animation_list = AnimationList.objects.filter(id=rand)
        # 创建分页对象，这里是自定义的MyPageNumberPagination
        page = MyViewPageNumberPagination()
        # 获取分页的数据
        animation_list_page = page.paginate_queryset(queryset=animation_list, request=request, view=self)
        # 对数据进行序列化
        ser = AnimationListSerializer(instance=animation_list_page, many=True)
        # return Response(ser.data)  # 不含上一页下一页
        return page.get_paginated_response(ser.data)
