function favorite(productNumber) {
    console.log(productNumber)
    fetch('/favorite/' + productNumber, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const favoriteIcon = document.getElementById('favorite-' + productNumber);
                console.log(favoriteIcon)
                favoriteIcon.setAttribute('class', data.favorite ? 'favorite-icon favorite' : 'favorite-icon');
            }
        });
}

function addToCart(productNumber) {
    fetch('/add-to-cart/' + productNumber, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const cartButton = document.getElementById('cart-button-' + productNumber);
                cartButton.innerText = "Added to cart!";
                setTimeout(function () {
                    cartButton.innerHTML = "Add to cart";
                }, 2000);
            }
        });
}

function filterShoes(criterion) {
    const cards = document.getElementsByClassName('card');
    const criterionValue = document.getElementById(criterion).value;
    console.log(criterion, criterionValue, cards);
    for (let i = 0; i < cards.length; i++) {
        if (String(cards[i].getAttribute('data-'+criterion)) !== String(criterionValue) && String(criterionValue) !== 'any') {
            cards[i].style.display = 'none';
        }
    }
}