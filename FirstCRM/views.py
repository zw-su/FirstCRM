from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

def acc_login(request):
    error_msg=''
    if request.method == 'POST':
        username =request.POST.get('username')
        password = request.POST.get('password')
        print(username,password)
        user =authenticate(username=username,password=password)
        if user:
            login(request,user)
            # return redirect('/crm/')

            return redirect(request.GET.get('next','/crm'))
        else :
            error_msg='user or password Error'

        print(user)
    return render(request,'login.html',{'error':error_msg})

def acc_logout(request):
    logout(request)
    return redirect('/login/')