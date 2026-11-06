# убирает вшитый титр «Идеально это:» (белые буквы) из кадра, без цветокоррекции
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1])
y0, y1, x0, x1 = 1040, 1150, 280, 800
band = im[y0:y1, x0:x1]
hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
mask = ((hsv[..., 2] > 215) & (hsv[..., 1] < 50)).astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((11, 11), np.uint8))
full = np.zeros(im.shape[:2], np.uint8); full[y0:y1, x0:x1] = mask
cv2.imwrite(sys.argv[2], cv2.inpaint(im, full, 9, cv2.INPAINT_TELEA), [cv2.IMWRITE_JPEG_QUALITY, 96])
