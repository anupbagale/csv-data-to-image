import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from csv_image import array_to_csv, array_to_image, csv_to_array, image_to_array, main  # noqa: E402

rng = np.random.default_rng(0)


@pytest.mark.parametrize("shape", [(40, 30), (40, 30, 3), (40, 30, 4), (1, 5)])
def test_round_trip_is_lossless(tmp_path, shape):
    image = rng.integers(0, 256, shape, dtype=np.uint8)
    path = tmp_path / "image.csv"
    array_to_csv(image, path)
    restored = csv_to_array(path)
    assert restored.dtype == np.uint8
    assert np.array_equal(restored, image)


def test_csv_layout(tmp_path):
    image = np.array([[[1, 2, 3], [4, 5, 6]]], dtype=np.uint8)
    path = tmp_path / "rgb.csv"
    array_to_csv(image, path)
    assert path.read_text().splitlines() == ["# shape: 1,2,3", "1,2,3,4,5,6"]


def test_plain_csv_without_header_is_grayscale(tmp_path):
    path = tmp_path / "plain.csv"
    path.write_text("0,128,255\n10,20,30\n")
    assert np.array_equal(csv_to_array(path), [[0, 128, 255], [10, 20, 30]])


def test_rejects_values_out_of_range(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("0,300\n")
    with pytest.raises(ValueError):
        csv_to_array(path)


def test_rejects_non_uint8(tmp_path):
    with pytest.raises(ValueError):
        array_to_csv(np.zeros((2, 2), dtype=float), tmp_path / "x.csv")


def test_colour_order_survives_image_files(tmp_path):
    """Pure red must stay red after PNG -> CSV -> PNG, despite OpenCV using BGR internally."""
    red = np.zeros((4, 4, 3), dtype=np.uint8)
    red[..., 0] = 255
    png = tmp_path / "red.png"
    array_to_image(red, str(png))
    assert np.array_equal(image_to_array(str(png)), red)

    csv = tmp_path / "red.csv"
    out = tmp_path / "out.png"
    main(["to-csv", str(png), str(csv)])
    assert csv.read_text().splitlines()[1].startswith("255,0,0")
    main(["to-image", str(csv), str(out)])
    assert np.array_equal(image_to_array(str(out)), red)


def test_command_line_gray(tmp_path):
    png = tmp_path / "in.png"
    array_to_image(rng.integers(0, 256, (8, 8, 3), dtype=np.uint8), str(png))
    csv = tmp_path / "gray.csv"
    main(["to-csv", str(png), str(csv), "--gray"])
    assert csv_to_array(csv).shape == (8, 8)
