from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Find My Gig home page")
