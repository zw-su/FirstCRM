from django.shortcuts import render

# Create your views here.
def studentsIndex(request):

    return render(request,'students/studentsIndex.html')

def score_inquiry(request):
    pass