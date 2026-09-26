from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================
    # AUTHENTICATION
    # =========================

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    path(
        'profile/',
        views.profile,
        name='profile'
    ),


    # =========================
    # PROJECTS
    # =========================

    path(
        'project/create/',
        views.create_project,
        name='create_project'
    ),

    path(
        'project/<int:project_id>/',
        views.project_detail,
        name='project_detail'
    ),


    # =========================
    # TASKS
    # =========================

    path(
        'project/<int:project_id>/task/create/',
        views.create_task,
        name='create_task'
    ),

    path(
        'task/<int:task_id>/',
        views.task_detail,
        name='task_detail'
    ),

    path(
        'task/<int:task_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),

    path(
        'task/<int:task_id>/status/',
        views.change_task_status,
        name='change_task_status'
    ),


    # =========================
    # NOTIFICATIONS
    # =========================

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),

    path(
        'notifications/read/',
        views.mark_notifications_read,
        name='mark_notifications_read'
    ),

]