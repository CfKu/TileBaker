# -*- coding: utf-8 -*-
#
# Copyright © by Christof Küstner

"""
Tile baker - combines pictures in given source directory

@author: kuestner
"""

# ==============================================================================
# IMPORT
# ==============================================================================
import sys
import os
import platform
import subprocess
from glob import glob
from datetime import datetime
from PIL import Image

# Local imports


# ==============================================================================
# CONSTANTS
# ==============================================================================
# TODO: Introduce margin
IMAGE_INPUT_FOLDER = "img_in"
KACHEL_OUTPUT_FOLDER = "img_out"
KACHEL_OUTPUT_FILENAME = "department_tile"
KACHEL_SHAPE = (5, 2)  # number of images on kachel: horizontal, vertical
KACHEL_IMG_SIZE_OUT = (2800, 1500)  # pixels: horizontal, vertical
KACHEL_IMG_SIZE_OUT_LOW = 1000  # width or height of low resultion kachel out
KACHEL_COLOR_SCHEME = "RGB"  # color scheme: RGB or CMYK
KACHEL_JPG_QUALITY = 96  # JPG quality of output JPG file


# ==============================================================================
# DEFINITION
# ==============================================================================
print()
print(" TILE BAKER by CfK & CSr ~~~".rjust(80, "~"))
print()
print(
    ">>> Info: Due to your security settings in Windows, the execution of\n"
    " this script directly on a network share (like \\...) may fail\n"
    " to load some of the images. Please copy all files to a local drive\n"
    " like C:\, D:\, ... and run it again."
)
print()

# init kachel output image
kachel_out = Image.new(KACHEL_COLOR_SCHEME, KACHEL_IMG_SIZE_OUT)
kachel_px_width = KACHEL_IMG_SIZE_OUT[0]
kachel_px_height = KACHEL_IMG_SIZE_OUT[1]

# init available pixel size for each image
img_count_h = KACHEL_SHAPE[0]
img_count_v = KACHEL_SHAPE[1]
img_px_width = kachel_px_width // img_count_h
img_px_height = kachel_px_height // img_count_v

# print some information
print(
    ">>> Info: The height of each image is fitted to the defined\n"
    " kachel space ({}x{} images on {}x{} pixels). If you want to change\n"
    " the clipping of an image, you will have to crop it with an image \n"
    " editor of your choice.".format(
        img_count_h, img_count_v, kachel_px_width, kachel_px_height
    )
)
print()

# read all available images
img_src = glob(os.path.abspath(os.path.join(".", IMAGE_INPUT_FOLDER, "*.jpg")))

# check number of pictures and dimension of kachel
if len(img_src) != img_count_h * img_count_v:
    print(
        "Number of images (={}) does not match kachel size (={}x{})!\n"
        "Please adjust kachel size or the number of images...".format(
            len(img_src), img_count_h, img_count_v
        )
    )
else:
    # compose kachel
    for i_v in range(img_count_v):
        for i_h in range(img_count_h):
            # image file source
            img_i = i_h + i_v * img_count_h
            img_filepath = img_src[img_i]
            # compute image coordinates
            img_pos_x = img_px_width * i_h
            img_pos_y = img_px_height * i_v
            # open image file
            img = Image.open(img_filepath)
            img_width, img_height = img.size
            # fit height of img in space
            img_ratio = img_width / img_height
            img = img.resize(
                (int(img_px_height * img_ratio), img_px_height), Image.ANTIALIAS
            )
            img_width, img_height = img.size
            # check width of image
            if img_width < img_px_width:
                status_message = (
                    "WARNING/ERROR\n"
                    " >>> Image ratio missmatch; Image width is too small "
                    "after fitting to height.\n"
                    " >>> Please crop it manually with an image editor of "
                    "your choice and run again!"
                )
            else:
                status_message = "OK"
            # center image horizontally by cropping it on the left side
            crop_left = (img_width - img_px_width) // 2
            crop_top = 0
            crop_right = (img_width + img_px_width) // 2 + 20  # overlapping
            crop_bottom = img_height
            crop_box = (crop_left, crop_top, crop_right, crop_bottom)
            img = img.crop(crop_box)
            # paste image in kachel
            kachel_out.paste(img, (img_pos_x, img_pos_y))
            # print status
            print(
                "Process {:>2} (h:{:>2}|v:{:>2}): {} ".format(
                    img_i + 1, i_h + 1, i_v + 1, os.path.basename(img_filepath)
                ).ljust(60, ".")
                + " "
                + status_message
            )

    # store kachel as jpg file
    now = datetime.now()
    date_now = now.strftime("%Y%m%d")
    kachel_out_filename_base = "{}__{}".format(date_now, KACHEL_OUTPUT_FILENAME)
    # store high resolution
    kachel_out_filepath_high = os.path.abspath(
        os.path.join(KACHEL_OUTPUT_FOLDER, kachel_out_filename_base + ".jpg")
    )
    kachel_out.save(kachel_out_filepath_high, quality=KACHEL_JPG_QUALITY)
    # resize and store low resultion
    kachel_out.thumbnail(
        (KACHEL_IMG_SIZE_OUT_LOW, KACHEL_IMG_SIZE_OUT_LOW), Image.ANTIALIAS
    )
    kachel_out_filepath_low = os.path.abspath(
        os.path.join(KACHEL_OUTPUT_FOLDER, kachel_out_filename_base + "--SMALL.jpg")
    )
    kachel_out.save(kachel_out_filepath_low, quality=KACHEL_JPG_QUALITY)
    # open and print high resultion
    current_platform = platform.system()
    if current_platform == "Windows":
        os.startfile(kachel_out_filepath_high)
    elif current_platform == "Darwin":  # macOS
        subprocess.call(("open", kachel_out_filepath_high))
    elif current_platform == "Linux":
        subprocess.call(("xdg-open", kachel_out_filepath_high))
    else:
        raise NotImplementedError
    print()
    print("Finished! >>>", kachel_out_filepath_high)
    print()
