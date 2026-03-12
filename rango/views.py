from django.shortcuts import render, redirect
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth import login

from rango.forms import UserSignUpForm, MusicianProfileForm, BandProfileForm

def home(request):
    return HttpResponse("Find My Gig home page")

@transaction.atomic
def musician_signup(request):
    if request.user.is_authenticated:
        return redirect('rango:home')
    
    if request.method == "Post":
        user_form = UserSignUpForm(request.POST)
        profile_form = MusicianProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            musician = profile_form.save(commit=False)
            musician.user = user
            musician.save()

            login(request, user)
            return redirect('rango:home')
        
    else:
        user_form = UserSignUpForm()
        profile_form = MusicianProfileForm()
    
    return render(request, 'rango/signup_musician.html', {'user_form': user_form, 'profile_form': profile_form})

@transaction.atomic
def band_signup(request):
    if request.user.is_authentication:
        return redirect('rango:home')
    
    if request.POST == 'POST':
        user_form = UserSignUpForm(request.POST)
        profile_form = BandProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            band = profile_form.save(commit=False)
            band.user = user
            band.save()

            login(request, user)
            return redirect('rango:home')
    
    else: 
        user_form = UserSignUpForm()
        profile_form = BandProfileForm()
    
    return render(request, 'rango/signup_band.html', {'user_form':user_form, 'profile_form': profile_form})
