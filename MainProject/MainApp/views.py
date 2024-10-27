from django.shortcuts import render

# Create your views here.
def mainPage(request):
    content = {
        "image": "https://images.gr-assets.com/books/1361975680m/2657.jpg"
    }
    return render(request, 'index.html', content)
