from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from desk.models import session, session_object
import datetime
import authenticate_pb2
import session_pb2

def login_view(webRequest):
    # lets parse the request from gproto data from the web request into 
    authRequest = authenticate_pb2.Request.FromString(webRequest.body)
    username = authRequest.username
    password = authRequest.password
    user = authenticate(username=username, password=password)
    response = authenticate_pb2.Response()
    if user is not None:
        if user.is_active:
            login(webRequest, user)
            print('Works')
            response.success = True
            response.errorMessage = ""
            # Redirect to a success page.
        else:
            print ('Disabled')
            response.success = False
            response.errorMessage = "Your Account is Disabled."
            # Return a 'disabled account' error message
    else:
        print ('Invalid Login')
        response.success = False
        response.errorMessage = "Invalid Login Details."
        # Return an 'invalid login' error message.
    return HttpResponse(response.SerializeToString(), content_type="application/octet-stream")

@login_required
def logout_view(request):
    logout(request)
    # Redirect to a success page.

@login_required
def create_session(webRequest):
    s = session(author=webRequest.user, title = "DeskSession", pub_date = datetime.datetime.now())
    s.save()
    protoSession = session_pb2.Session()
    protoSession.id = s.id
    return HttpResponse(protoSession.SerializeToString(), content_type="application/octet-stream")

@login_required
def join_session(webRequest):   
    webRequestbody = str(webRequest.body)
    ojectRequest = session_pb2.SessionObject.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.session.id)
    return HttpResponse(protoSession.SerializeToString(), content_type="application/octet-stream")
    
@login_required   
def get_list(webRequest):
    sessionList = session.objects.all()
    protoSessionList = session_pb2.SessionList()
    for eachSession in sessionList:
        protoSession = protoSessionList.sessionList.add()
        protoSession.id = eachSession.id
        protoSession.username = str(eachSession.author.username)
        protoSession.timeStart = str(eachSession.pub_date)
        protoSession.timeEnd = str(eachSession.end_date)
        protoSession.title = eachSession.title
    return HttpResponse(protoSessionList.SerializeToString(), content_type="application/octet-stream")
    
@login_required    
def object_store(webRequest): 
    webRequestbody = str(webRequest.body)
    objectRequest = session_pb2.SessionObject.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.session.id)
    s = session_object(session=objectSession, date_added = objectRequest.insertTime, data_type = objectRequest.type, binary_data = objectRequest.data)
    s.save()
    
    response = session_pb2.SessionResponse()
    response.error = False
    return HttpResponse(response.SerializeToString(), content_type="application/octet-stream")
