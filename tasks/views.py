from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Project, Task, Comment, Notification


# ==========================================
# HOME / DASHBOARD
# ==========================================

@login_required
def home(request):

    projects = Project.objects.filter(
        Q(created_by=request.user) |
        Q(members=request.user)
    ).distinct()

    tasks = Task.objects.filter(
        Q(created_by=request.user) |
        Q(assigned_to=request.user) |
        Q(project__members=request.user)
    ).distinct()

    # Dashboard statistics
    total_projects = projects.count()
    total_tasks = tasks.count()

    in_progress = tasks.filter(
        status='progress'
    ).count()

    completed = tasks.filter(
        status='done'
    ).count()

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Send everything to home.html
    context = {
        'projects': projects,
        'tasks': tasks,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'completed': completed,
        'notifications': notifications,
    }

    return render(
        request,
        'tasks/home.html',
        context
    ) 

# ==========================================
# REGISTER
# ==========================================

def register(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password:
            messages.error(
                request,
                'Please fill all fields.'
            )
            return redirect('register')

        if password != confirm_password:
            messages.error(
                request,
                'Passwords do not match.'
            )
            return redirect('register')

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )
            return redirect('register')

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email already exists.'
            )
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            'Registration successful!'
        )

        return redirect('home')

    return render(
        request,
        'tasks/register.html'
    )


# ==========================================
# LOGIN
# ==========================================

def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'tasks/login.html'
    )


# ==========================================
# LOGOUT
# ==========================================

def user_logout(request):

    logout(request)

    return redirect('login')


# ==========================================
# PROFILE
# ==========================================

@login_required
def profile(request):

    return render(
        request,
        'tasks/profile.html'
    )


# ==========================================
# CREATE PROJECT
# ==========================================

@login_required
def create_project(request):

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        if not name:

            messages.error(
                request,
                'Project name is required.'
            )

            return redirect('create_project')

        project = Project.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )

        project.members.add(
            request.user
        )

        messages.success(
            request,
            'Project created successfully!'
        )

        return redirect(
            'project_detail',
            project_id=project.id
        )

    return render(
        request,
        'tasks/create_project.html'
    )


# ==========================================
# PROJECT DETAIL / BOARD
# ==========================================

@login_required
def project_detail(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id
    )

    if (
        project.created_by != request.user
        and not project.members.filter(
            id=request.user.id
        ).exists()
    ):

        messages.error(
            request,
            'You do not have access to this project.'
        )

        return redirect('home')

    tasks = project.tasks.all().order_by(
        '-created_at'
    )

    todo_tasks = tasks.filter(
        status='todo'
    )

    progress_tasks = tasks.filter(
        status='progress'
    )

    done_tasks = tasks.filter(
        status='done'
    )

    return render(
        request,
        'tasks/project_detail.html',
        {
            'project': project,
            'todo_tasks': todo_tasks,
            'progress_tasks': progress_tasks,
            'done_tasks': done_tasks,
        }
    )


# ==========================================
# CREATE TASK
# ==========================================

@login_required
def create_task(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id
    )

    # Check project access
    if (
        project.created_by != request.user
        and not project.members.filter(
            id=request.user.id
        ).exists()
    ):
        messages.error(
            request,
            'You do not have access to this project.'
        )

        return redirect('home')

    # ==========================
    # CREATE TASK
    # ==========================

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        assigned_username = request.POST.get(
            'assigned_to',
            ''
        ).strip()

        if not title:

            messages.error(
                request,
                'Task title is required.'
            )

            return redirect(
                'create_task',
                project_id=project.id
            )

        # Find assigned user
        assigned_user = None

        if assigned_username:

            assigned_user = User.objects.filter(
                username=assigned_username
            ).first()

        # Create task
        task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            created_by=request.user,
            assigned_to=assigned_user
        )

        # Notification
        if (
            assigned_user
            and assigned_user != request.user
        ):

            Notification.objects.create(
                user=assigned_user,
                message=f'You were assigned a task: {task.title}'
            )

        messages.success(
            request,
            'Task created successfully!'
        )

        return redirect(
            'project_detail',
            project_id=project.id
        )

    # ==========================
    # SHOW CREATE TASK PAGE
    # ==========================

    users = User.objects.exclude(
        id=request.user.id
    )

    return render(
        request,
        'tasks/create_task.html',
        {
            'project': project,
            'users': users
        }
    )


# ==========================================
# TASK DETAIL
# ==========================================

@login_required
def task_detail(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    project = task.project

    if (
        project.created_by != request.user
        and not project.members.filter(
            id=request.user.id
        ).exists()
    ):

        messages.error(
            request,
            'You do not have access to this task.'
        )

        return redirect('home')

    comments = task.comments.all().order_by(
        'created_at'
    )

    return render(
        request,
        'tasks/task_detail.html',
        {
            'task': task,
            'comments': comments,
        }
    )


# ==========================================
# ADD COMMENT
# ==========================================

@login_required
def add_comment(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    if request.method == 'POST':

        message = request.POST.get(
            'message',
            ''
        ).strip()

        if message:

            Comment.objects.create(
                task=task,
                user=request.user,
                message=message
            )

    return redirect(
        'task_detail',
        task_id=task.id
    )


# ==========================================
# CHANGE TASK STATUS
# ==========================================

@login_required
def change_task_status(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    project = task.project

    if (
        project.created_by != request.user
        and not project.members.filter(
            id=request.user.id
        ).exists()
    ):

        messages.error(
            request,
            'You do not have permission.'
        )

        return redirect('home')

    if request.method == 'POST':

        status = request.POST.get(
            'status'
        )

        valid_statuses = [
            'todo',
            'progress',
            'done'
        ]

        if status in valid_statuses:

            task.status = status
            task.save()

    return redirect(
        'project_detail',
        project_id=project.id
    )


# ==========================================
# NOTIFICATIONS
# ==========================================

@login_required
def notifications(request):

    notification_list = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'tasks/notifications.html',
        {
            'notifications': notification_list
        }
    )


@login_required
def mark_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return redirect('notifications')