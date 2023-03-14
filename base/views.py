from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages # used for error messages
from django.contrib.auth.decorators import login_required   # used for restriction of page
from django.db.models import Q # used for search function
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        # get username and password
        username = request.POST.get('username').lower()
        password = request.POST.get('password').lower()

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

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def register_user(request):

    """
        The reason UserCreationForm is used twice is because we need to create an
        instance of the form with no data to display it initially. If the user
        submits the form (i.e., the request method is POST), we need to create
        another instance of the form with the submitted data to process it.

        We convert the username to lowercase to ensure that usernames are
        consistent, regardless of whether they are entered in uppercase or
        lowercase. This helps prevent users from accidentally creating
        multiple accounts with the same username.
    """

    # Create an instance of UserCreationForm with no data
    form = UserCreationForm()

     # If the request method is POST, the user has submitted the form
    if request.method == 'POST':

         # Create an instance of UserCreationForm with the POST data
        form = UserCreationForm(request.POST)

        # If the form data is valid
        if form.is_valid():

            # Create a new user account but don't save it to the database yet
            user = form.save(commit=False)

            # Convert the username to lowercase
            user.username = user.username.lower()

            # Save the user to the database
            user.save()

            # Log the user in
            login(request, user)

            # Redirect the user to the home page
            return redirect('home')
        
        # If the form data is not valid
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})


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
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body'),
        )
        room.participants.add(request.user) # add user as a participant when he send a message
        return redirect('room', pk=room.id)


    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login') # allows only logged-in user to do the fuction below
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

@login_required(login_url='login') # allows only logged-in user to do the fuction below
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # pre-filled room info when editing it

    # only the host can update the room
    if request.method != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login') # allows only logged-in user to do the fuction below
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    # only the host can delete the room
    if request.method != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})