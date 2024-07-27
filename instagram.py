from rocketapi import InstagramAPI
import dotenv, os, random, json, requests

# https://www.instagram.com/p/C95Svt0NLGg/?img_index=1

def parsePost(caption):
    sizes = []
    for line in caption.split("\n"):
        if line.startswith("#kids_fashion_store_eu_"):
            sizes.append(line.split("_")[-1])

    sizesCm = []
    for size in sizes:
        for line in caption.split("\n"):
            if (f'Розмір ' + size) in line:
                sizesCm.append({str(size): line.split(" ")[-2].replace("(", "")})

    price = 0
    for line in caption.split("\n"):
        if line.startswith("Ціна"):
            if int(line.split(" ")[1]) > price:
                price = int(line.split(" ")[1])
    return sizes, sizesCm, price

def loadImage(url, productId):
    os.makedirs(f'static/img/products/{productId}', exist_ok=True)
    existing = sorted([im.split('.')[0] for im in os.listdir(f'static/img/products/{productId}') if im.endswith('.jpg')])
    if existing:
        new = str(int(existing[-1])+1)
    else:
        new = '1'
 
    response = requests.get(url)
    with open(f'static/img/products/{productId}/{new}.jpg', 'wb') as f:
        f.write(response.content)

def getPost(link, productId):
    dotenv.load_dotenv()
    token = random.choice(os.getenv("ROCKET_TOKENS").split(","))
    rocket = InstagramAPI(token)
    shortCode = link.split("/")[-2]
    post = rocket.get_media_info_by_shortcode(link)
    with open(f"post_{productId}.json", "w") as f:
        json.dump(post, f)
    caption = post["items"][0]['caption']['text']
    sizes, sizesCm, price = parsePost(caption)

    images = []
    for image in post['items'][0]['carousel_media']:
        images.append(image['image_versions2']['candidates'][0]['url'])
    
    for image in images:
        loadImage(image, productId)
    
    return sizes, sizesCm, price

if __name__ == "__main__":
    getPost("C95Svt0NLGg", 1)