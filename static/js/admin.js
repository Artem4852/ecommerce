function getProduct() {
    const product = document.getElementById('inputProductNumber').value;
    const url = '/admin/products/edit/' + product;
    window.location.href = url;
}

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
            wrapper.id = 'image' + data['image'];
            wrapper.setAttribute('data-index', data['index']);

            const image = document.createElement('div');
            image.className = 'image';

            const svg = document.getElementById('deleteIcon').cloneNode(true);
            svg.setAttribute("id", "");
            svg.setAttribute("onclick", `deleteImage('${data['image']}')`);

            const svgBack = document.getElementById('backIcon').cloneNode(true);
            svgBack.setAttribute("id", "");
            svgBack.setAttribute("onclick", `imageBack('${data['image']}')`);

            const svgForward = document.getElementById('forwardIcon').cloneNode(true);
            svgForward.setAttribute("id", "");
            svgForward.setAttribute("onclick", `imageForward('${data['image']}')`);

            const img = document.createElement('img');
            img.src = '/static/img/products/'+productId+'/'+data.image;
            img.alt = '';

            image.appendChild(img);
            image.appendChild(svg);
            image.appendChild(svgBack);
            image.appendChild(svgForward);
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

function imageForward(img) {
    let images = document.getElementsByClassName('imageWrapper');
    images = Array.from(images).sort((a, b) => {
        return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
    });
    const currentIdx = parseInt(document.getElementById('image'+img).getAttribute('data-index'));
    if (currentIdx === images.length - 1) return;
    else {
        const next = images[currentIdx + 1];
        const current = images[currentIdx];
        const nextIndex = next.getAttribute('data-index');
        const currentIndex = current.getAttribute('data-index');
        next.setAttribute('data-index', currentIndex);
        current.setAttribute('data-index', nextIndex);
        document.getElementById('images').insertBefore(next, current);
    }
}

function imageBack(img) {
    let images = document.getElementsByClassName('imageWrapper');
    images = Array.from(images).sort((a, b) => {
        return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
    });
    const currentIdx = parseInt(document.getElementById('image'+img).getAttribute('data-index'));
    if (currentIdx === 0) return;
    else {
        const previous = images[currentIdx - 1];
        const current = images[currentIdx];
        const previousIndex = previous.getAttribute('data-index');
        const currentIndex = current.getAttribute('data-index');
        previous.setAttribute('data-index', currentIndex);
        current.setAttribute('data-index', previousIndex);
        document.getElementById('images').insertBefore(current, previous);
    }
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
        sizesCm: document.getElementById('inputInsoleLengths').value,
        maxQuantities: document.getElementById('inputQuantitiesLeft').value,
        warehouses: document.getElementById('inputWarehouses').value,
        images: Array.from(document.getElementsByClassName('imageWrapper'))
            .sort((a, b) => parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index')))
            .map(wrapper => wrapper.id.substring(5)),
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
                window.location.href = '/product/' + productId;
            }
            else {
                console.log(data.error);
            }
        });
}

const inputs = ['Sizes', 'InsoleLengths', 'QuantitiesLeft', 'Warehouses'];
inputs.forEach(input => {
    document.getElementById('input' + input).addEventListener('blur', () => {
        const sizes = document.getElementById('input' + input).value.trim();
        if (sizes === '') return;

        let sizesArray;

        if (input === 'Sizes') {
            sizesArray = sizes.split(',').map(size => size.trim())
        } else {
            sizesArray = sizes.split(',').map(size => size.trim().split(' ')[0].trim());
        }

        let currentInputs = inputs.filter(i => i !== input);

        currentInputs.forEach(currentInput => {
            const input = document.getElementById('input' + currentInput);
            const toAdd = [];
            sizesArray.forEach(size => {
                if (size === '' || size === '()') return;
                if (!input.value.includes(size)) {
                    if (currentInput === 'Sizes') {
                        toAdd.push(size);
                    } else if (currentInput === 'InsoleLengths') {
                        toAdd.push(`${size} ( cm)`);
                    } else if (currentInput === 'QuantitiesLeft') {
                        toAdd.push(`${size} (1)`);
                    } else {
                        toAdd.push(`${size} ()`);
                    }
                }
            });

            if (input.value === '' && toAdd.length > 0) {
                input.value += toAdd.join(', ');
            } else if (toAdd.length > 0) {
                input.value += ', ' + toAdd.join(', ');
            }
        });
    });
});

document.getElementById('inputInstagramUrl').addEventListener('blur', () => {
    const url = document.getElementById('inputInstagramUrl').value;
    console.log(productId, url)
    if (url === '') return;

    fetch('/admin/product/load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ productId: productId, url: url }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                document.getElementById('inputSizes').value = data.sizes.join(', ');
                document.getElementById('inputInsoleLengths').value = Object.entries(data.sizesCm)
                    .map(([size, value]) => `${size} (${value} cm)`)
                    .join(', ');
                document.getElementById('inputSizes').dispatchEvent(new Event('blur'));
                document.getElementById('inputPrice').value = data.price;
                document.getElementById('inputBrand').value = data.brand;
                document.getElementById('inputCategory').value = data.category;
                // delete previous images
                document.getElementById('images').innerHTML = '';
                for (let i = 0; i < data.images.length; i++) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'imageWrapper';
                    wrapper.id = 'image' + data.images[i];
                    wrapper.setAttribute('data-index', i);

                    const image = document.createElement('div');
                    image.className = 'image';

                    const svg = document.getElementById('deleteIcon').cloneNode(true);
                    svg.setAttribute("id", "");
                    svg.setAttribute("onclick", `deleteImage('${data.images[i]}')`);

                    const svgBack = document.getElementById('backIcon').cloneNode(true);
                    svgBack.setAttribute("id", "");
                    svgBack.setAttribute("onclick", `imageBack('${data.images[i]}')`);

                    const svgForward = document.getElementById('forwardIcon').cloneNode(true);
                    svgForward.setAttribute("id", "");
                    svgForward.setAttribute("onclick", `imageForward('${data.images[i]}')`);

                    const img = document.createElement('img');
                    img.src = '/static/img/products/'+productId+'/'+data.images[i];
                    img.alt = '';

                    image.appendChild(img);
                    image.appendChild(svg);
                    image.appendChild(svgBack);
                    image.appendChild(svgForward);
                    wrapper.appendChild(image);

                    document.getElementById('images').appendChild(wrapper);
                }

                const addImage = document.createElement('div');
                addImage.id = 'addImage';
                addImage.className = 'add';
                addImage.setAttribute('onclick', 'triggerInput()');

                const plus = document.createElement('div');
                plus.className = 'plus';
                plus.innerText = '+';

                const input = document.createElement('input');
                input.type = 'file';
                input.id = 'inputImage';
                input.style.display = 'none';
                input.addEventListener('change', addImg);
                
                addImage.appendChild(plus);
                addImage.appendChild(input);
                document.getElementById('images').appendChild(addImage);
            }
            else {
                console.log(data.error);
            }
        });
});