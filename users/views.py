from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout


def register_view(request):	
	if request.method == 'POST':
		form = UserCreationForm(data=request.POST)
		if form.is_valid():
			new_user = form.save()
			login(request, new_user)
			return redirect('blog:welcome')
	else:
		form = UserCreationForm()
		
	return render(request, 'registration/register.html', {
		'form':form
	})


def logout_view(request):
	logout(request)
	return render(request, 'registration/logged_out.html')