# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .serializers import CustomUserSerializer, EventSerializer, CategorySerializer, SubCategorySerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
import re
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Hashtag, Message, CustomUser, Category, SubCategory
from .forms import EventForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserRegistrationForm
from rest_framework import viewsets, permissions
from rest_framework.parsers import JSONParser
# from .serializers import EventSerializer


def home(request):
    events = Event.objects.all()
    return render(request, 'home.html', {'events': events})


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            event.participants.add(request.user)

            hashtags_str = form.cleaned_data.get('hashtags', '')
            hashtag_pattern = r'#([^#\s]+)'
            hashtags_list = re.findall(hashtag_pattern, hashtags_str)
            for tag_name in hashtags_list:
                hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
                event.hashtags.add(hashtag)
            return redirect('home')
    else:
        form = EventForm()
    return render(request, 'event_create.html', {'form': form})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})


@login_required
def join_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.is_full():
        # イベントが満員の場合の処理（メッセージの表示など）
        return redirect('event_detail', pk=pk)
    if request.user not in event.participants.all():
        event.participants.add(request.user)
    return redirect('event_detail', pk=pk)


def event_search(request):
    hashtag = request.GET.get('hashtag', None)
    if hashtag:
        events = Event.objects.filter(hashtags__name=hashtag)
    else:
        events = Event.objects.all()
    return render(request, 'event_search.html', {'events': events, 'hashtag': hashtag})


def chat_room(request, pk):
    event = get_object_or_404(Event, pk=pk)
    messages = Message.objects.filter(event=event)

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(event=event, sender=request.user, content=content)

    return render(request, 'chat_room.html', {'event': event, 'messages': messages})


# アカウント関連
def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request, id):
    user = get_object_or_404(CustomUser, id=id)  # IDでユーザーを取得
    return render(request, 'profile.html', {'user_profile': user})


class CustomLoginView(LoginView):
    template_name = 'login.html'


class CustomLogoutView(LogoutView):
    next_page = 'home'


# API


class EventListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    parser_classes = [JSONParser]  # 明示的にJSONのみを受け付ける
    permission_classes = [AllowAny]  # 認証されていないユーザーでもアクセス可能

    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            # オーガナイザーとして現在のユーザーを設定して保存
            event = serializer.save(organizer=request.user)

            # 自動生成されたパスコードを設定
            event.passcode = uuid.uuid4().hex[:12]
            event.save()

            # 作成者を participants に追加
            event.participants.add(request.user)

            # 更新されたイベントインスタンスで新しいシリアライザを作成
            serializer = EventSerializer(event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ログイン


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
        })
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# カテゴリーのリストを取得
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# サブカテゴリーのリストを取得


class SubCategoryListAPIView(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


# 特定のカテゴリーに属するサブカテゴリーを取得
class SubCategoriesByCategoryAPIView(generics.ListAPIView):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SubCategory.objects.filter(category_id=category_id)
