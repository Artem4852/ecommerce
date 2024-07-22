function favorite(productId) {
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
                    favoriteIcon.classList.toggle('favorite');
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

function toggleForm(name) {
    const form = document.getElementById('form-' + name);
    form.classList.toggle('disabled');
    const toggle = document.getElementById('toggle-' + name);
    toggle.classList.toggle('disabled');
}


function selectCountry() {
    const country = document.getElementById('input-country').value;
    const cities = deliveryCities[country];
    const city = document.getElementById('input-city');
    city.innerHTML = '';
    let option = new Option('Select city', '', true, true);
    option.setAttribute('disabled', 'disabled');
    city.appendChild(option);
    for (let i = 0; i < cities.length; i++) {
        let option = new Option(cities[i], cities[i]);
        city.appendChild(option);
    }

    const branch = document.getElementById('input-post-office-branch');
    branch.innerHTML = '';
    option = new Option('Select post office branch', '', true, true);
    option.setAttribute('disabled', 'disabled');
    branch.appendChild(option);
}

function selectCity() {
    const city = document.getElementById('input-city').value;
    const branches = postOfficeBranches[city];
    const branch = document.getElementById('input-post-office-branch');
    branch.innerHTML = '';
    let option = new Option('Select post office branch', '', true, true);
    option.setAttribute('disabled', 'disabled');
    branch.appendChild(option);
    for (let i = 0; i < branches.length; i++) {
        let option = new Option(branches[i], branches[i]);
        branch.appendChild(option);
    }
}

function selectDeliveryMethod() {
    const deliveryMethod = document.getElementById('input-delivery-method').value;
    if (deliveryMethod === 'pick-up-from-post-office') {
        document.getElementById('wrapper-input-post-office-branch').classList.remove('disabled');
        document.getElementById('input-address').classList.add('disabled');
        document.getElementById('input-address-2').classList.add('disabled');
        document.getElementById('input-postal-code').classList.add('disabled');
        return;
    }
    document.getElementById('wrapper-input-post-office-branch').classList.add('disabled');
    document.getElementById('input-address').classList.remove('disabled');
    document.getElementById('input-address-2').classList.remove('disabled');
    document.getElementById('input-postal-code').classList.remove('disabled');
}

function selectMessenger() {
    const messenger = document.getElementById('input-contact-messenger').value;
    if (messenger === 'instagram') {
        document.getElementById('input-phone-number').classList.add('disabled');
        document.getElementById('input-username').classList.remove('disabled');
        return;
    }
    document.getElementById('input-phone-number').classList.remove('disabled');
    document.getElementById('input-username').classList.add('disabled');

}

function checkSaveShippingData() {
    document.getElementById('input-check-shipping').classList.toggle('disabled');
}

function checkSavePaymentData() {
    document.getElementById('input-check-payment').classList.toggle('disabled');
}

function checkSaveContactData() {
    document.getElementById('input-check-contact').classList.toggle('disabled');    
}

function validateCheckout() {
    const firstName = document.getElementById('input-first-name').value;
    const lastName = document.getElementById('input-last-name').value;
    const middleName = document.getElementById('input-middle-name').value;
    const country = document.getElementById('input-country').value;
    const city = document.getElementById('input-city').value;
    const deliveryMethod = document.getElementById('input-delivery-method').value;
    const postOfficeBranch = document.getElementById('input-post-office-branch').value;
    const address = document.getElementById('input-address').value;
    const address2 = document.getElementById('input-address-2').value;
    const postalCode = document.getElementById('input-postal-code').value;
    const paymentMethod = document.getElementById('input-payment-method').value;
    const promoCode = document.getElementById('input-promo-code').value;
    const contactMessenger = document.getElementById('input-contact-messenger').value;
    const username = document.getElementById('input-username').value;
    const phoneNumber = document.getElementById('input-phone-number').value;

    if (firstName === '' || lastName === '' || middleName === '' || country === '' || city === '') {
        return('Please fill in all required fields');
    }
    if (deliveryMethod === 'pick-up-from-post-office' && postOfficeBranch === '') {
        return('Please select post office branch');
    }
    if (deliveryMethod === 'deliver-to-address' && (address === '' || postalCode === '')) {
        return('Please fill in all required fields');
    }
    if (paymentMethod === '') {
        return('Please select payment method');
    }
    if (contactMessenger === 'instagram' && username === '') {
        return('Please fill in all required fields');
    }
    if (contactMessenger === 'phone' && phoneNumber === '') {
        return('Please fill in all required fields');
    }
    return '';
}

function checkout() {
    const error = validateCheckout();
    if (error !== '') {
        document.getElementById('button-checkout').innerHTML = error;
        setTimeout(function () {
            document.getElementById('button-checkout').innerHTML = 'Checkout';
        }, 5000);
        return;
    }

    const data = {
        "firstName": document.getElementById('input-first-name').value,
        "lastName": document.getElementById('input-last-name').value,
        "middleName": document.getElementById('input-middle-name').value,
        "country": document.getElementById('input-country').value,
        "city": document.getElementById('input-city').value,
        "deliveryMethod": document.getElementById('input-delivery-method').value
    }
    if (data['deliveryMethod'] == 'pick-up-from-post-office') {
        data['postOfficeBranch'] = document.getElementById('input-post-office-branch').value;
    } else {
        data['address'] = document.getElementById('input-address').value;
        data['address2'] = document.getElementById('input-address-2').value;
        data['postalCode'] = document.getElementById('input-postal-code').value;
    }
    data['saveShippingData'] = !document.getElementById('input-check-shipping').classList.contains('disabled');

    data['paymentMethod'] = document.getElementById('input-payment-method').value;
    data['promoCode'] = document.getElementById('input-promo-code').value;
    data['savePaymentData'] = !document.getElementById('input-check-payment').classList.contains('disabled');

    data['contactMessenger'] = document.getElementById('input-contact-messenger').value;
    if (data['contactMessenger'] == 'instagram') {
        data['username'] = document.getElementById('input-username').value;
    } else {
        data['phoneNumber'] = document.getElementById('input-phone-number').value;
    }
    data['saveContactData'] = !document.getElementById('input-check-contact').classList.contains('disabled');

    fetch('/checkout', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/order-confirmation';
            }
        });
}