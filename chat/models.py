# models.py
from django.contrib.auth.base_user import BaseUserManager
import re
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"#{self.name}"


class CustomUserManager(BaseUserManager):
    def create_user(self, account_id, email, password=None, **extra_fields):
        if not account_id:
            raise ValueError('The account_id must be set')
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(account_id=account_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, account_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(account_id, email, password, **extra_fields)


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    username = models.CharField(max_length=150, unique=False)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    preferred_region = models.CharField(max_length=100, blank=True, null=True)
    account_id = models.CharField(max_length=30, unique=True, blank=False, null=False)

    categories = models.ManyToManyField(Category, blank=True, related_name='interested_users')
    subcategories = models.ManyToManyField(SubCategory, blank=True, related_name='interested_users')

    USERNAME_FIELD = 'account_id'  # 認証に使用するフィールドを指定
    REQUIRED_FIELDS = ['email']    # スーパーユーザー作成時に必要なフィールド

    objects = CustomUserManager()

    def __str__(self):
        return f"@{self.account_id}" if self.account_id else self.username


class Event(models.Model):
    PARTICIPATION_METHOD_CHOICES = [
        ('request', 'Participation Request → Approval → Join'),
        ('direct', 'Join Button → Join'),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    capacity = models.IntegerField()
    participants = models.ManyToManyField(CustomUser, related_name='joined_events', blank=True)
    registration_deadline = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    participation_method = models.CharField(max_length=10, choices=PARTICIPATION_METHOD_CHOICES, default='direct')
    organizer = models.ForeignKey(CustomUser, related_name='organized_events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    passcode = models.CharField(max_length=12, unique=False)
    event_date = models.DateTimeField(null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='related_events', blank=True)

    def clean(self):
        if self.passcode and not re.match(r'^[a-zA-Z0-9]*$', self.passcode):
            raise ValidationError('Passcode can only contain alphanumeric characters.')
        if not self.category and self.subcategory:
            raise ValidationError('Subcategory cannot be specified without a category.')

    def save(self, *args, **kwargs):
        if not self.passcode:
            self.passcode = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def is_full(self):
        return self.participants.count() >= self.capacity

    def __str__(self):
        return self.title


class Message(models.Model):
    event = models.ForeignKey(Event, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender.username}: {self.content[:20]}'
