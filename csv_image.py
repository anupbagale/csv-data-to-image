"""Convert images to CSV files of pixel values and back.

Each row of the image becomes one line of the CSV file. Grayscale images give one
number per pixel. Colour images give one number per channel, so a row of an RGB image
is written as r, g, b, r, g, b, ... from left to right.

The first line of the file is a comment with the image shape, for example
``# shape: 512,512,3``. It is needed to turn the numbers back into a colour image.
Files without this line are read as grayscale.

Command line use:

    python csv_image.py to-csv photo.png photo.csv
    python csv_image.py to-image photo.csv restored.png
"""

import argparse
import sys

import cv2
import numpy as np


def image_to_array(path):
    """Read an image file. Colour images are returned in RGB (or RGBA) order."""
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"could not read image: {path}")
    if image.ndim == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
    return image


def array_to_image(image, path):
    """Write an RGB, RGBA or grayscale array to an image file."""
    if image.ndim == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
    if not cv2.imwrite(path, image):
        raise OSError(f"could not write image: {path}")


def array_to_csv(image, path):
    """Save an image array (H x W or H x W x C, uint8) as a CSV file."""
    image = np.asarray(image)
    if image.dtype != np.uint8:
        raise ValueError("only 8-bit images (dtype uint8) are supported")
    if image.ndim not in (2, 3):
        raise ValueError("expected an array of shape (H, W) or (H, W, C)")
    rows = image.reshape(image.shape[0], -1)
    shape = ",".join(str(n) for n in image.shape)
    np.savetxt(path, rows, fmt="%d", delimiter=",", header=f"shape: {shape}", comments="# ")


def csv_to_array(path):
    """Read a CSV file written by array_to_csv (or a plain grayscale CSV) into a uint8 array."""
    shape = None
    with open(path) as f:
        first = f.readline()
    if first.startswith("#") and "shape:" in first:
        shape = tuple(int(n) for n in first.split("shape:")[1].split(","))

    values = np.loadtxt(path, delimiter=",", comments="#", ndmin=2)
    if values.min() < 0 or values.max() > 255:
        raise ValueError("pixel values must be between 0 and 255")
    values = values.astype(np.uint8)
    return values.reshape(shape) if shape else values


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert images to CSV files of pixel values and back.")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("to-csv", help="image file -> CSV")
    a.add_argument("image")
    a.add_argument("csv")
    a.add_argument("--gray", action="store_true", help="convert to grayscale first")
    b = sub.add_parser("to-image", help="CSV -> image file")
    b.add_argument("csv")
    b.add_argument("image")
    args = parser.parse_args(argv)

    if args.command == "to-csv":
        image = image_to_array(args.image)
        if args.gray and image.ndim == 3:
            image = cv2.cvtColor(image[..., :3], cv2.COLOR_RGB2GRAY)
        array_to_csv(image, args.csv)
        print(f"{args.image} {image.shape} -> {args.csv}")
    else:
        image = csv_to_array(args.csv)
        array_to_image(image, args.image)
        print(f"{args.csv} {image.shape} -> {args.image}")


if __name__ == "__main__":
    sys.exit(main())
