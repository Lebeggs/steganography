# image_steganography.py
from PIL import Image

def encode_text_in_image(payload, image_path, lsb_bits):
    image = Image.open(image_path)
    image = image.convert("RGB")
    payload += '###'  # Add delimiter to mark the end of the message
    binary_payload = ''.join([format(ord(i), "08b") for i in payload])  # Convert payload to binary

    pixels = list(image.getdata())
    new_pixels = []

    payload_index = 0
    # Calculate how many bits can be stored in the image
    max_bits = len(pixels) * lsb_bits * 3  # 3 color channels (R, G, B)

    if len(binary_payload) > max_bits:
        raise ValueError("Message is too large to fit in the cover image.")

    for pixel in pixels:
        r, g, b = pixel
        new_pixel = list(pixel)

        for i in range(lsb_bits):  # LSB encoding in each color channel
            if payload_index < len(binary_payload):
                new_pixel[0] = (r & ~1) | int(binary_payload[payload_index])  # Encode in red channel
                payload_index += 1
            if payload_index < len(binary_payload):
                new_pixel[1] = (g & ~1) | int(binary_payload[payload_index])  # Encode in green channel
                payload_index += 1
            if payload_index < len(binary_payload):
                new_pixel[2] = (b & ~1) | int(binary_payload[payload_index])  # Encode in blue channel
                payload_index += 1

        new_pixels.append(tuple(new_pixel))

    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    new_image.save("stego_image.png")
    print("Message encoded in image and saved as stego_image.png")


def decode_text_from_image(stego_image_path, lsb_bits):
    image = Image.open(stego_image_path)
    binary_payload = ""
    pixels = list(image.getdata())

    for pixel in pixels:
        r, g, b = pixel

        # Extract LSBs based on the specified number of bits
        for i in range(lsb_bits):
            binary_payload += bin(r)[-1]  # Extract from red channel
            binary_payload += bin(g)[-1]  # Extract from green channel
            binary_payload += bin(b)[-1]  # Extract from blue channel

    decoded_message = ""
    for i in range(0, len(binary_payload), 8):
        byte = binary_payload[i:i+8]
        decoded_message += chr(int(byte, 2))
        if "###" in decoded_message:  # End of message marker
            break

    print("Hidden message:", decoded_message.replace("###", ""))



# Example usage:
encode_text_in_image("Secret Message", "hua.png", 3)
decode_text_from_image("stego_image.png", 3)
