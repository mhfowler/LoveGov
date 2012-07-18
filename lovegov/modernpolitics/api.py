from lovegov.modernpolitics.models import *

def handleRequest(request, model, vals={}):
	if model=='petition':
		return HttpResponse("You requested a petition from the LoveGov API.")
	else:
		return HttpResponse("The requested model - \""+model+"\" - is not valid in the LoveGov API.")