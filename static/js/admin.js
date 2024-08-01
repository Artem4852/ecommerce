function getProduct() {
    const product = document.getElementById('inputProductNumber').value;
    if (product === '') return;
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
    const error = validateProduct();
    if (error !== '') {
        document.getElementById('buttonUpdateProduct').innerText = error;
        setTimeout(() => {
            document.getElementById('buttonUpdateProduct').innerText = translations['updateProduct'][lang];
        }, 2000);
        return;
    }

    const product = {
        id: productId,
        tags: document.getElementById('inputTags').value,
        category: document.getElementById('inputCategory').value,
        brand: document.getElementById('inputBrand').value,
        prevPrice: document.getElementById('inputPrice').value,
        discount: document.getElementById('inputDiscount').value,
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

function archiveProduct() {
    const inputTags = document.getElementById('inputTags');
    inputTags.value = 'archived, ' + inputTags.value;
    const buttonArchiveProduct = document.getElementById('buttonArchiveProduct');
    buttonArchiveProduct.innerText = translations['archived'][lang];
    setTimeout(() => {
        buttonArchiveProduct.innerText = translations['unarchiveProduct'][lang];
        buttonArchiveProduct.setAttribute('onclick', 'unarchiveProduct()');
    }, 2000);
}

function unarchiveProduct() {
    const inputTags = document.getElementById('inputTags');
    inputTags.value = inputTags.value.replace('archived, ', '').replace(', archived', '');
    const buttonArchiveProduct = document.getElementById('buttonArchiveProduct');
    buttonArchiveProduct.innerText = translations['unarchived'][lang];
    setTimeout(() => {
        buttonArchiveProduct.innerText = translations['archiveProduct'][lang];
        buttonArchiveProduct.setAttribute('onclick', 'archiveProduct()');
    }, 2000);
}

function archiveProductNoForm(productId) {
    fetch('/admin/product/archive', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({productId: productId}),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('archived'+productId).classList.toggle('hidden');
                document.getElementById('sizes'+productId).classList.toggle('hidden');
                button = document.getElementById('buttonArchiveProduct'+productId);
                if (button.innerText === translations['archive'][lang]) {
                    button.innerText = translations['unarchive'][lang];
                } else {
                    button.innerText = translations['archive'][lang];
                }
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

function filterOrders(criterion) {
    const criterionValue = document.getElementById(criterion).value;
    console.log(criterionValue);
    const url = new URL(window.location.href);
    if (criterionValue === 'Any' || criterionValue === '') url.searchParams.delete(criterion);
    else url.searchParams.set(criterion, criterionValue);
    url.searchParams.delete('scroll');
    url.searchParams.delete('page');
    window.location.href = url.toString();
}

function setStatus(status) {
    statusWrapper = document.getElementById('status' + status);

    fetch('/admin/order/status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ orderId: orderId, status: status }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                statusWrappers = document.getElementsByClassName('status');
                Array.from(statusWrappers).forEach(wrapper => {
                    wrapper.children[0].classList.remove('active');
                });

                statusWrapper.children[0].classList.add('active');
            }
            else {
                console.log(data.error);
            }
        });
}

function setTrackingNumber() {
    const trackingNumber = document.getElementById('inputTrackingNumber').value;
    if (trackingNumber === '') return;
    fetch('/admin/order/trackingNumber', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ orderId: orderId, trackingNumber: trackingNumber }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('inputTrackingNumber').value = translations['saved'][lang];
                setTimeout(() => {
                    document.getElementById('inputTrackingNumber').value = trackingNumber;
                }, 2000);
            }
            else {
                console.log(data.error);
            }
        });
}

function deleteOrder(productId) {
    fetch('/admin/order/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ orderId: orderId, productId: productId }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/admin/orders';
            }
            else {
                console.log(data.error);
            }
        });
}