import os
import tkinter as tk
import tkinter.ttk as ttk

import PIL.Image
import PIL.ImageTk
import keyboard

image_dir_name = "img"
timeout = 8
# fmt: off
one_table = [
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8
]
# fmt: on


def get_one_count(n):
    count = 0
    for i in range(0, 32, 8):
        count += one_table[(n >> i) & 0xFF]
    return count


def init_settings(image_dir_path):
    keys = []
    with open(f"{image_dir_path}/keys.txt") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) > 0:
                keys.append(line)
    invalid_patterns = []
    with open(f"{image_dir_path}/invalid.txt") as f:
        for line in f.readlines():
            number = 0
            for part in line.split("+"):
                part = part.strip()
                if len(part) > 0 and part.isdigit():
                    number += int(2 ** (int(part) - 1))
            if number != 0:
                invalid_patterns.append(number)
    images = [None] * (2 ** len(keys))
    for _, _, files in os.walk(image_dir_path):
        for file in files:
            name = os.path.splitext(file)[0]
            if not name.replace("+", "").isdigit():
                continue
            number = 0
            for part in name.split("+"):
                number += int(2 ** (int(part) - 1))
            images[number] = PIL.Image.open(f"{image_dir_path}/{file}")
    return keys, images, invalid_patterns


def composite(images, invalid_patterns):
    bg = images[0]
    sorted_images = sorted(zip(range(len(images)), images), key=lambda x: get_one_count(x[0]), reverse=True)
    for index, (number, image) in enumerate(sorted_images):
        if image is not None:
            images[number] = PIL.Image.alpha_composite(bg, image)
            continue
        if number in invalid_patterns:
            continue
        new_image = PIL.Image.new(bg.mode, bg.size)
        not_composited = number
        for number2, image2 in sorted_images[index + 1 :]:
            if number2 & not_composited == number2 and image2 is not None:
                new_image = PIL.Image.alpha_composite(image2, new_image)
                not_composited -= number2
            if not_composited == 0:
                break
        images[number] = PIL.Image.alpha_composite(bg, new_image)


def pillowed(images):
    for index, image in enumerate(images):
        if image is not None:
            images[index] = PIL.ImageTk.PhotoImage(image)


def main():
    keys, images, invalid_patterns = init_settings(image_dir_name)
    previous_valid_patterns = [0] * len(invalid_patterns)
    composite(images, invalid_patterns)
    root = tk.Tk()
    frame = ttk.Frame(root)
    label = ttk.Label(frame)
    pillowed(images)
    image_index = 0
    label["image"] = images[image_index]
    label.pack()
    frame.pack()

    def set_image(index):
        label["image"] = images[index]

    def update():
        number = 0
        for index, key in enumerate(keys):
            if keyboard.is_pressed(key):
                number += 1 << index
        for index, invalid_pattern in enumerate(invalid_patterns):
            if number & invalid_pattern == invalid_pattern:
                if previous_valid_patterns[index] == 0:
                    number -= invalid_pattern
                else:
                    number -= previous_valid_patterns[index]
            elif number & invalid_pattern != 0:
                previous_valid_patterns[index] = number & invalid_pattern
        set_image(number)
        frame.after(timeout, update)

    frame.after(timeout, update)
    root.mainloop()


if __name__ == "__main__":
    main()
