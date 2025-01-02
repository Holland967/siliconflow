from PIL import Image
import io
import base64

def image_processor(uploaded_image):
    img = Image.open(uploaded_image)

    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background

    max_size = 1024
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    output_buffer = io.BytesIO()
    img.save(output_buffer, format='PNG', quality=95)
    while output_buffer.tell() > 1024 * 1024:
        quality = int(95 * (1024 * 1024 / output_buffer.tell()))
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='PNG', quality=quality)

    base64_encoded = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

    return base64_encoded
