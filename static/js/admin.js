function getProduct() {
    const product = document.getElementById('inputProductNumber').value;
    const url = '/admin/product/' + product;
    window.location.href = url;
}