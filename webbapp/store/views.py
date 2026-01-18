from django.shortcuts import render
from django.http import HttpResponse
from .forms import PersonForm



# Create your views here.

def hello_World_view(request):
    return HttpResponse("hello world")

def hello_python(request):
    return HttpResponse("<h1><center>Hello Python</center></h1>")

def htmlView(request):
    return render(request, "store/submit.html")

def postExample (request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            age = form.cleaned_data['age']
            email = form.cleaned_data['email']
            
            return HttpResponse(f"Received: Name={name}, Age={age}, Email={email}")
    return HttpResponse("Method not allowed. Please use the form at /submit/")

def submit_django_form(request):
    form = PersonForm()
    return render(request, "store/submit_django_form.html", {"form": form})

def template_view (request):
    context = {
        "name": "Vu",
        "age": 20,
        "skills": ["Python", "Java", "Django"]
    }
    return render(request, "store/template.html", context)