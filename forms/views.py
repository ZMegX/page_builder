from django.shortcuts import render


def home(request):
    return render(request, "forms/home.html", {})
