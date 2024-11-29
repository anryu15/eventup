from .models import CustomUser, Category, SubCategory
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Event, Category, SubCategory, Hashtag
import re


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False)
    organizer = serializers.StringRelatedField(read_only=True)
    passcode = serializers.CharField(read_only=True)
    participants = serializers.SerializerMethodField()

    # ハッシュタグのシリアライズとデシリアライズを分ける
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    hashtag_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'subcategory', 'capacity', 'participants',
            'registration_deadline', 'location', 'description', 'image',
            'participation_method', 'organizer', 'created_at', 'passcode',
            'event_date', 'hashtags', 'hashtag_names'
        ]

    def get_participants(self, obj):
        return [participant.username for participant in obj.participants.all()]

    def get_hashtag_names(self, obj):
        return [hashtag.name for hashtag in obj.hashtags.all()]

    def create(self, validated_data):
        hashtags = validated_data.pop('hashtags', [])
        event = Event.objects.create(**validated_data)

        # ハッシュタグの作成と関連付け
        for tag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag_name)
            event.hashtags.add(hashtag)

        return event


class CustomUserSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )
    subcategories = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
        many=True,
        required=False
    )
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False)
    token = serializers.SerializerMethodField()
    account_id = serializers.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'account_id', 'password', 'bio', 'profile_picture',
            'gender', 'age', 'preferred_region', 'categories', 'subcategories', 'token'
        ]
        extra_kwargs = {
            'username': {'required': False},  # usernameを必須から解除
        }

    def validate_account_id(self, value):
        # 先頭の「@」を削除
        value = value.lstrip('@')
        # 英数字とアンダースコアのみ許可
        if not re.match(r'^\w+$', value):
            raise serializers.ValidationError('account_idは英数字とアンダースコアのみ使用できます。')
        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        subcategories = validated_data.pop('subcategories', [])
        password = validated_data.pop('password')

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        user.categories.set(categories)
        user.subcategories.set(subcategories)

        return user

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }
