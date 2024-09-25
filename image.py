import cv2
import numpy as np
from stegano import lsb


def encode_text_in_video(video_path, text_file, output_path, lsb_bits=1):
    # Read the video
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Read the text file (payload)
    with open(text_file, 'r') as file:
        payload = file.read()

    # Embed the payload bit by bit into the frames
    payload_bits = ''.join([format(ord(i), "08b") for i in payload])
    bit_index = 0
    max_bits = len(payload_bits)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Modify LSB bits in the frame's pixels
        if bit_index < max_bits:
            frame = encode_frame_with_lsb(frame, payload_bits[bit_index:bit_index + lsb_bits], lsb_bits)
            bit_index += lsb_bits

        # Write the frame with the hidden message
        out.write(frame)

    # Release everything
    cap.release()
    out.release()

    print("Video encoding completed.")


def encode_frame_with_lsb(frame, payload_bits, lsb_bits):
    # Flatten frame array for easy manipulation
    flat_frame = frame.flatten()

    for i in range(len(payload_bits)):
        if i < len(flat_frame):
            flat_frame[i] = (flat_frame[i] & ~(2 ** lsb_bits - 1)) | int(payload_bits[i:i + 1], 2)

    # Reshape the array back to the original frame shape
    return flat_frame.reshape(frame.shape)


def main():
    video_path = "./input_video.mp4"
    text_file = "./secret_message.txt"
    output_path = "./output_encoded_video.avi"
    lsb_bits = 1  # Number of LSB bits to use

    encode_text_in_video(video_path, text_file, output_path, lsb_bits)


if __name__ == "__main__":
    main()
