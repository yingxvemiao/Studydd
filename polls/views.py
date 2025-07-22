import json
from math import fabs
# from pyexpat.errors import messages
import random
import re
from django.shortcuts import redirect, render
from .models import Card, Chat, Lesson, Love, StudentInfo
from django.shortcuts import render, HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
import uuid
from datetime import date, datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Lesson
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from polls import models
from django.contrib import messages

MBTI_TYPES = [
    "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

def validate_password(password):
    """密码强度检验（包含5种规则）[9,11](@ref)"""
    errors = []
    
    # 长度检查
    if len(password) < 8:
        errors.append("长度至少8个字符")
    
    # 大写字母检查
    if not re.search(r'[A-Z]', password):
        errors.append("必须包含大写字母")
    
    # 小写字母检查
    if not re.search(r'[a-z]', password):
        errors.append("必须包含小写字母")
    
    # 数字检查
    if not re.search(r'\d', password):
        errors.append("必须包含数字")
    
    # 特殊字符检查
    if not re.search(r'[!@#$%^&*()_+=\-{}$$$$|:;"<>,.?/]', password):
        errors.append("必须包含特殊字符(!@#$%^&*等)")
    
    return errors

def toLogin_view(request):
    """登录页面视图[2](@ref)"""
    return render(request, 'login.html')

def Login_view(request):
    u = request.POST.get("user", '')
    p = request.POST.get("pwd", '')

    if not u or not p:
        return render(request, 'prompt.html', {
            'icon': 'fas fa-exclamation-triangle',
            'icon_class': 'warning',
            'message': '请输入用户名和密码'
        }, status=400)

    try:
        student = StudentInfo.objects.get(stu_name=u)
        if student.stu_pwd == p:
            # 存储用户会话信息
            request.session['username'] = u
            request.session['is_logged_in'] = True
            
            # 跳转到欢迎页面
            return redirect('/polls/welcome/')
        else:
            return render(request, 'prompt.html', {
                'icon': 'fas fa-lock',
                'icon_class': 'error',
                'message': '密码错误'
            }, status=401)
    except StudentInfo.DoesNotExist:
        return render(request, 'prompt.html', {
            'icon': 'fas fa-user-times',
            'icon_class': 'error',
            'message': '用户不存在'
        }, status=404)

def toregister_view(request):
    """注册页面视图[6](@ref)"""
    return render(request, 'register.html', {'mbti_types': MBTI_TYPES})

def register_view(request):
    """注册处理视图（含密码强度/用户名/邮箱判重）[7,8,10](@ref)"""
    form_data = {
        'user': request.POST.get("user", ''),
        'pwd': request.POST.get("pwd", ''),
        'gender': request.POST.get("gender", ''),
        'mbti': request.POST.get("mbti", ''),
        'email': request.POST.get("email", '')
    }
    
    errors = {'user': '', 'pwd': '', 'email': ''}
    has_errors = False
    
    # 用户名判重
    if StudentInfo.objects.filter(stu_name=form_data['user']).exists():
        errors['user'] = "用户名已被占用"
        has_errors = True
    
    # 邮箱判重
    if StudentInfo.objects.filter(stu_email=form_data['email']).exists():
        errors['email'] = "此邮箱已注册过账号"
        has_errors = True
    
    # 密码强度验证
    password_errors = validate_password(form_data['pwd'])
    if password_errors:
        errors['pwd'] = "密码强度不足: " + "，".join(password_errors)
        has_errors = True
    
    # 返回错误信息
    if has_errors:
        return render(request, 'register.html', {
            'form_data': form_data,
            'error_user': errors['user'],
            'error_pwd': errors['pwd'],
            'error_email': errors['email'],
            'mbti_types': MBTI_TYPES
        })
    
    # 创建新用户
    try:
        StudentInfo.objects.create(
            stu_id=str(random.randint(100000, 999999)),
            stu_name=form_data['user'],
            stu_pwd=form_data['pwd'],
            stu_gender=form_data['gender'],
            stu_mbti=form_data['mbti'],
            stu_email=form_data['email'],
            stu_area='0',
            stu_style='ABCDABCDABCDABCDABCD',
            stu_score='60'
        )
        return render(request, 'prompt2.html', {
            'icon': 'fas fa-check-circle',
            'icon_class': 'success',
            'message': '注册成功！'
        })
    except Exception as e:
        return render(request, 'register.html', {
            'form_data': form_data,
            'error_pwd': f'注册失败: {str(e)}',
            'mbti_types': MBTI_TYPES
        })
def prompt_view(request):
    return render(request, 'prompt.html')
def prompt2_view(request):
    return render(request, 'prompt2.html')
def prompt3_view(request):
    if 'username' not in request.session:
        return redirect('/polls/login/')  # 未登录则跳转到登录页面
    return render(request, 'prompt3.html')
def welcome_view(request):
    if 'username' not in request.session:
        return redirect('/polls/login/')  # 未登录则跳转到登录页面
    """登录成功后的欢迎页面（含进入网站和注销按钮）"""
    return render(request, 'welcome.html')
    
def logout_view(request):
    # 清除会话
    request.session.flush()
    # 重定向到登录页面
    return redirect('/polls/login/')

def logout_confirm_view(request):
    """注销确认页面"""
    return render(request, 'logout_confirm.html')

def home_view(request):
    # 检查用户是否登录
    if 'username' not in request.session:
        return redirect('/polls/login/')  # 未登录则跳转到登录页面
    
    username = request.session['username']
    return render(request, 'home.html', {'username': username})

def kill_view(request):
    # 获取当前用户名
    if 'username' in request.session:
        username = request.session['username']
        # 从数据库中删除用户
        try:
            user = StudentInfo.objects.get(stu_name=username)
            user.delete()
        except StudentInfo.DoesNotExist:
            pass  # 如果用户不存在，则忽略
        
        # 清除会话
        request.session.flush()
    
    # 重定向到登录页面
    return redirect('/polls/login/')

### 后面就是8个卡片了

def top_students_view(request):
    """学霸榜视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')  # 未登录则跳转到登录页面
    # 从数据库获取所有学生，按stu_score降序排序
    students = StudentInfo.objects.all().order_by('-stu_score')
    return render(request, 'top_students.html', {'students': students})

def study_locations_view(request):
    if 'username' not in request.session:
        return redirect('/polls/login/')
    return render(request, 'study_locations.html')

def learning_style_view(request):
    """学习风格测评视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')
    return render(request, 'learning_style.html')

def course_share_view(request):
    """网课分享视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')  # 未登录则跳转到登录页面
    ### 插入代码
    lessons = Lesson.objects.all().order_by('les_id')
    return render(request, 'course_share.html', {'lessons': lessons})

def study_partner_view(request):
    """学习搭子dd视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')
    return render(request, 'study_partner.html')

def whisper_view(request):
    """悄悄话视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')
    return render(request, 'whisper.html')

def get_card_view(request):
    """公聊区视图"""
    if 'username' not in request.session:
        return redirect('/polls/login/')
    return render(request, 'get_card.html')

def friends_zone_view(request):
    """好友区视图（不使用Q对象）"""
    if 'username' not in request.session:
        return redirect('/polls/login/')
    
    # 获取当前用户stu_id
    current_username = request.session['username']
    current_user = StudentInfo.objects.get(stu_name=current_username)
    
    # 查询两个方向的好友关系
    # 1. 当前用户作为love_a时的好友
    friends_as_a = Love.objects.filter(love_a=current_user.stu_id)
    # 2. 当前用户作为love_b时的好友
    friends_as_b = Love.objects.filter(love_b=current_user.stu_id)
    
    # 提取所有好友ID（双向合并）
    friend_ids = []
    for relation in friends_as_a:
        friend_ids.append(relation.love_b)
    for relation in friends_as_b:
        friend_ids.append(relation.love_a)
    
    # 去重并获取好友学生对象
    unique_friend_ids = set(friend_ids)
    students = StudentInfo.objects.filter(
        stu_id__in=unique_friend_ids
    ).order_by('-stu_score')
    
    return render(request, 'friends_zone.html', {'students': students})
def public_chat(request):
    """加载公共聊天室页面"""
    # 从数据库获取所有聊天记录按时间排序
    all_chats = Chat.objects.all().order_by('chat_time')
    return render(request, 'public_chat.html', {
        'all_chats': all_chats
    })

def send_chat_message(request):
    """处理消息发送请求"""
    if request.method == 'POST':
        HttpResponse(1)
        message = request.POST.get('message', '').strip()
        if not message:
            return redirect('public_chat')
        
        # 生成唯一ID (20位)
        chat_id = str(uuid.uuid4())[:20]
        
        # 获取当前时间（格式：YYYY-MM-DD HH:MM:SS）
        chat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建新记录
        new_chat = Chat(
            chat_id=chat_id,
            chat_time=chat_time,
            chat_name=request.user.username,
            chat_str=message[:300]  # 确保不超过字段限制
        )
        new_chat.save()
        
        return redirect('public_chat')
    
    return redirect('public_chat')

def update_position(request):
    if request.method == 'POST':
        area = request.POST.get('stu_area')
        StudentInfo.objects.filter(
            stu_name=request.session['username']
        ).update(stu_area=area)
    
    return redirect('home')  # 替换为实际URL名称

def save_learning_style(request):
    if request.method == 'POST':
        style = request.POST.get('stu_style')
        StudentInfo.objects.filter(
            stu_name=request.session['username']
        ).update(stu_style=style)
    
    return redirect('home')  # 替换为实际URL名称

def study_partner_view(request):
    lzp=request.session['username']
    lzp_set = StudentInfo.objects.filter(stu_name=lzp)
    user_a=lzp_set[0]
    other_users = StudentInfo.objects.exclude(stu_name=lzp)
    user_b = random.choice(other_users)
    print(user_a.stu_name)
    
    # 计算匹配度
    # 1. 学习风格匹配度（20个特征中相同位置的数量）
    print(user_a.stu_style)
    style_match_count = sum(1 for i in range(20) if user_a.stu_style[i] == user_b.stu_style[i])
    style_match_rate = style_match_count / 20.0
    
    # 2. 学习地点匹配度
    location_diff = fabs((float)(user_a.stu_area) - (float)(user_b.stu_area))
    location_match_rate = (1310.0 - location_diff) / 1310.0
    
    # 3. MBTI匹配度
    mbti_match_count = sum(1 for i in range(4) if user_a.stu_mbti[i] == user_b.stu_mbti[i])
    mbti_match_rate = mbti_match_count / 4.0
    
    # 总匹配度
    total_match_rate = (style_match_rate + location_match_rate + mbti_match_rate) / 3.0
    
    # 格式化匹配度为百分比
    style_match_percent = "{:.2%}".format(style_match_rate)
    location_match_percent = "{:.2%}".format(location_match_rate)
    mbti_match_percent = "{:.2%}".format(mbti_match_rate)
    total_match_percent = "{:.2%}".format(total_match_rate)

    context = {
        'user_id': user_a.stu_id,
        'partner': user_b,
        'style_match': style_match_percent,
        'style_match_count': style_match_count,
        'location_match': location_match_percent,
        'location_diff': location_diff,
        'mbti_match': mbti_match_percent,
        'mbti_match_count': mbti_match_count,
        'total_match': total_match_percent,
        'no_partner': False,
    }
    
    return render(request, 'study_partner.html', context)

@csrf_exempt  # 简化示例，生产环境应使用csrf保护
def add_friend_view(request):
    if request.method == 'POST':
        try:
            # 解析请求数据
            data = json.loads(request.body)
            current_id = data['current_id']
            partner_id = data['partner_id']
            
            # 生成随机love_id (20位)
            love_id = uuid.uuid4().hex[:20]
            
            # 创建Love记录
            Love.objects.create(
                love_id=love_id,
                love_a=current_id,
                love_b=partner_id
            )

            love_id = uuid.uuid4().hex[:20]

            Love.objects.create(
                love_id=love_id,
                love_a=partner_id,
                love_b=current_id
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'好友添加成功！好友id：{partner_id}'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'数据库错误: {str(e)}'
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'}, status=400)

def handle_gamble(request):
    if request.method == 'POST':
        try:
            username = request.session.get('username')
            if Card.objects.filter(card_name=username, card_date=date.today()).count()>=3:
                messages.error(request, '今天已经玩过了，请明天再来！')
                return redirect('get_card')
            card_id = uuid.uuid4().hex[:20]
            Card.objects.create(
                card_id=card_id,
                card_name=username,
                card_date=date.today()
            )
            student = StudentInfo.objects.get(stu_name=username)
            
            risk_level = request.POST.get('risk_level')
            current_score = student.stu_score
            
            # 积分计算逻辑
            operation = random.choice([0, 1])  # 50%概率
            if risk_level == "low":
                change = -1 if operation == 0 else 3
            elif risk_level == "medium":
                change = -5 if operation == 0 else 5
            elif risk_level == "high":
                change = -(current_score // 2) if operation == 0 else 10
            
            # 更新积分
            new_score = max(0, current_score + change)  # 防止负分
            student.stu_score = new_score
            student.save()
            
            # 生成操作结果消息
            risk_names = {"low": "低风险", "medium": "中风险", "high": "高风险"}
            result = "成功" if change >= 0 else "失败"
            messages.success(request, 
                f"{risk_names[risk_level]}操作{result}！积分变化: {'+' if change >=0 else ''}{change} → 新积分: {new_score}")
            
        except Exception as e:
            messages.error(request, f"操作失败: {str(e)}")
    
    return redirect('get_card')

def get_card_view(request):
    me=request.session.get('username')
    student = StudentInfo.objects.get(stu_name=me)
    played_today = Card.objects.filter(card_name=me, card_date=date.today()).count()>=3
    print(played_today)
    return render(request, 'get_card.html', {'current_score': student.stu_score,'played_today': played_today})