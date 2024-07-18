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
    fetch('/add-to-cart/' + productId, {
        method: 'POST',
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
    window.location.href = url.toString();
}