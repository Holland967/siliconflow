from PIL import Image, ImageOps
import base64
import io

# Define a function to process an image given its path
def process_image(uploaded_image):
    try:
        # Open the image file and assign it to img
        with Image.open(uploaded_image) as img:
            # Check if the image is a transparent PNG
            is_transparent_png = img.mode == "RGBA"
            # If the image is a transparent PNG
            if is_transparent_png:
                # Convert the image to RGB mode
                img = img.convert("RGB")
            
            # Get the width and height of the image
            width, height = img.size
            # If the image is larger than 1024x1024 pixels
            if width >= 1024 or height >= 1024:
                # Set the maximum size to 1024x1024 pixels
                max_size = (1024, 1024)
                # Resize the image to fit within the maximum size
                img = ImageOps.fit(img, max_size, Image.Resampling.LANCZOS)
            
            # Create a BytesIO object to hold the image data
            img_byte_arr = io.BytesIO()
            # Save the image to the BytesIO object in PNG format
            img.save(img_byte_arr, format="PNG")
            # Get the binary data from the BytesIO object
            img_byte_arr = img_byte_arr.getvalue()
            # If the image data is larger than 1MB
            if len(img_byte_arr) > 1 * 1024 * 1024:
                # Set the initial compression level to 9 (maximum)
                compress_level = 9
                # While the image data is larger than 1MB and compression level is greater than 0
                while len(img_byte_arr) > 1 * 1024 * 1024 and compress_level > 0:
                    # Create a new BytesIO object
                    img_byte_arr = io.BytesIO()
                    # Save the image with the current compression level
                    img.save(img_byte_arr, format="PNG", compress_level=compress_level)
                    # Get the binary data from the BytesIO object
                    img_byte_arr = img_byte_arr.getvalue()
                    # Decrease the compression level by 1
                    compress_level -= 1
            
            # If the image is a transparent PNG
            if is_transparent_png:
                # Open the image from the BytesIO object
                img = Image.open(io.BytesIO(img_byte_arr))
                # Convert the image back to RGBA mode
                img = img.convert("RGBA")
                # Create a new BytesIO object
                img_byte_arr = io.BytesIO()
                # Save the image to the BytesIO object in PNG format
                img.save(img_byte_arr, format="PNG")
                # Get the binary data from the BytesIO object
                img_byte_arr = img_byte_arr.getvalue()
            
            # Encode the image data in base64 and decode it to a string
            base64_encoded_image = base64.b64encode(img_byte_arr).decode("utf-8")
            
            return base64_encoded_image
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
