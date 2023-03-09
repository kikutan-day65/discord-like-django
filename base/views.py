from django.shortcuts import render

# Create your views here.

rooms = [
    {'id': 1, 'name': 'Lets learn python!'},
    {'id': 2, 'name': 'Lets learn java!'},
    {'id': 3, 'name': 'Lets learn c!'},
]

def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)

def room(request):
    return render(request, 'base/room.html')