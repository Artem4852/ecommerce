document.addEventListener('DOMContentLoaded', () => {
    const imagecols = document.querySelectorAll('.imagecol');
    const imgheight = imagecols[0].children[0].getBoundingClientRect().height;
    let scrolling = [];

    for (let i = 0; i < imagecols.length; i++) {
        scrolling.push(-1);
    }

    starts = []

    for (let i = 0; i < imagecols.length; i++) {
        pos = Math.random() * 2*imgheight - imgheight;
        starts.push(pos);
        imagecols[i].style.top = pos + 'px';
        // console.log(imagecols[i].style.top);
    }

    setInterval(() => {
        for (let i = 0; i < imagecols.length; i++) {
            const col = imagecols[i];
            const images = col.children;

            // console.log(col.getBoundingClientRect().top);
            if (col.offsetTop <= starts[i]-imgheight) {
                col.appendChild(images[0]);
                col.style.top = parseFloat(col.style.top.replace('px', '')) + imgheight + 'px';
            }

            col.style.top = parseFloat(col.style.top.replace('px', '')) + scrolling[i]*2 + 'px';
        }
    }, 30);
});