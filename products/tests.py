# from django.test import TestCase

# Create your tests here.
url = "https://fakestoreapi.com/products/"
response = requests.get(url)
data = response.json()

# Limit to first 5 products
products_to_save = data[:5]

for product in products_to_save:
    # Extract relevant data from the API response
    title = product["title"]
    price = product["price"]
    description = product["description"]
    # ... (other product fields)
    category_name = product.get("category", "Uncategorized")  # Handle missing category

    # Create or retrieve a Category object based on name (optional)
    category, created = Category.objects.get_or_create(name=category_name)

    if "image" in product:
        image_url = product["image"]

        # Download image data
        image_response = requests.get(image_url, stream=True)

        if image_response.status_code == 200:
            # Generate a unique filename (optional)
            import uuid

            filename = str(uuid.uuid4()) + '.jpg'  # Adjust file extension based on image type
            # filename_path = "product_images/" + str(uuid.uuid4()) + '.jpg'  # Adjust file extension based on image type

            # Save the image to the file system (optional processing using Pillow)
            with open(f'images/product_images/{filename}', 'wb') as f:
                for chunk in image_response.iter_content(1024):
                    f.write(chunk)

            # Create and save a new Product object
            new_product = Product(name=title, price=price, description=description,
                                  category=category)
            new_product.save()

            # Create and save a new ProductImage object (optional)
            new_image = ProductImage(product=new_product,
                                     image="product_images/" + filename)  # Foreign key relationship
            new_image.save()

    else:
        # Handle case where image URL is not available
        print("Image URL not found for product:", title)