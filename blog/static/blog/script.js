(()=>{
    let firstEl = document.querySelector(".slide")
    if( firstEl ){
        firstEl.classList.add("active");
        document.querySelector(".slider").hidden = false;
    }
})();

const textarea = document.getElementById('auto-resize');

textarea.addEventListener('scroll', () => {
    textarea.style.height = textarea.scrollHeight + 'px'; 
});

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
