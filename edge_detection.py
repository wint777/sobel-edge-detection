"""Sobel 에지 검출 모듈.

사용법 (CLI):
    python edge_detection.py input.jpg output.png
"""
import sys

import cv2
import numpy as np

VALID_KSIZES = (1, 3, 5, 7)


def sobel_edge_detection(image_bytes: bytes, ksize: int = 3) -> bytes:
    """Take encoded image bytes (JPEG/PNG/BMP/WEBP etc.), return PNG-encoded bytes of the Sobel edge magnitude image (grayscale, uint8, normalized 0-255)."""
    if ksize not in VALID_KSIZES:
        raise ValueError(f"ksize는 {VALID_KSIZES} 중 하나여야 합니다 (입력값: {ksize!r})")
    if not image_bytes:
        raise ValueError("이미지 데이터가 비어 있습니다.")

    # 바이트 -> 이미지 디코딩
    img = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("이미지를 디코딩할 수 없습니다. 지원되는 이미지 파일인지 확인하세요.")

    # 그레이스케일 변환 + 노이즈 감소를 위한 가벼운 블러
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # x, y 방향 기울기 (음수 값 보존을 위해 CV_64F 사용)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)

    # 기울기 크기 계산 후 0~255로 정규화
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    edges = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    ok, buf = cv2.imencode(".png", edges)
    if not ok:
        raise ValueError("PNG 인코딩에 실패했습니다.")
    return buf.tobytes()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("사용법: python edge_detection.py input.jpg output.png", file=sys.stderr)
        return 1
    src, dst = argv
    with open(src, "rb") as f:
        result = sobel_edge_detection(f.read())
    with open(dst, "wb") as f:
        f.write(result)
    print(f"저장 완료: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
