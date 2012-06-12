########################################################################################################################
########################################################################################################################
#
#       ActionsGet [get information from database with get request]
#               - check get
#
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

### INTERNAL ###
from BeautifulSoup import BeautifulStoneSoup
from lovegov.alpha.splash.views import ajaxRender
import images
from haystack.query import SearchQuerySet
from lovegov.beta.modernpolitics.models import UserProfile, UserPhysicalAddress, Representative, Senator, DebateMessage, Network
from lovegov.beta.modernpolitics.backend import getUserProfile
from lovegov.alpha.splash.views import renderToResponseCSRF
from lovegov.beta.modernpolitics import backend
from django.db.models import Q
from lovegov.beta.modernpolitics import constants

### DJANGO LIBRARIES ###
from django.http import *
from django.forms import *
from django.utils import simplejson

### OTHER ###
import urllib2
import sunlight
import Image
import PIL
from googlemaps import GoogleMaps
import json


#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all accesses. [checks is accesses]
# post: actionGET - which actionGET to call
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def actionGET(request, dict={}):
    if request.method=='GET' and request.is_ajax and request.user:
        dict['user'] = getUserProfile(request)
        action = request.GET['action']
        if action=='getFeed':
            return getFeed(request)
        elif action=='getQuestion':
            return getQuestion(request)
        elif action=='syncDebate':
            return syncDebate(request)
        elif action=='getLinkInfo':
            return getLinkInfo(request)
        elif action=='getCongressmen':
            return getCongressmen(request,dict)
        elif action=='searchAutoComplete':
            return searchAutoComplete(request,dict)
        elif action=='loadNetworkUsers':
            return loadNetworkUsers(request,dict)
        else:
            dict['message'] = "There is no such action."
            return renderToResponseCSRF('usable/message.html',dict,request)
    else:
        dict['message'] = "This is not a viewable page."
        return renderToResponseCSRF('usable/message.html',dict,request)


#-----------------------------------------------------------------------------------------------------------------------
# Gets content from database, transforms it ino json, and sends it to user
# get: none
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def getFeed(request):
    user = UserProfile.objects.get(id=request.user.id)
    feed = backend.OldFeed(user)
    feed.calculateScores()
    content = feed.getTopicTypeMatches()
    content = completeFields(content)
    return HttpResponse(simplejson.dumps(content))

#-----------------------------------------------------------------------------------------------------------------------
# Gets debate messages from database and returns to user as list of text TODO
# get: debateID - the id of the question to get
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def completeFields(content):
    toReturn = content.downcast()
    toReturn = model_to_dict(toReturn)
    # handle image field later, empty it for now
    toReturn['main_image'] = ''
    toReturn['debate_when'] = ''
    toReturn['topics'] = list(content.topics.all().values_list('topic_text', flat=True))
    return toReturn

#-----------------------------------------------------------------------------------------------------------------------
# Gets question from database and returns to user wrapped in display_question template
# get: q_id - the id of the question to get
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def getQuestion(request):
    question = backend.QUESTIONS.objects.get(id=request.GET['q_id'])
    dict = {'object':question, 'back':request.GET['back']}
    return renderToResponseCSRF('qaweb/display_question.html', dict, request)


#-----------------------------------------------------------------------------------------------------------------------
# Gets debate messages from database and returns to user as list of text
# get: debateID - the id of the question to get
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def syncDebate(request):
    debateID = request.GET['debateID']
    left_messages = list(DebateMessage.objects.filter(room=debateID, debate_side='L', id__gt=request.GET['lastLeftID']).values_list('id','sender__first_name','message',))
    right_messages = list(DebateMessage.objects.filter(room=debateID, debate_side='R', id__gt=request.GET['lastRightID']).values_list('id','sender__first_name','message',))
    toReturn = {'left_messages':left_messages, 'right_messages':right_messages}
    return HttpResponse(simplejson.dumps(toReturn))


#-----------------------------------------------------------------------------------------------------------------------
# Takes URL and retrieves HTML.  Parses HTML and extracts title and description metadata.  Also takes a picture
# snapshot of the website.
# GET: url - the url of the website to extract data from
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
PREFIX_ITERATIONS = ["","http://","http://www."]
def getLinkInfo(request):
    url = str(request.GET['url'])
    url.strip()
    # url may not be well formed so try variations until one works
    for prefix in PREFIX_ITERATIONS:
        try:
            URL = prefix + url
            html = urllib2.urlopen(URL,data=None).fp.read()
            if html: break
        except ValueError:
            continue
    if html and URL:
        soup = BeautifulStoneSoup(html,selfClosingTags=['img'])
        dict = {}
        try:
            dict['title'] = soup.title.string
        except:
            dict['title'] = "No Title"
        try:
            dict['description'] = soup.findAll(attrs={"name":"description"})[0]['content']
        except:
            dict['description'] = "No Description"
        try:
            image_refs = soup.findAll("img")
            list = []
            first_image = None

            for num in range(0,len(image_refs)):
                try:
                    img_url = image_refs[num]['src']
                    if num == 0:
                        first_image = images.downloadImage(img_url=img_url,url=URL,min_size=1)
                    elif len(list) == 3:
                        break
                    else:
                        toAdd = images.downloadImage(img_url=img_url,url=URL)
                        if toAdd: list.append(toAdd)
                except:
                    continue

            list.sort(key=lambda img:img['size'],reverse=True)

            try:
                for imageobj in list:
                    imageobj['path'] = images.resizeImage(imageobj['path'])
            except:
                pass

            if len(list) == 0 and (first_image is not None or first_image is not False):
                first_image['path'] = images.resizeImage(first_image['path'])
                list.append(first_image)

            if len(list) == 0:
                list.append({'path':"/static/images/top-logo-default.png"})

            dict['imglink'] = list
            html = ajaxRender('deployment/snippets/news-autogen.html', dict, request)
            return HttpResponse(json.dumps({'html':html,'imglink':list}))

        except:
            return HttpResponse(json.dumps({'html':"exception",'imglink':[{'path':"/static/images/top-logo-default.png"}]}))

