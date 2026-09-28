"""Flask web server: upload an image, download its Sobel edge detection result."""
import io
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from edge_detection import sobel_edge_detection

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}
MAX_UPLOAD_MB = 10

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(_e):
    return _error(f"파일이 너무 큽니다. 최대 {MAX_UPLOAD_MB}MB까지 업로드할 수 있습니다.", 413)


@app.get("/")
def index():
    return render_template("index.html", max_mb=MAX_UPLOAD_MB)


@app.get("/healthz")
def healthz():
    return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.post("/api/edge")
def edge():
    file = request.files.get("image")
    if file is None or not file.filename:
        return _error("이미지 파일을 선택해 주세요.", 400)
    if not _allowed(file.filename):
        return _error("지원하지 않는 파일 형식입니다. (png, jpg, jpeg, bmp, webp)", 400)

    ksize_raw = request.form.get("ksize", "3").strip() or "3"
    try:
        ksize = int(ksize_raw)
    except ValueError:
        return _error("ksize는 정수여야 합니다. (1, 3, 5, 7)", 400)

    image_bytes = file.read()  # in memory only; never written to disk
    if not image_bytes:
        return _error("빈 파일입니다.", 400)

    try:
        png_bytes = sobel_edge_detection(image_bytes, ksize=ksize)
    except ValueError as e:
        return _error(str(e) or "이미지를 처리할 수 없습니다.", 400)

    stem = secure_filename(Path(file.filename).stem) or "image"
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name=f"{stem}_sobel.png",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
