from PIL import Image

# Load the image
img = Image.open("image.jpg")

# Resize to desired dimensions (e.g., 16x16)
scaled_img = img.resize((16, 16))

# Save or show the resized image
scaled_img.save("resized_image.jpg")
# OR to preview it
scaled_img.show()
