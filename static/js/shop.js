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
                    const card = document.getElementById('card' + productId);
                    card.remove();
                } else {
                    const favoriteIcon = document.getElementById('favorite' + productId);
                    favoriteIcon.classList.toggle('favorite');
                }
            }
        });
}

function addToCart(productId) {
    const size = document.getElementById('size').value;
    const quantity = document.getElementById('quantity' + size).value;
    fetch('/addToCart/' + productId, {
        method: 'POST',
        body: JSON.stringify({size: size, quantity: quantity}),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const cartButton = document.getElementById('cartButton' + productId);
                cartButton.innerText = "Added to cart!";
                setTimeout(function () {
                    cartButton.innerHTML = "Add to cart";
                }, 2000);
            }
        });
}

function removeFromCart(productId, size, quantity) {
    fetch('/removeFromCart/' + productId, {
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
    const card = document.getElementById('card' + productId);
    const infoSize = card.getElementsByClassName('infoSize')[0];
    const infoQuantity = card.getElementsByClassName('infoQuantity')[0];
    infoSize.style.display = 'none';
    infoQuantity.style.display = 'none';

    const editSize = card.getElementsByClassName('editSize')[0];
    const editQuantity = card.getElementsByClassName('editQuantity')[0];
    editSize.style.display = 'flex';
    editQuantity.style.display = 'flex';

    const buttonLeft = document.getElementById('buttonLeft' + productId);
    const buttonRight = document.getElementById('buttonRight' + productId);
    buttonLeft.setAttribute('onclick', 'saveCart("' + productId + '")');
    buttonLeft.innerHTML = 'Save';
    buttonRight.setAttribute('onclick', 'cancelCart("' + productId + '")');
    buttonRight.innerHTML = 'Cancel';
}

function saveCart(productId) {
    const card = document.getElementById('card' + productId);
    const size = card.getElementsByClassName('editSize')[0].getElementsByClassName('size')[0].value;
    const quantity = card.getElementsByClassName('editQuantity')[0].getElementsByClassName('quantity' + size)[0].value;
    console.log(size, quantity)
    fetch('/editCart/' + productId, {
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
    const card = document.getElementById('card' + productId);
    const infoSize = card.getElementsByClassName('infoSize')[0];
    const infoQuantity = card.getElementsByClassName('infoQuantity')[0];
    infoSize.style.display = 'flex';
    infoQuantity.style.display = 'flex';

    const editSize = card.getElementsByClassName('editSize')[0];
    const editQuantity = card.getElementsByClassName('editQuantity')[0];
    editSize.style.display = 'none';
    editQuantity.style.display = 'none';

    const buttonLeft = document.getElementById('buttonLeft' + productId);
    const buttonRight = document.getElementById('buttonRight' + productId);
    buttonRight.setAttribute('onclick', 'editCart("' + productId + '")');
    buttonRight.innerHTML = 'Edit';
    buttonLeft.setAttribute('onclick', `removeFromCart("${productId}", "${infoSize.innerHTML.replace('Size: ', '')}", "${infoQuantity.innerHTML.replace('Quantity: ', '')}")`);
    buttonLeft.innerHTML = 'Remove';
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

    let pageSize = url.searchParams.get('productsPerPage');
    if (pageSize == null) {
        pageSize = 12;
    }
    pageSize = parseInt(pageSize) + 12;
    url.searchParams.set('productsPerPage', pageSize);
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
    images.sort((a, b) => parseInt(a.getAttribute('dataIndex')) - parseInt(b.getAttribute('dataIndex')))

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

    document.getElementById('mainImg').src = src

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

    let imagesNew = [idx, after, after_2, after_3]

    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').removeChild(images[imagesNew[i]])
    }
    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').appendChild(images[imagesNew[i]])
    }
}

function imgForward() {
    images = Array.from(document.getElementById('others').children);
    images.sort((a, b) => parseInt(a.getAttribute('dataIndex')) - parseInt(b.getAttribute('dataIndex')))

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

    document.getElementById('mainImg').src = src

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

    let imagesNew = [idx, after, after_2, after_3]
    if (images.length < 4) imagesNew.pop()
    if (images.length < 3) imagesNew.pop()

    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').removeChild(images[imagesNew[i]])
    }
    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').appendChild(images[imagesNew[i]])
    }
}

