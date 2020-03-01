import ctypes
if __name__ == "__main__":
    tmp_cv = ctypes.CDLL('./libopencv_imgproc420.dll')
    tmp_cv.matchTemplate()
    print(123)