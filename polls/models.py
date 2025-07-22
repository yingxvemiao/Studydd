from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class StudentInfo(models.Model):
    stu_id=models.CharField(primary_key=True,max_length=20)
    stu_name=models.CharField(max_length=20)
    stu_gender=models.CharField(max_length=20)
    stu_mbti=models.CharField(max_length=20)
    stu_email=models.CharField(max_length=40)
    stu_pwd=models.CharField(max_length=20)
    stu_area=models.CharField(max_length=20)
    stu_style=models.CharField(max_length=20)
    stu_score=models.IntegerField()
    stu_tag=models.CharField(max_length=1)

class Chat(models.Model):
    chat_id=models.CharField(primary_key=True,max_length=20)
    chat_time=models.CharField(max_length=45)
    chat_name=models.CharField(max_length=45)
    chat_str=models.CharField(max_length=300)

class Lesson(models.Model):
    les_id=models.CharField(primary_key=True,max_length=20)
    les_name=models.CharField(max_length=30)
    les_str=models.CharField(max_length=300)
    les_score=models.CharField(max_length=20)

class Love(models.Model):
    love_id=models.CharField(primary_key=True,max_length=20)
    love_a=models.CharField(max_length=30)
    love_b=models.CharField(max_length=30)

class Card(models.Model):
    card_id=models.CharField(primary_key=True,max_length=20)
    card_name=models.CharField(max_length=20)
    card_date=models.CharField(max_length=30)