#-----------------------------------------------------------------------------------------------------------------------
# Takes address and/or zip code, finds a geolocation from Google Maps, finds congressional district, gets congressmen,
# generates comparisons, and returns HTML back to user
# GET: url - the url of the website to extract data from
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def getCongressmen(request, dict={}):
    # Get variables from GET request and formats data
    user = dict['user']
    address = request.GET['address']
    zip = request.GET['zip']
    if zip is None: zip = ""
    if address is None: address= ""

    # Load from database if we have this address or zip code stored already
    if address != "" and zip != "" and UserPhysicalAddress.objects.filter(Q(address_string=address)&Q(zip=zip)).exists():
        address = UserPhysicalAddress.objects.filter(Q(address_string=address)&Q(zip=zip))[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    elif address == "" and zip != "" and UserPhysicalAddress.objects.filter(Q(zip=zip)).exists():
        address = UserPhysicalAddress.objects.filter(zip=zip)[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    elif address != "" and zip == "" and UserPhysicalAddress.objects.filter(Q(address_string=address)).exists():
        address = UserPhysicalAddress.objects.filter(address_string=address)[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    else: # Load from Google Maps and Sunlight if we don't have this address or zip code stored
        if address== "" and zip != "": address=zip
        gmaps = GoogleMaps(constants.GOOGLEMAPS_API_KEY)
        coordinates = gmaps.address_to_latlng(address)
        state_district = sunlight.congress.districts_for_lat_lon(coordinates[0],coordinates[1])
        try:
            address = UserPhysicalAddress(user=user.id,address_string=address,zip=zip,latitude=coordinates[0],longitude=coordinates[1],state=state_district[0]['state'],district=state_district[0]['number'])
            address.save()
        except:
            pass
    user.userAddress = address
    user.save()
    # Get congressmen objects and generate comparisons
    congressmen = []
    for s_d in state_district:
        representative = Representative.objects.get(congresssessions=112,state=s_d['state'],district=s_d['number'])
        representative.json = backend.getUserUserComparison(user,representative).toJSON()
        congressmen.append(representative)
    senators = Senator.objects.filter(congresssessions=112,state=state_district[0]['state'])
    for senator in senators:
        senator.json = backend.getUserUserComparison(user,senator).toJSON()
        congressmen.append(senator)

    # Generate HTML and send back HTML to user via ajax
    dict['userProfile'] = user
    dict['congressmen'] = congressmen
    dict['state'] = state_district[0]['state']
    dict['district'] = state_district[0]['number']
    dict['latitude'] = coordinates[0]
    dict['longitude'] = coordinates[1]
    html = ajaxRender('deployment/snippets/match-compare-div.html', dict, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
#
# Returns json of list of results which match inputted 'term'. For jquery autocomplete.
#
#-----------------------------------------------------------------------------------------------------------------------
def searchAutoComplete(request,dict={}):
    string = request.GET['string'].lstrip().rstrip()
    userProfiles = SearchQuerySet().models(UserProfile).autocomplete(content_auto=string)
    dict['userProfiles'] = [userProfile.object for userProfile in userProfiles]
    html = ajaxRender('deployment/pieces/autocomplete.html', dict, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
#
# Loads members.
#
#-----------------------------------------------------------------------------------------------------------------------
def loadNetworkUsers(request,dict={}):
    user = dict['user']
    num = int(request.GET['histogram_displayed_num'])
    histogram_topic = request.GET['histogram_topic']
    histogram_block = int(request.GET['histogram_block'])
    network = Network.objects.get(id=request.GET['network_id'])
    print 'topic: ' + histogram_topic
    print 'block: ' + str(histogram_block)
    next_num = num + 1
    all_members = network.getMembers(user, block=histogram_block, topic=histogram_topic)
    if len(all_members) >= next_num:
        more_members = all_members[num:next_num]
    else:
        more_members = []
    html = ""
    dict['defaultImage'] = backend.getDefaultImage().image
    for member in more_members:
        dict['member'] = member
        html += ajaxRender('deployment/snippets/network-member.div.html',dict,request)
    return HttpResponse(json.dumps({'html':html,'num':next_num}))