function setSelected(imageIdx) {
    images = Array.from(document.getElementById('others').children);
    images.sort((a, b) => parseInt(a.getAttribute('dataIndex')) - parseInt(b.getAttribute('dataIndex')))

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

    document.getElementById('mainImg').src = src

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

    let imagesNew = [idx, after, after_2, after_3]

    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').removeChild(images[imagesNew[i]])
    }
    for (let i = 0; i < imagesNew.length; i++) {
        document.getElementById('others').appendChild(images[imagesNew[i]])
    }
}

function selectSize() {
    const size = document.getElementById('size').value;
    console.log(size)
    const quantitySelects = document.getElementsByClassName('quantity');
    for (let i = 0; i < quantitySelects.length; i++) {
        quantitySelects[i].style.display = 'none';
        quantitySelects[i].setAttribute('disabled', 'disabled');
    }
    const quantitySelect = document.getElementById('quantity' + size);
    console.log(quantitySelect)
    quantitySelect.style.display = 'block';
    quantitySelect.removeAttribute('disabled');
}

function selectSizeCart(productId) {
    const size = document.getElementById('size'+productId).value;
    console.log(size)
    const quantitySelects = document.getElementsByClassName('quantity');
    for (let i = 0; i < quantitySelects.length; i++) {
        quantitySelects[i].style.display = 'none';
        quantitySelects[i].setAttribute('disabled', 'disabled');
    }
    const quantitySelect = document.getElementById('quantity' + size + '' + productId);
    console.log(quantitySelect)
    quantitySelect.style.display = 'block';
    quantitySelect.removeAttribute('disabled');
}

function toggleFaq(name) {
    const faq = document.getElementById('faq'+name);
    faq.classList.toggle('active');
}

function toggleForm(name) {
    const form = document.getElementById('form' + name);
    form.classList.toggle('disabled');
    const toggle = document.getElementById('toggle' + name);
    toggle.classList.toggle('disabled');
}


function selectCountry() {
    const country = document.getElementById('inputCountry').value;
    const cities = deliveryCities[country];
    const city = document.getElementById('inputCity');
    city.innerHTML = '';
    let option = new Option('Select city', '', true, true);
    option.setAttribute('disabled', 'disabled');
    city.appendChild(option);

    let execute = false;
    for (let i = 0; i < cities.length; i++) {
        if (cities[i] === default_city) execute = true;
        let option = new Option(cities[i], cities[i], cities[i] === default_city, cities[i] === default_city);
        city.appendChild(option);
    }
    if (execute) selectCity();

    const branch = document.getElementById('inputPostOfficeBranch');
    branch.innerHTML = '';
    option = new Option('Select post office branch', '', true, true);
    option.setAttribute('disabled', 'disabled');
    branch.appendChild(option);
}

function selectCity() {
    const city = document.getElementById('inputCity').value;
    const countryCode = document.getElementById('inputCountry').value;

    document.getElementById('wrapperInputPostOfficeBranch').classList.remove('disabled');
    document.getElementById('inputPostOfficeBranchNoselect').classList.add('disabled');
    const branch = document.getElementById('inputPostOfficeBranch');
    branch.innerHTML = '';
    let option = new Option('Select post office branch', '', true, true);
    option.setAttribute('disabled', 'disabled');
    branch.appendChild(option);

    fetch('/getBranches', {
        method: 'POST',
        body: JSON.stringify({"city": city, "countryCode": countryCode}),
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (!data.success) {
                console.log(data.success)
                document.getElementById('wrapperInputPostOfficeBranch').classList.remove('disabled');
                document.getElementById('inputPostOfficeBranchNoselect').classList.add('disabled');
                return;
            }

            const branches = data.branches;

            for (let i = 0; i < branches.length; i++) {
                console.log(branches[i]['number']);
                shortName = branches[i]['shortName'];
                if (shortName.includes(" (")) shortName = shortName.substring(0, shortName.indexOf(" ("));
                let option = new Option(shortName, branches[i]['number'], branches[i]['number'] === default_branch, branches[i]['number'] === default_branch);
                option.setAttribute('data-name', shortName);
                branch.appendChild(option);
            }
        });
}

