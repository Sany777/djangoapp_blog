const textarea = document.getElementById('auto-resize');

textarea.addEventListener('scroll', () => {
    textarea.style.height = textarea.scrollHeight+40 + 'px'; 
});

(()=>{
    if( !document.getElementById('edit-flag')){
        textarea.disabled = true;
    }
})()

