from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import playlist_user
from django.urls.base import reverse
from django.contrib.auth import authenticate,login,logout
from youtube_search import YoutubeSearch
import json
# import cardupdate
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken


def user_login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            if username:
                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    user_details = {
                        'username': username,
                        'id': user.id,
                        'email': user.email,
                    }
                    # Redirect to the default page after successful login
                    return redirect('default')
                else:
                    return render(request, 'login.html', {'detail': 'Invalid credentials'})
            return render(request, 'login.html')
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, 'login.html', {'detail': 'An error occurred'})
      
def user_logout(request):
    try:
        logout(request)  # Call the Django logout function
        return redirect('login')
    except Exception as e:
        return render(request, 'login.html', {'detail': 'An error occurred during logout'})
    
def signup(request):
    if request.method == 'POST':  # Check if the request method is POST
      username = request.POST.get('username')
      email = request.POST.get('email')
      password = request.POST.get('password')
      
      if User.objects.filter(username=username).exists():
          # If username already exists, render the signup page with a message
          return render(request, 'signup.html', {'username_exists': True})
      
      if username and email and password:  # Check if all required fields are provided
        user = User.objects.create_user(
          username=username,
          email=email,
          password=password
        )
        if user is not None:
          login(request, user)
          refresh = RefreshToken.for_user(user)
          return redirect('default')
    
    # If the request method is not POST or if required fields are missing, render the signup form
    return render(request, 'signup.html')


f = open('card.json', 'r')
CONTAINER = json.load(f)

def default(request):
    global CONTAINER


    if request.method == 'POST':

        add_playlist(request)
        return HttpResponse("")

    song = 'kSFJGEHDCrQ'
    return render(request, 'player.html',{'CONTAINER':CONTAINER, 'song':song})



def playlist(request):
    cur_user = playlist_user.objects.get(username = request.user)
    try:
      song = request.GET.get('song')
      song = cur_user.playlist_song_set.get(song_title=song)
      song.delete()
    except:
      pass
    if request.method == 'POST':
        add_playlist(request)
        return HttpResponse("")
    song = 'kSFJGEHDCrQ'
    user_playlist = cur_user.playlist_song_set.all()
    # print(list(playlist_row)[0].song_title)
    return render(request, 'playlist.html', {'song':song,'user_playlist':user_playlist})


def search(request):
  if request.method == 'POST':

    add_playlist(request)
    return HttpResponse("")
  try:
    search = request.GET.get('search')
    song = YoutubeSearch(search, max_results=10).to_dict()
    song_li = [song[:10:2],song[1:10:2]]
    # print(song_li)
  except:
    return redirect('/')

  return render(request, 'search.html', {'CONTAINER': song_li, 'song':song_li[0][0]['id']})




def add_playlist(request):
    cur_user = playlist_user.objects.get(username = request.user)

    if (request.POST['title'],) not in cur_user.playlist_song_set.values_list('song_title', ):

        songdic = (YoutubeSearch(request.POST['title'], max_results=1).to_dict())[0]
        song__albumsrc=songdic['thumbnails'][0]
        cur_user.playlist_song_set.create(song_title=request.POST['title'],song_dur=request.POST['duration'],
        song_albumsrc = song__albumsrc,
        song_channel=request.POST['channel'], song_date_added=request.POST['date'],song_youtube_id=request.POST['songid'])