function selectDeliveryMethod() {
    const deliveryMethod = document.getElementById('inputDeliveryMethod').value;
    updateShippingPrice();
    if (deliveryMethod === 'pickUpFromPostOffice') {
        document.getElementById('wrapperInputPostOfficeBranch').classList.remove('disabled');
        document.getElementById('inputAddress').classList.add('disabled');
        document.getElementById('inputAddress-2').classList.add('disabled');
        document.getElementById('inputPostalCode').classList.add('disabled');
        return;
    }
    document.getElementById('wrapperInputPostOfficeBranch').classList.add('disabled');
    document.getElementById('inputAddress').classList.remove('disabled');
    document.getElementById('inputAddress-2').classList.remove('disabled');
    document.getElementById('inputPostalCode').classList.remove('disabled');
}

function selectMessenger() {
    const messenger = document.getElementById('inputContactMessenger').value;
    if (messenger === 'instagram') {
        document.getElementById('inputPhoneNumber').classList.add('disabled');
        document.getElementById('inputUsername').classList.remove('disabled');
        return;
    }
    document.getElementById('inputPhoneNumber').classList.remove('disabled');
    document.getElementById('inputUsername').classList.add('disabled');

}

function checkSaveShippingData() {
    document.getElementById('inputCheckShipping').classList.toggle('disabled');
}

function checkSavePaymentData() {
    document.getElementById('inputCheckPayment').classList.toggle('disabled');
}

function checkSaveContactData() {
    document.getElementById('inputCheckContact').classList.toggle('disabled');    
}

async function checkPromoCode() {
    const promoCode = document.getElementById('inputPromoCode').value;
    console.log(promoCode);
    if (promoCode === '') return Promise.resolve(undefined);
    
    const response = await fetch('/checkPromoCode', {
        method: 'POST',
        body: JSON.stringify({ "promoCode": promoCode }),
        headers: {
            'Content-Type': 'application/json',
        },
    });
    const data = await response.json();
    if (!data.success) {
        console.log("E2", data.error);
        return data.error;
    }
    subtotal = parseInt(document.getElementById('subtotal').innerHTML);
    delivery = parseInt(document.getElementById('delivery').innerHTML);
    discount = (subtotal * data.discount / 100).toFixed(2);
    document.getElementById('discount').innerHTML = discount;
    document.getElementById('total').innerHTML = subtotal - discount + delivery;
    return;
}

function updateShippingPrice() {
    const countryCode = document.getElementById('inputCountry').value;
    const city = document.getElementById('inputCity').value;
    const deliveryMethod = document.getElementById('inputDeliveryMethod').value;

    let price = 0;
    if (countryCode == 'UA') {
        if (city.includes('city')) {
            if (deliveryMethod == 'pickUpFromPostOffice') price = 80;
            else price = 110;
        }
        else
            if (deliveryMethod == 'pickUpFromPostOffice') price = 110;
            else price = 140;
    }
    else price = 600;
    document.getElementById('delivery').innerHTML = price;
    document.getElementById('total').innerHTML = parseInt(document.getElementById('subtotal').innerHTML) - parseInt(document.getElementById('discount').innerHTML) + parseInt(price);

    // fetch('/getShippingPrice', {
    //     method: 'POST',
    //     body: JSON.stringify({ "countryCode": countryCode, "branch": branch, "cart": cart }),
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    // })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.success) {
    //             price = data.price;
    //         } else {
    //             if (countryCode == 'UA') price = 100;
    //             else price = 400;
    //         }
    //         document.getElementById('delivery').innerHTML = price;
    //         document.getElementById('total').innerHTML = parseInt(document.getElementById('subtotal').innerHTML) - parseInt(document.getElementById('discount').innerHTML) + parseInt(data.price);
    //     });
}

