function getProduct() {
    const product = document.getElementById('inputProductNumber').value;
    const url = '/admin/product/' + product;
    window.location.href = url;
}

// allows to insert a new image
function triggerInput() {
    document.getElementById('inputImage').click();
}

function addImg() {
    const img = document.getElementById('inputImage').files[0];
    document.getElementById('inputImage').value = '';
    const formData = new FormData();
    formData.append('file', img);

    // <div class="imageWrapper">
    //     <div class="image">
    //         <img src="{{ url_for('static', filename='img/products/'+product.id|string+'/'+img) }}" alt="">
    //     </div>
    // </div>

    fetch('/admin/product/image?productId='+productId, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                return;
            }
            const wrapper = document.createElement('div');
            wrapper.className = 'imageWrapper';
            wrapper.id = 'image'+data['image'];

            const image = document.createElement('div');
            image.className = 'image';

            const svg = document.getElementById('deleteIcon').cloneNode(true);

            svg.setAttribute("onclick", `deleteImage('${data['image']}')`);

            const img = document.createElement('img');
            img.src = '/static/img/products/'+productId+'/'+data.image;
            img.alt = '';

            image.appendChild(img);
            image.appendChild(svg);
            wrapper.appendChild(image);

            document.getElementById('images').appendChild(wrapper);
            document.getElementById('images').appendChild(document.getElementById('addImage'));
        });
}

function deleteImage(img) {
    fetch('/admin/product/deleteImage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({image: img, productId: productId}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('image'+img).remove();
            }
            else {
                console.log(data.error);
            }
        });
}

function validateProduct() {
    const category = document.getElementById('inputCategory').value;
    if (category === '') return 'Invalid category';

    const brand = document.getElementById('inputBrand').value;
    if (brand === '') return 'Invalid brand';

    const price = document.getElementById('inputPrice').value;
    if (price === '') return 'Invalid price';

    const sizes = document.getElementById('inputSizes').value;
    if (sizes === '') return 'Invalid sizes';

    const season = document.getElementById('inputSeason').value;
    if (season === '') return 'Invalid season';

    const outerMaterial = document.getElementById('inputMaterialOuter').value;
    if (outerMaterial === '') return 'Invalid outer material';

    const innerMaterial = document.getElementById('inputMaterialInner').value;
    if (innerMaterial === '') return 'Invalid inner material';

    const insoleMaterial = document.getElementById('inputMaterialInsole').value;
    if (insoleMaterial === '') return 'Invalid insole material';

    const insoleLengths = document.getElementById('inputInsoleLengths').value;
    if (insoleLengths === '') return 'Invalid insole lengths';

    const quantities = document.getElementById('inputQuantitiesLeft').value;
    if (quantities === '') return 'Invalid quantities';

    const warehouses = document.getElementById('inputWarehouses').value;
    if (warehouses === '') return 'Invalid warehouses';

    return '';
}

function updateProduct() {
    // product id, category, brand, price, sizes, season, outer material, inner material, insole material, insole lengths, quantities, warehouses
    const error = validateProduct();
    if (error !== '') {
        document.getElementById('buttonUpdateProduct').innerText = error;
        setTimeout(() => {
            document.getElementById('buttonUpdateProduct').innerText = 'Update product';
        }, 2000);
        return;
    }

    const product = {
        id: productId,
        category: document.getElementById('inputCategory').value,
        brand: document.getElementById('inputBrand').value,
        price: document.getElementById('inputPrice').value,
        sizes: document.getElementById('inputSizes').value,
        season: document.getElementById('inputSeason').value,
        outerMaterial: document.getElementById('inputMaterialOuter').value,
        innerMaterial: document.getElementById('inputMaterialInner').value,
        insoleMaterial: document.getElementById('inputMaterialInsole').value,
        insoleLengths: document.getElementById('inputInsoleLengths').value,
        quantities: document.getElementById('inputQuantitiesLeft').value,
        warehouses: document.getElementById('inputWarehouses').value
    };

    fetch('/admin/product/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({data: product}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Product updated');
            }
            else {
                console.log(data.error);
            }
        });
}