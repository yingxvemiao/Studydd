from django.urls import path

from mydemo import settings
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.toLogin_view),
    path('index/', views.Login_view),
    path('toregister/', views.toregister_view),
    path('register/', views.register_view),
    path('prompt/', views.prompt_view),
    path('prompt2/', views.prompt2_view),
    path('welcome/', views.welcome_view, name='welcome'),
    path('kill/', views.kill_view, name='kill'),
    path('logout_confirm/', views.logout_confirm_view, name='logout_confirm'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('top_students/', views.top_students_view, name='top_students'),
    path('study_locations/', views.study_locations_view, name='study_locations'),
    path('learning_style/', views.learning_style_view, name='learning_style'),
    path('course_share/', views.course_share_view, name='course_share'),
    path('study_partner/', views.study_partner_view, name='study_partner'),
    path('whisper/', views.whisper_view, name='whisper'),
    path('friends_zone/', views.friends_zone_view, name='friends_zone'),
    path('update-position/', views.update_position, name='update_position'),
    path('save_learning_style/', views.save_learning_style, name='save_learning_style'),
    path('add_friend/', views.add_friend_view, name='add_friend'),
    path('get_card/', views.get_card_view, name='get_card'),
    path('handle_gamble/', views.handle_gamble, name='handle_gamble'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)