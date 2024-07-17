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