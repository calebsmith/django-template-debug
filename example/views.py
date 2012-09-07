from django.shortcuts import render


def view_a(request):
    return render(request, 'a.html', {'a': 3})
