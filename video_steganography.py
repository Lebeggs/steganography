import math
import os
import re
import shutil
from subprocess import call, STDOUT
import cv2
from PIL import Image

# Global Variable
global frame_location


def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    temp_folder = "./temp"
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1


def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")


def generateData(data):
    newdata = []
    for i in data:
        newdata.append(format(ord(i), '08b'))
    return newdata


def modifyPixel(pixel, data, bits):
    datalist = generateData(data)
    lengthofdata = len(datalist)
    imagedata = iter(pixel)
    for i in range(lengthofdata):
        pixel = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        for j in range(bits):  # Adjust to use specified bits
            if datalist[i][j] == '0' and pixel[j] % 2 != 0:
                pixel[j] -= 1
            elif datalist[i][j] == '1' and pixel[j] % 2 == 0:
                pixel[j] -= 1 if pixel[j] != 0 else -1
        if i == lengthofdata - 1:
            pixel[-1] -= 1 if pixel[-1] % 2 == 0 and pixel[-1] != 0 else -1
        else:
            pixel[-1] -= 1 if pixel[-1] % 2 != 0 else 0
        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]


def encoder(newimage, data, n_lsb):
    w = newimage.size[0]
    (x, y) = (0, 0)

    for pixel in modifyPixel(newimage.getdata(), data, n_lsb):
        newimage.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


def encode(start, end, filename, frame_loc, output_folder, n_lsb):
    total_frame = end - start + 1
    print("Frame start", start)
    print("\nFrame end", end)
    try:
        with open(filename) as fileinput:
            filedata = fileinput.read() + '====='
    except FileNotFoundError:
        print("\nFile to hide not found! Exiting...")
        quit()

    datapoints = math.ceil(len(filedata) / total_frame)
    counter = start
    print("Performing Steganography...")
    for convnum in range(0, len(filedata), datapoints):
        numbering = os.path.join(frame_loc, "{}.png".format(counter))
        print("numbering is: ", numbering)
        encodetext = filedata[convnum:convnum + datapoints]
        try:
            image = Image.open(numbering, 'r')
        except FileNotFoundError:
            print("\n%d.png not found" % counter)
            quit()

        newimage = image.copy()
        encoder(newimage, encodetext, n_lsb)  # Pass n_lsb to the encoder

        new_img_name = os.path.join(output_folder, "{}.png".format(counter))
        newimage.save(new_img_name, str(new_img_name.split(".")[1].upper()))
        counter += 1

    print("Complete!\n")


def decode(number, frame_location, n_lsb=8):
    data = ''
    numbering = str(number)
    decoder_numbering = os.path.join(frame_location, "{}.png".format(numbering))
    image = Image.open(decoder_numbering, 'r')
    imagedata = iter(image.getdata())

    while True:
        pixels = [value for value in imagedata.__next__()[:3] + imagedata.__next__()[:3] + imagedata.__next__()[:3]]
        binstr = ''

        # Collecting bits
        for i in pixels[:n_lsb]:
            binstr += '0' if i % 2 == 0 else '1'

        # Debugging print
        print(f"Extracted bits: {binstr}")

        if len(binstr) == n_lsb:
            char = chr(int(binstr, 2))
            if re.match("[ -~]", char):  # Check if it's printable
                data += char

            # Check for termination
            if pixels[-1] % 2 != 0:  # Assuming termination is in the last pixel
                print(f"Termination detected. Final data: {data}")
                return data
        else:
            print("Warning: Not enough bits extracted, continuing...")

    return data


def input_main(video_filename, message_filename, frame_location, output_file_path, n_lsb):
    frame_extraction(video_filename)
    call(["ffmpeg", "-i", video_filename, "-q:a", "0", "-map", "a", "audio.mp3", "-y"],
         stdout=open(os.devnull, "w"), shell=True, stderr=STDOUT)
    encode(0, len(os.listdir(frame_location)) - 1, message_filename, frame_location, "temp", n_lsb)
    call(["ffmpeg", "-i", "temp/%d.png", "-c:v", "ffv1", output_file_path, "-y"],
         stdout=open(os.devnull, "w"), stderr=STDOUT)
    call(["ffmpeg", "-i", output_file_path, "-i", "audio.mp3", "-c:v", "ffv1", "-c:a", "aac", "Embedded_Video.avi",
          "-y"],
         stdout=open(os.devnull, "w"), stderr=STDOUT)


def encode_video(video_filename, message_filename, output_file_path, n_lsb):
    input_main(video_filename=video_filename,
               message_filename=message_filename,
               frame_location="./temp",
               output_file_path=output_file_path,
               n_lsb=n_lsb)
    clean_temp()


def decode_video(file_name, n_lsb):
    frame_extraction(file_name)
    extracted_data = ""
    for convnum in range(len(os.listdir("./temp")) - 1):
        try:
            extracted_data += decode(convnum, "./temp", n_lsb)
        except StopIteration:
            print("No data found in Frame %d" % convnum)

    result = extracted_data.split("=====", 1)[0]
    clean_temp()
    return result


def main():
    video_filename = "FLIGHT.mp4"  # Replace with your video file
    message_filename = "secret.txt"  # Replace with your message file
    output_file_path = "Embedded_Video.avi"  # The output video file path

    n_lsb = int(input("Enter the number of LSBs to use for hiding data (1-8): "))

    print("Encoding process started...\n")
    encode_video(video_filename, message_filename, output_file_path, n_lsb)
    print("Encoding completed and saved to", output_file_path)

    print("\nDecoding process started...\n")
    decoded_message = decode_video(output_file_path, n_lsb)
    print("Decoded Message:", decoded_message)


if __name__ == "__main__":
    main()
