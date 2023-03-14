from django.shortcuts import render, redirect
from django.contrib import messages # used for error messages
from django.db.models import Q # used for search function
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Room, Topic
from .forms import RoomForm

# Create your views here.

def login_page(request):

    if request.method == 'POST':

        # get username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # check if the user exists
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, username=username, password=password)

        # then login and redirect to home, otherwise error message
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')

    context = {}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''


    rooms = Room.objects.all().filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room  = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)

def create_room(request):
    form = RoomForm()

    # check if the method is POST
    if request.method == 'POST':

        # get and save data in the form variable
        form = RoomForm(request.POST)

        # if form is valid, then save it and redirect to the home
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # pre-filled room info when editing it

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})