const element = document.getElementById('swipeObject');

document.addEventListener('mousemove', (event) => {
    console.log(element)
    // Set the position of the swipeObject to follow the mouse
    element.style.left = event.pageX + 'px';
    element.style.top = event.pageY + 'px';
});