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
            if (data.success) {
                const wrapper = document.createElement('div');
                wrapper.className = 'imageWrapper';

                const image = document.createElement('div');
                image.className = 'image';

                const img = document.createElement('img');
                img.src = '/static/img/products/'+productId+'/'+data.image;
                img.alt = '';

                image.appendChild(img);
                wrapper.appendChild(image);

                document.getElementById('images').appendChild(wrapper);
                document.getElementById('images').appendChild(document.getElementById('addImage'));
            }
        });
}