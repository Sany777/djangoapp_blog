(function showFirstCardElement()
{
    let firstEl = document.querySelector(".slide")
    if( firstEl ){
        firstEl.classList.add("active");
        document.querySelector(".slider").hidden = false;
    }
})();


function slidePrev()
{
    let activeSlide = document.querySelector('.slide.active');
    let toSlide = activeSlide.previousElementSibling;
    if (!toSlide)
        toSlide = activeSlide.parentElement.lastElementChild;
    activeSlide.classList.remove('active');
    toSlide.classList.add('active');
}

function slideNext()
{
    let activeSlide = document.querySelector('.slide.active');
    let toSlide = activeSlide.nextElementSibling;
    toSlide = activeSlide.nextElementSibling;
    if (!toSlide)
        toSlide = activeSlide.parentElement.firstElementChild;
    activeSlide.classList.remove('active');
    toSlide.classList.add('active');
}


function moveBox(event)
{
    const keyCode = event.keyCode;
    if (keyCode === 37) {
        slidePrev();
    } else if (keyCode === 39) {
        slideNext();
    }
}

document.addEventListener("keydown", moveBox);

document.querySelectorAll('.ratingForm').forEach(function(form) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let form = this;
        const entry_id = form.publication_id.value;
        let formData = new FormData(form);
        let xhr = new XMLHttpRequest();
        xhr.open(form.method, form.action, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onload = function() {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response?.r >= 0) {
                    document.querySelector('.entry_'+entry_id).innerText = "Оцінка: " + response.r;  
                }
            }
        };
        xhr.send(formData);
    } )
})


