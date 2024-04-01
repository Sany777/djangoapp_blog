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



function moveBox(event){
    const keyCode = event.keyCode;
    if (keyCode === 37) {
        slidePrev();
    } else if (keyCode === 39) {
        slideNext();
    }
}

document.addEventListener("keydown", moveBox);




// var modal = document.getElementById("myModal");
// var closeBtn = document.getElementsByClassName("close")[0];

// modal.style.display = "block";

// closeBtn.onclick = function() {
//   modal.style.display = "none";
// }

// window.onclick = function(event) {
//   if (event.target == modal) {
//     modal.style.display = "none";
//   }
// }