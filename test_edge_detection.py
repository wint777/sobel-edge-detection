import os

import cv2
import numpy as np
import pytest

from edge_detection import sobel_edge_detection

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _decode(png_bytes):
    return cv2.imdecode(np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_UNCHANGED)


def _square_image():
    # 흰 배경(100x100) 위의 검은 사각형(30~69)
    img = np.full((100, 100, 3), 255, np.uint8)
    img[30:70, 30:70] = 0
    ok, buf = cv2.imencode(".png", img)
    return buf.tobytes()


def test_valid_image_returns_png_of_same_size():
    path = os.path.join(HERE, "img.jpg")
    if not os.path.exists(path):
        pytest.skip("img.jpg 없음")
    with open(path, "rb") as f:
        data = f.read()
    src = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    out = sobel_edge_detection(data)
    assert out.startswith(PNG_SIGNATURE)
    edges = _decode(out)
    assert edges.ndim == 2 and edges.dtype == np.uint8
    assert edges.shape == src.shape[:2]
    assert edges.max() > 0


def test_synthetic_square_edges():
    edges = _decode(sobel_edge_detection(_square_image()))
    assert edges.shape == (100, 100)
    # 경계에는 강한 에지
    assert edges[50, 29:31].max() > 200
    assert edges[29:31, 50].max() > 200
    # 평탄한 영역(사각형 내부, 바깥 배경)은 ~0
    assert edges[40:60, 40:60].max() < 5
    assert edges[0:15, 0:15].max() < 5
    assert edges[85:100, 85:100].max() < 5


@pytest.mark.parametrize("k", [1, 3, 5, 7])
def test_all_valid_ksizes(k):
    edges = _decode(sobel_edge_detection(_square_image(), ksize=k))
    assert edges.shape == (100, 100) and edges.max() == 255


def test_empty_bytes_raises():
    with pytest.raises(ValueError):
        sobel_edge_detection(b"")


def test_garbage_bytes_raises():
    with pytest.raises(ValueError):
        sobel_edge_detection(b"this is not an image at all" * 10)


@pytest.mark.parametrize("k", [0, 2, 4, 9, -1])
def test_invalid_ksize_raises(k):
    with pytest.raises(ValueError):
        sobel_edge_detection(_square_image(), ksize=k)
