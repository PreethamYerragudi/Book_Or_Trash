from django.shortcuts import render

# Create your views here.
def mainPage(request):
    content = {
        "image": "https://images.gr-assets.com/books/1361975680m/2657.jpg"
    }
    return render(request, 'index.html', content)

def update_counter(request):
    global is_left_side
    if request.method == 'POST':
        is_left_side = request.POST.get('isLeftSide') == 'true'
    print(is_left_side)
    return render(request, "book.html")
