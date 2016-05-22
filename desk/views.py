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
    # take the webrequest and take title and pub date create new database
    webRequestbody = str(webRequest.body)
    objectRequest = session_pb2.Session.FromString(webRequestbody)
    s = session(author=webRequest.user, title = objectRequest.title, pub_date = datetime.datetime.now())
    s.save()
    # send back a proto object 
    protoSession = session_pb2.Session()
    protoSession.id = s.id
    return HttpResponse(protoSession.SerializeToString(), content_type="application/octet-stream")

@login_required
def update_session(webRequest):
    webRequestbody = str(webRequest.body)
    objectRequest = session_pb2.SessionObject.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.session.id)
    # Update Details
    objectSession.author = webRequestbody.username
    objectSession.title = webRequestbody.title
    objectSession.pub_date = timeStart
    objectSession.end_date = timeEnd
    objectSession.save()
    # Send a Proto of the new session filled with objsectSession details
    protoSession = session_pb2.Session()
    protoSession.id = objectSession.id
    protoSession.timeStart = objectSession.pub_date
    protoSession.title = objectSession.title
    protoSession.timeEnd = objectSession.end_date
    return HttpResponse(protoSession.SerializeToString(), content_type="appplication/octet-stream")

@login_required
def join_session(webRequest):   
    # get requested object from DB
    webRequestbody = str(webRequest.body)
    ojectRequest = session_pb2.SessionObject.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.session.id)
    # construct proto object from session DB object to send back
    protoSession = session_pb2.Session()
    protoSession.id = objectSession.id
    protoSession.username = objectSession.author
    protoSession.timeStart = objectSession.pub_date
    protoSession.title = objectSession.title
    protoSession.timeEnd = objectSession.end_date
    return HttpResponse(protoSession.SerializeToString(), content_type="application/octet-stream")
    
@login_required   
def get_list(webRequest):
    # grab all session objeccts from DB
    sessionList = session.objects.all()
    protoSessionList = session_pb2.SessionList()
    # for each session in the session list construct proto objects in a proto list to send back
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
    s = session_object(session=objectSession, date_added = datetime.datetime.now(), data_type = objectRequest.type, binary_data = objectRequest.data)
    s.save()
    response = session_pb2.SessionResponse()
    response.error = False
    return HttpResponse(response.SerializeToString(), content_type="application/octet-stream")

@login_required
def get_objects(webRequest):
    webRequestBody = str(webRequest.body)
    # lets parse string
    parsedSession = session_pb2.Session.FromString(webRequestbody)
    # grab the object relevant to id in string
    objectSession = session.objects.get(id=parsedSession.id)
    # grab all session_objects from the desired session
    associatedObjects = session_object.objects.all().filter(session=parsedSession.id)
    # create a return list that we'll populate with each session_object
    returnList = session_pb2.SessionObjectContainer;
    # if the session has an end date or if we haven't gotten any data from here before then return every object
    if not (objectSession.end_date) or parsedSession.timeEnd == "NO":
        for eachObject in associatedObjects:
            protoObject = returnList.object.add()
            protoObject.session = eachObject.id
            protoObject.type = eachObject.data_type
            protoObject.insertTime = str(eachObject.date_added)
            protoObject.data = eachObject.binary_data
    else:
    # else its a live session
        for eachObject in associatedObjects:
        # loop through each object in the filtered objects we have and populate with objects 
            if (parsedSession.timeEnd() < eachObject.date_added):
                protoObject = returnList.object.add()
                protoObject.session = eachObject.id
                protoObject.type = eachObject.data_type
                protoObject.insertTime = str(eachObject.date_added)
                protoObject.data = eachObject.binary_data

    return HttpResponse(returnList.SerializeToString(), content_type="application/octet-stream")
