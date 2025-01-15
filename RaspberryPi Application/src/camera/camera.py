from picamera2 import Picamera2
from PIL import Image
import io

class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_video_configuration(
            # main={"size": (720, 480)},
            main={"size": (640, 360)},
            controls={"FrameRate": 24}
        )
        self.picam2.configure(camera_config)
        self.picam2.start()

    def generate_frames(self):
        while True:
            frame = self.picam2.capture_array("main")
            image = Image.fromarray(frame)
            if image.mode == "RGBA":
                image = image.convert("RGB")
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=100)
            jpeg_data = buffer.getvalue()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n')