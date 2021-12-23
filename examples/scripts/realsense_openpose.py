import logging
import sys
import time
import math
import cv2
import numpy as np
from openpose import pyopenpose as op
import pyrealsense2.pyrealsense2 as rs


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)


if __name__ == '__main__':
    fps_time = 0

    params = dict()
    params["model_folder"] = "../../models/"

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()


    print("OpenPose start")
    pipeline.start(config)

        # Convert images to numpy arrays
    
    count = 0
    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            dst = np.asanyarray(color_frame.get_data())
            #dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
            #cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", dst)
            #continue

            datum = op.Datum()
            datum.cvInputData = dst
            opWrapper.emplaceAndPop([datum])
            fps = 1.0 / (time.time() - fps_time)
            fps_time = time.time()
            newImage = datum.cvOutputData[:, :, :]
            cv2.putText(newImage , "FPS: %f" % (fps), (20, 40),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # out_video.write(newImage)

            print("captured fps %f"%(fps))
            cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", newImage)
            count += 1

    finally:

        # Stop streaming
        pipeline.stop()