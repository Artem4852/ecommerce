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
                url = new URL(window.location.href);
                favoritePage = url.toString().includes('favorites');
                if (favoritePage) {
                    const card = document.getElementById('card-' + productId);
                    card.remove();
                } else {
                    const favoriteIcon = document.getElementById('favorite-' + productId);
                    favoriteIcon.setAttribute('class', data.favorite ? 'favorite-icon favorite' : 'favorite-icon');
                }
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

function removeFromCart(productId, size, quantity) {
    fetch('/remove-from-cart/' + productId, {
        method: 'POST',
        body: JSON.stringify({size: size, quantity: quantity}),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function editCart(productId) {
    const card = document.getElementById('card-' + productId);
    const info_size = card.getElementsByClassName('info-size')[0];
    const info_quantity = card.getElementsByClassName('info-quantity')[0];
    info_size.style.display = 'none';
    info_quantity.style.display = 'none';

    const edit_size = card.getElementsByClassName('edit-size')[0];
    const edit_quantity = card.getElementsByClassName('edit-quantity')[0];
    edit_size.style.display = 'flex';
    edit_quantity.style.display = 'flex';

    const button_left = document.getElementById('button-left-' + productId);
    const button_right = document.getElementById('button-right-' + productId);
    button_left.setAttribute('onclick', 'saveCart("' + productId + '")');
    button_left.innerHTML = 'Save';
    button_right.setAttribute('onclick', 'cancelCart("' + productId + '")');
    button_right.innerHTML = 'Cancel';
}

function saveCart(productId) {
    const card = document.getElementById('card-' + productId);
    const size = card.getElementsByClassName('edit-size')[0].getElementsByClassName('size')[0].value;
    const quantity = card.getElementsByClassName('edit-quantity')[0].getElementsByClassName('quantity-' + size)[0].value;
    console.log(size, quantity)
    fetch('/edit-cart/' + productId, {
        method: 'POST',
        body: JSON.stringify({size: size, quantity: quantity}),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function cancelCart(productId) {
    const card = document.getElementById('card-' + productId);
    const info_size = card.getElementsByClassName('info-size')[0];
    const info_quantity = card.getElementsByClassName('info-quantity')[0];
    info_size.style.display = 'flex';
    info_quantity.style.display = 'flex';

    const edit_size = card.getElementsByClassName('edit-size')[0];
    const edit_quantity = card.getElementsByClassName('edit-quantity')[0];
    edit_size.style.display = 'none';
    edit_quantity.style.display = 'none';

    const button_left = document.getElementById('button-left-' + productId);
    const button_right = document.getElementById('button-right-' + productId);
    button_right.setAttribute('onclick', 'editCart("' + productId + '")');
    button_right.innerHTML = 'Edit';
    button_left.setAttribute('onclick', `removeFromCart("${productId}", "${info_size.innerHTML.replace('Size: ', '')}", "${info_quantity.innerHTML.replace('Quantity: ', '')}")`);
    button_left.innerHTML = 'Remove';
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
    console.log(size)
    const quantity_selects = document.getElementsByClassName('quantity');
    for (let i = 0; i < quantity_selects.length; i++) {
        quantity_selects[i].style.display = 'none';
        quantity_selects[i].setAttribute('disabled', 'disabled');
    }
    const quantity_select = document.getElementById('quantity-' + size);
    console.log(quantity_select)
    quantity_select.style.display = 'block';
    quantity_select.removeAttribute('disabled');
}

function selectSizeCart(productId) {
    const size = document.getElementById('size-'+productId).value;
    console.log(size)
    const quantity_selects = document.getElementsByClassName('quantity');
    for (let i = 0; i < quantity_selects.length; i++) {
        quantity_selects[i].style.display = 'none';
        quantity_selects[i].setAttribute('disabled', 'disabled');
    }
    const quantity_select = document.getElementById('quantity-' + size + '-' + productId);
    console.log(quantity_select)
    quantity_select.style.display = 'block';
    quantity_select.removeAttribute('disabled');
}

function toggleFaq(name) {
    const faq = document.getElementById('faq-'+name);
    faq.classList.toggle('active');
}