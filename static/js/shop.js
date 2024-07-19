function favorite(productId) {
    console.log(productId)
    fetch('/favorite/' + productId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const favoriteIcon = document.getElementById('favorite-' + productId);
                console.log(favoriteIcon)
                favoriteIcon.setAttribute('class', data.favorite ? 'favorite-icon favorite' : 'favorite-icon');
            }
        });
}

function addToCart(productId) {
    const size = document.getElementById('size').value;
    const quantity = document.getElementById('quantity-' + size).value;
    fetch('/add-to-cart/' + productId, {
        method: 'POST',
        body: JSON.stringify({size: size, quantity: quantity}),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const cartButton = document.getElementById('cart-button-' + productId);
                cartButton.innerText = "Added to cart!";
                setTimeout(function () {
                    cartButton.innerHTML = "Add to cart";
                }, 2000);
            }
        });
}

function filterShoes(criterion) {
    const criterionValue = document.getElementById(criterion).value;
    console.log(criterionValue);
    const url = new URL(window.location.href);
    if (criterionValue === 'Any') url.searchParams.delete(criterion);
    else url.searchParams.set(criterion, criterionValue);
    url.searchParams.delete('scroll');
    url.searchParams.delete('page');
    window.location.href = url.toString();
}

function loadMore() {
    const url = new URL(window.location.href);

    url.searchParams.set('scroll', window.scrollY);
    history.replaceState(null, '', url.toString());

    let page_size = url.searchParams.get('products-per-page');
    if (page_size == null) {
        page_size = 12;
    }
    page_size = parseInt(page_size) + 12;
    url.searchParams.set('products-per-page', page_size);
    window.location.href = url.toString();
}

window.addEventListener('load', function () {
    const url = new URL(window.location.href);
    const scrollPosition = url.searchParams.get('scroll');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        localStorage.removeItem('scrollPosition');
    }
});

function imgBack() {
    images = Array.from(document.getElementById('others').children);
    images.sort((a, b) => parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index')))

    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').removeChild(images[i])
    }
    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').appendChild(images[i])
    }

    selected = 0
    for (let i = 0; i < images.length; i++) {
        if (images[i].classList.contains('selected')) {
            selected = i
            break
        }
    }
    let idx = (selected - 1 + images.length) % images.length

    images[idx].classList.add('selected')
    src = images[idx].src
    images[selected].classList.remove('selected')

    document.getElementById('main-img').src = src

    after = (idx + 1) % images.length
    after_2 = (idx + 2) % images.length
    after_3 = (idx + 3) % images.length

    for (let i = 0; i < images.length; i++) {
        images[i].classList.add('inactive')
    }
    images[idx].classList.remove('inactive')
    images[after].classList.remove('inactive')
    images[after_2].classList.remove('inactive')
    images[after_3].classList.remove('inactive')

    let images_new = [idx, after, after_2, after_3]

    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').removeChild(images[images_new[i]])
    }
    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').appendChild(images[images_new[i]])
    }
}

function imgForward() {
    images = Array.from(document.getElementById('others').children);
    images.sort((a, b) => parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index')))

    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').removeChild(images[i])
    }
    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').appendChild(images[i])
    }

    selected = 0
    for (let i = 0; i < images.length; i++) {
        if (images[i].classList.contains('selected')) {
            selected = i
            break
        }
    }
    let idx = (selected + 1) % images.length

    images[idx].classList.add('selected')
    src = images[idx].src
    images[selected].classList.remove('selected')

    document.getElementById('main-img').src = src

    after = (idx + 1) % images.length
    after_2 = (idx + 2) % images.length
    after_3 = (idx + 3) % images.length

    for (let i = 0; i < images.length; i++) {
        images[i].classList.add('inactive')
    }
    images[idx].classList.remove('inactive')
    images[after].classList.remove('inactive')
    images[after_2].classList.remove('inactive')
    images[after_3].classList.remove('inactive')

    let images_new = [idx, after, after_2, after_3]

    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').removeChild(images[images_new[i]])
    }
    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').appendChild(images[images_new[i]])
    }
}

function setSelected(imageIdx) {
    images = Array.from(document.getElementById('others').children);
    images.sort((a, b) => parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index')))

    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').removeChild(images[i])
    }
    for (let i = 0; i < images.length; i++) {
        document.getElementById('others').appendChild(images[i])
    }

    selected = 0
    for (let i = 0; i < images.length; i++) {
        if (images[i].classList.contains('selected')) {
            selected = i
            break
        }
    }
    let idx = imageIdx

    images[idx].classList.add('selected')
    src = images[idx].src
    images[selected].classList.remove('selected')

    document.getElementById('main-img').src = src

    after = (idx + 1) % images.length
    after_2 = (idx + 2) % images.length
    after_3 = (idx + 3) % images.length

    for (let i = 0; i < images.length; i++) {
        images[i].classList.add('inactive')
    }
    images[idx].classList.remove('inactive')
    images[after].classList.remove('inactive')
    images[after_2].classList.remove('inactive')
    images[after_3].classList.remove('inactive')

    let images_new = [idx, after, after_2, after_3]

    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').removeChild(images[images_new[i]])
    }
    for (let i = 0; i < images_new.length; i++) {
        document.getElementById('others').appendChild(images[images_new[i]])
    }
}

function selectSize() {
    const size = document.getElementById('size').value;
    const quantity_selects = document.getElementsByClassName('quantity');
    for (let i = 0; i < quantity_selects.length; i++) {
        quantity_selects[i].style.display = 'none';
        quantity_selects[i].setAttribute('disabled', 'disabled');
    }
    const quantity_select = document.getElementById('quantity-' + size);
    quantity_select.style.display = 'block';
    quantity_select.removeAttribute('disabled');
    console.log(quantity_selects, quantity_select);
}

function toggleFaq(name) {
    const faq = document.getElementById('faq-'+name);
    faq.classList.toggle('active');
}