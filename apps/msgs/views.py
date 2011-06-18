from django.http import Http404, HttpResponseRedirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from msgs.models import Message

import jingo


def login_user(request):
    '''
    Login user and store username in logged_user session variable.
    After authentication redirect logged_user to their homepage.    
    '''
    msg = []
    if request.method == 'POST':
        username = request.POST['u']
        password = request.POST['p']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['logged_user'] = username
                homepage = "/user/" + username
                return HttpResponseRedirect(homepage)
            else:
                msg.append("You have entered a disabled account")
        else:
            msg.append("Invalid login")
    return jingo.render(request, 'msgs/login.html', {'errors': msg})


def logout_user(request):
    '''
    Logs out user and deletes logged_user session variable. 
    '''
    try:
        del request.session['logged_user']
    except KeyError:
        pass
    logout(request)
    return jingo.render(request, 'msgs/logout.html')


def user_page(request, username):
    ''' 
    Gets user name from logged_user session variable. 
    Retrieve username messages from database.
    Pass in database results to user_page.html template.
    '''
    try:
        logged_user = request.session['logged_user']
        q = (Message.objects.filter(to_user__username=username)
            .order_by("-date"))
    except:
        raise Http404('Requested user page not found.')

    return jingo.render(request, 'msgs/user_page.html',
                                 {'username': username,
                                 'logged_user': logged_user,
                                 'q': q})


def send_message(request):
    '''
    Sends message to a User with a valid username.
    Retrieves User objects from database and creates
    a Message object in the database. Afterwards, display
    message on commented page.
    '''
    if request.method == 'POST':
        to = request.POST['usr']
        frm = request.session['logged_user']
        to_who = User.objects.get(username__exact=to)
        frm_who = User.objects.get(username__exact=frm)
        msg = request.POST['message']

        entry = Message(to_user=to_who, from_user=frm_who, msg=msg)
        entry.save()
        userpage = "/user/" + to
        return HttpResponseRedirect(userpage)
    else:
        raise Http404('Requested POST method send_message() not found')
