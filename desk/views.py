from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from desk.models import session, session_object
import datetime
from django.utils.dateparse import parse_datetime
from django.core.cache import cache
from django.template import RequestContext
from django.contrib.auth.models import User
import authenticate_pb2
import time
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
    # add session in the database, parse datetime
    s = session(author=webRequest.user, title = objectRequest.title, pub_date = parse_datetime(str(objectRequest.timeStart)))
    s.save()
    # send back a proto object 
    protoSession = session_pb2.Session()
    protoSession.id = s.id
    return HttpResponse(protoSession.SerializeToString(), content_type="application/octet-stream")

@login_required
def update_session(webRequest):
    webRequestbody = str(webRequest.body)
    objectRequest = session_pb2.Session.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.id)
    # Update Details
    userObject = User.objects.get(id=webRequest.user.id)
    if (objectSession.author == webRequest.user):
        objectSession.title = objectRequest.title
        objectSession.end_date = parse_datetime(objectRequest.timeEnd)
        objectSession.save()
    # Send a Proto of the new session filled with objsectSession details
    protoSession = session_pb2.Session()
    protoSession.id = objectSession.id
    return HttpResponse(protoSession.SerializeToString(), content_type="appplication/octet-stream")

@login_required
def join_session(webRequest):   
    # get requested object from DB
    webRequestbody = str(webRequest.body)
    objectRequest = session_pb2.Session.FromString(webRequestbody)
    objectSession = session.objects.get(id=objectRequest.id)
    # construct proto object from session DB object to send back
    protoSession = session_pb2.Session()
    protoSession.id = objectSession.id
    protoSession.username = objectSession.author.username
    protoSession.timeStart = str(objectSession.pub_date)
    protoSession.title = objectSession.title
    protoSession.timeEnd = str(objectSession.end_date)
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
    s = session_object(session=objectSession, date_added = parse_datetime(str(objectRequest.insertTime)), data_type = objectRequest.type, binary_data = objectRequest.data, author=webRequest.user)
    s.save()
    response = session_pb2.SessionResponse()
    response.error = False
    return HttpResponse(response.SerializeToString(), content_type="application/octet-stream")

@login_required
def get_objects(webRequest, content_type):
    start_time = time.time()
    webBody = str(webRequest.body)
    # lets parse string
    parsedSession = session_pb2.Session.FromString(webBody)
    # grab the object relevant to id in string
    objectSession = session.objects.get(id=parsedSession.id)
    # grab all session_objects from the desired session
    associatedObjects = session_object.objects.all().filter(session=parsedSession.id, data_type=content_type).order_by('date_added')
    # create a return list that we'll populate with each session_object
    returnList = session_pb2.SessionObjectContainer()
    # only return 
    clientNum = cache.get_or_set('object_client_count', int(associatedObjects.count()))
    # check to see that we have new objects to return
    while (associatedObjects.count() == clientNum):
    # return after 60 seconds anyway, just so the request doesn't timeout on client side *** fix this by not timing out client side
        if (int(time.time() - start_time) == 60 ):
            break
        else:
            associatedObjects = session_object.objects.all().filter(session=parsedSession.id, data_type=content_type).order_by('date_added')
    print(associatedObjects.count())
    print(clientNum)
    for eachObject in associatedObjects:
    # loop through each object in the filtered objects we have and populate with objects 
        if (parsedSession.timeEnd == "NO" or (parse_datetime(parsedSession.timeEnd)  < eachObject.date_added)):
            protoObject = returnList.sessionContainer.add()
            # protoObject.session = eachObject.id
            protoObject.type = eachObject.data_type
            protoObject.insertTime = str(eachObject.date_added)
            protoObject.data = eachObject.binary_data
            userObject = User.objects.get(id=eachObject.author.id)
            protoObject.user = str(userObject.username)
    
    cache.set('object_client_count', int(associatedObjects.count()))
    return HttpResponse(returnList.SerializeToString(), content_type="application/octet-stream")