document.getElementById('inputPromoCode').addEventListener('blur', checkPromoCode);

async function validateCheckout() {
    const firstName = document.getElementById('inputFirstName').value;
    const lastName = document.getElementById('inputLastName').value;
    const middleName = document.getElementById('inputMiddleName').value;
    const country = document.getElementById('inputCountry').value;
    const city = document.getElementById('inputCity').value;
    const deliveryMethod = document.getElementById('inputDeliveryMethod').value;
    const postOfficeBranch = document.getElementById('inputPostOfficeBranch').value;
    const address = document.getElementById('inputAddress').value;
    const postalCode = document.getElementById('inputPostalCode').value;
    const paymentMethod = document.getElementById('inputPaymentMethod').value;
    const contactMessenger = document.getElementById('inputContactMessenger').value;
    const username = document.getElementById('inputUsername').value;
    const phoneNumber = document.getElementById('inputPhoneNumber').value;

    if (firstName === '' || lastName === '' || middleName === '' || country === '' || city === '') {
        return('Please fill in all required fields');
    }
    if (deliveryMethod === 'pickUpFromPostOffice' && postOfficeBranch === '') {
        return('Please select post office branch');
    }
    if (deliveryMethod === 'deliverToAddress' && (address === '' || postalCode === '')) {
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
    const promoCodeError = await checkPromoCode();
    if (promoCodeError !== undefined) {
        return promoCodeError;
    }
    return '';
}

async function checkout() {
    const error = await validateCheckout();
    if (error !== '') {
        document.getElementById('buttonCheckout').innerHTML = error;
        setTimeout(function () {
            document.getElementById('buttonCheckout').innerHTML = 'Checkout';
        }, 5000);
        return;
    }

    const data = {
        "firstName": document.getElementById('inputFirstName').value,
        "lastName": document.getElementById('inputLastName').value,
        "middleName": document.getElementById('inputMiddleName').value,
        "country": document.getElementById('inputCountry').value,
        "city": document.getElementById('inputCity').value,
        "deliveryMethod": document.getElementById('inputDeliveryMethod').value
    }
    if (data['deliveryMethod'] == 'pickUpFromPostOffice') {
        data['postOfficeBranch'] = document.getElementById('inputPostOfficeBranch').value;
        data['postOfficeBranchName'] = document.getElementById('inputPostOfficeBranch').selectedOptions[0].getAttribute('data-name');
    } else {
        data['address'] = document.getElementById('inputAddress').value;
        data['address2'] = document.getElementById('inputAddress-2').value;
        data['postalCode'] = document.getElementById('inputPostalCode').value;
    }
    data['saveShippingData'] = !document.getElementById('inputCheckShipping').classList.contains('disabled');

    data['paymentMethod'] = document.getElementById('inputPaymentMethod').value;
    data['promoCode'] = document.getElementById('inputPromoCode').value;
    data['savePaymentData'] = !document.getElementById('inputCheckPayment').classList.contains('disabled');

    data['contactMessenger'] = document.getElementById('inputContactMessenger').value;
    if (data['contactMessenger'] == 'instagram') {
        data['username'] = document.getElementById('inputUsername').value;
    } else {
        data['phoneNumber'] = document.getElementById('inputPhoneNumber').value;
    }
    data['saveContactData'] = !document.getElementById('inputCheckContact').classList.contains('disabled');

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
                window.location.href = '/orderConfirmation';
            }
        });
}