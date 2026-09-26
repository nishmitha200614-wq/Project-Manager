from django.contrib import admin
from .models import Project, Task, Comment, Notification


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'created_by',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'project',
        'created_by',
        'assigned_to',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'project',
    )

    search_fields = (
        'title',
        'description',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        'task',
        'user',
        'created_at',
    )

    search_fields = (
        'message',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'message',
        'is_read',
        'created_at',
    )

    list_filter = (
        'is_read',
    )