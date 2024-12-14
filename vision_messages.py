from typing import List

def vision_msg(base64_images: List[str], user_prompt: str) -> dict:
    """
    Generates a message for a vision model, handling multiple base64 images.

    Args:
        base64_images: A list of base64 encoded images.
        user_prompt: The user's text prompt.

    Returns:
        A dictionary representing the message for the vision model.
    """
    msg: dict = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_prompt
            }
        ]
    }

    for base64_image in base64_images:
        image_data = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
            }
        }
        msg["content"].insert(-1, image_data)  # Insert image data before the text prompt

    return msg

