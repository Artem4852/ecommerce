from rocketapi import InstagramAPI
import dotenv, os, random, json, requests, re

# https://www.instagram.com/p/C95Svt0NLGg/?img_index=1

def parsePost(caption, username):
    sizes = []
    for line in caption.split("\n"):
        if username == 'marynahavrykova':
            if 'см' in line:
                size = line.split("-")[0].strip()
                size = re.sub(r'[^\d]', '', size)
                try: sizes.append(size.split("/")[1])
                except: sizes.append(size)

        elif username == 'kids_premium_shoes':
            if ' р ' in line:
                size = line.split(" ")[0]
                size = re.sub(r'[^\d]', '', size)
                try: sizes.append(size.split("/")[1])
                except: sizes.append(size)
        else:
            if "Розмір" in line:
                size = line.split(" ")[1]
                size = re.sub(r'[^\d]', '', size)
                try: sizes.append(size.split("/")[1])
                except: sizes.append(size)

    sizesCm = {}
    for size in sizes:
        for line in caption.split("\n"):
            if username == 'marynahavrykova':
                if (size in line and 'см' in line):
                    sizesCm[str(size)] = line.split("-")[1].strip().split(" ")[0].replace(",", ".")
            elif username == 'kids_premium_shoes':
                if (size + ' р ') in line:
                    line = line[:line.index('см')]
                    try: sizesCm[str(size)] = line.split(" ")[-2].replace("(", "").split("/")[1]
                    except: sizesCm[str(size)] = line.split(" ")[-2].replace("(", "")
            else:
                if ('Розмір ' + size) in line:
                    try: sizesCm[str(size)] = line.split(" ")[-2].replace("(", "").split("/")[1]
                    except: sizesCm[str(size)] = line.split(" ")[-2].replace("(", "")


    price = 0
    for line in caption.split("\n"):
        if username == 'kids_premium_shoes':
            if 'Ціна' in line:
                if int(line.split(" ")[1]) > price:
                    price = int(line.split(" ")[1])
        else:
            if line.startswith("Ціна"):
                if username == 'marynahavrykova':
                    new_price = int(line.split(" ")[-2])
                else:    
                    new_price = int(line.split(" ")[1])
                if new_price > price:
                    price = new_price

    category = ""
    if "демі" in caption.split("\n")[0].lower(): category = "Demi"
    elif "кросівки" in caption.split("\n")[0].lower(): category = "Sneakers"
    elif "кеди" in caption.split("\n")[0].lower(): category = "Sneakers"
    elif "черевики" in caption.split("\n")[0].lower(): category = "Boots"
    elif "босоніжки" in caption.split("\n")[0].lower(): category = "Sandals"
    elif "сандалі" in caption.split("\n")[0].lower(): category = "Sandals"

    brand = ""
    if "італійського" in caption.split("\n")[0].lower(): brand = "Geox"
    elif "австрійського" in caption.split("\n")[0].lower(): brand = "Superfit"
    elif "німецького" in caption.split("\n")[0].lower(): brand = "Adidas"
    elif "данського" in caption.split("\n")[0].lower(): brand = "Ecco"

    return sizes, category, brand, sizesCm, price

def loadImage(url, productId, index):
    os.makedirs(f'static/img/products/{productId}', exist_ok=True)
    if not index:
        existing = sorted([im.split('.')[0] for im in os.listdir(f'static/img/products/{productId}') if im.endswith('.jpg')])
        if existing:
            new = str(int(existing[-1])+1)
        else:
            new = '0'
    else:
        new = str(index)
 
    response = requests.get(url)
    with open(f'static/img/products/{productId}/{new}.jpg', 'wb') as f:
        f.write(response.content)
    return f'{new}.jpg'

def getPost(link, productId):
    dotenv.load_dotenv()
    token = random.choice(os.getenv("ROCKET_TOKENS").split(","))
    rocket = InstagramAPI(token)
    shortCode = link.split("/")[-2]
    post = rocket.get_media_info_by_shortcode(shortCode)
    # with open(f"json/post_{productId}.json", "w") as f:
    #     json.dump(post, f)
    caption = post["items"][0]['caption']['text']
    username = post["items"][0]['user']['username']
    sizes, category, brand, sizesCm, price = parsePost(caption, username)

    images = []
    for image in post['items'][0]['carousel_media']:
        images.append(image['image_versions2']['candidates'][0]['url'])
    
    imagesSrcs = []
    for n, image in enumerate(images):
        imagesSrcs.append(loadImage(image, productId, n))
    
    return caption, sizes, category, brand, sizesCm, price, imagesSrcs

if __name__ == "__main__":
    print(getPost("https://www.instagram.com/p/C95Svt0NLGg/?img_index=1", 1))