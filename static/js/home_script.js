scrolling = []
strength = 1.5
for (let i = 0; i < 8; i++) {
    if (scrolling[i-1] > 0) {
        scrolling.push(-Math.random() * strength);
    } else {
        scrolling.push(Math.random() * strength);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const imagecols = document.querySelectorAll('.imagecol');
    for (let i = 0; i < imagecols.length; i++) {
        pos = Math.random() * 800 - 400;
        imagecols[i].style.top = pos + 'px';
        console.log(imagecols[i].style.top);
    }
});

let prev = window.scrollY;

window.addEventListener('scroll', () => {
    const imagecols = document.querySelectorAll('.imagecol');
    for (let i = 0; i < imagecols.length; i++) {
        pos = parseFloat(imagecols[i].style.top.replace('px', ''));
        pos += scrolling[i] * (window.scrollY - prev);
        imagecols[i].style.top = pos + 'px';

        if (i+1 == imagecols.length) {
            console.log(imagecols[i].style.top);
        }
    }
    prev = window.scrollY;
});