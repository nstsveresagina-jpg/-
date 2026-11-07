# Естественная ретушь лиц + единый мягкий фильтр.
# Лицо размечается MediaPipe Face Landmarker (Apache-2.0); сглаживается только кожа,
# глаза, брови, губы и ноздри не трогаются, мелкая текстура кожи возвращается обратно.
import cv2, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

# индексы контуров сетки лица MediaPipe
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
L_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
R_EYE = [263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390, 249]
L_BROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
R_BROW = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
LIPS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
NOSTRILS = [[98, 97, 2, 326, 327, 294, 278, 344, 440, 275, 4, 45, 220, 115, 48, 64]]
UNDER_L = [[33, 7, 163, 144, 145, 153, 154, 155, 133, 243, 112, 26, 22, 23, 24, 110, 25, 130]]
UNDER_R = [[263, 249, 390, 373, 374, 380, 381, 382, 362, 463, 341, 256, 252, 253, 254, 339, 255, 359]]


class Retoucher:
    def __init__(self, model, video=True):
        opts = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model),
            running_mode=vision.RunningMode.VIDEO if video else vision.RunningMode.IMAGE,
            num_faces=3, min_face_detection_confidence=0.4, min_face_presence_confidence=0.4, min_tracking_confidence=0.4)
        self.lm = vision.FaceLandmarker.create_from_options(opts)
        self.video = video

    def faces(self, rgb, ts_ms=0):
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        r = self.lm.detect_for_video(img, ts_ms) if self.video else self.lm.detect(img)
        h, w = rgb.shape[:2]
        cur = [np.array([[p.x * w, p.y * h] for p in f]) for f in r.face_landmarks]
        # сглаживание разметки между кадрами, чтобы маска не дрожала (сброс на склейке/скачке)
        prev = getattr(self, '_prev', [])
        out = []
        for f in cur:
            c = f.mean(0); best = None
            for q in prev:
                if np.linalg.norm(q.mean(0) - c) < (np.ptp(f[:, 0]) * 0.25): best = q
            out.append(f if best is None else best * 0.45 + f * 0.55)
        self._prev = out
        return out

    @staticmethod
    def poly(mask, pts, idx, val, grow=1.0):
        p = pts[idx]
        if grow != 1.0:
            c = p.mean(0); p = c + (p - c) * grow
        cv2.fillPoly(mask, [p.astype(np.int32)], val)

    def retouch(self, rgb, ts_ms=0, strength=None):
        out = rgb.astype(np.float32)
        for pts in self.faces(rgb, ts_ms):
            x0, y0 = pts.min(0); x1, y1 = pts.max(0)
            fw = x1 - x0
            if fw < 40: continue
            pad = int(fw * 0.35)
            H, W = rgb.shape[:2]
            ax, ay, bx, by = max(0, int(x0) - pad), max(0, int(y0) - pad), min(W, int(x1) + pad), min(H, int(y1) + pad)
            roi = out[ay:by, ax:bx]; p = pts - [ax, ay]
            m = np.zeros(roi.shape[:2], np.float32)
            self.poly(m, p, OVAL, 1.0, 0.97)
            for idx, g in ((L_EYE, 1.5), (R_EYE, 1.5), (L_BROW, 1.25), (R_BROW, 1.25), (LIPS, 1.12)):
                self.poly(m, p, idx, 0.0, g)
            k = max(3, int(fw * 0.06) | 1)
            m = cv2.GaussianBlur(m, (k * 2 + 1, k * 2 + 1), 0)
            # сила: тёмные волосы над лбом -> героиня в чёрном, ей ретушь сильнее
            fx, fy = int(p[10][0]), int(max(0, p[10][1] - fw * 0.18))
            hair = roi[max(0, fy - 6):fy + 6, max(0, fx - 20):fx + 20].mean() if fy > 6 else 128
            s = strength if strength is not None else (0.5 if hair < 75 else 0.32)
            # частотное разделение: убираем неровности средней частоты, мелкую текстуру возвращаем
            u8 = np.clip(roi, 0, 255).astype(np.uint8)
            d = max(5, int(fw * 0.035))
            smooth = cv2.bilateralFilter(u8, d * 2 + 1, 22, d).astype(np.float32)
            smooth = cv2.bilateralFilter(smooth.astype(np.uint8), d + 1, 16, d).astype(np.float32)
            fine = roi - cv2.GaussianBlur(roi, (0, 0), max(0.8, fw / 420))
            soft = smooth + fine * 0.8
            # чуть осветляем зону под глазами (тени), очень мягко
            ue = np.zeros_like(m)
            for idx in (UNDER_L[0], UNDER_R[0]):
                self.poly(ue, p, idx, 1.0, 1.0)
            ue = cv2.GaussianBlur(ue, (k * 4 + 1, k * 4 + 1), 0) * m
            lum = cv2.GaussianBlur(roi.mean(2), (0, 0), fw / 30)
            soft += (ue * np.clip(lum.mean() - lum, 0, 40) * 0.2)[..., None]
            a = (m * s)[..., None]
            roi[:] = roi * (1 - a) + soft * a
        return np.clip(out, 0, 255).astype(np.uint8)


def make_grade():
    """Единый мягкий фильтр: тёплый нейтральный баланс, мягкая S-кривая, чуть приглушённые цвета."""
    x = np.arange(256, dtype=np.float32) / 255
    s = x + 0.06 * np.sin(2 * np.pi * (x - 0.5)) * -1 * (x * (1 - x)) * 4  # мягкий контраст
    s = 0.02 + s * 0.975                                                    # слегка приподнятые тени
    r = np.clip((s * 1.015) * 255, 0, 255); g = np.clip(s * 255, 0, 255); b = np.clip((s * 0.975) * 255, 0, 255)
    return np.stack([r, g, b], 1).astype(np.float32)


def apply_grade(rgb, lut, gains, sat=0.94):
    f = rgb.astype(np.float32) * gains
    f = np.clip(f, 0, 255).astype(np.uint8)
    o = np.empty_like(f, dtype=np.float32)
    for c in range(3): o[..., c] = lut[f[..., c], c]
    y = o @ np.array([0.299, 0.587, 0.114], np.float32)
    o = y[..., None] + (o - y[..., None]) * sat
    return np.clip(o, 0, 255).astype(np.uint8)
