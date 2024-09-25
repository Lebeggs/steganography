# steganography_factory.py
from image_steganography import encode_text_in_image, decode_text_from_image
from audio_steganography import encode_text_in_audio, decode_text_from_audio
from video_steganography import encode_text_in_video, decode_text_from_video
from gif_steganography import encode_text_in_gif, decode_text_from_gif

def get_steganography_module(file_type):
    if file_type == 'image':
        return encode_text_in_image, decode_text_from_image
    elif file_type == 'audio':
        return encode_text_in_audio, decode_text_from_audio
    elif file_type == 'video':
        return encode_text_in_video, decode_text_from_video
    elif file_type == 'gif':
        return encode_text_in_gif, decode_text_from_gif
    else:
        raise ValueError("Unsupported file type")
