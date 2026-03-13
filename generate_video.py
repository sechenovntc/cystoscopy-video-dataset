# Copyright (c) 2026 Chernenkiy Ivan, Sechenov University

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import cv2
import numpy as np

from utils import SechenovCystoscopyDataset

DATASET_DIR = "archive"
OUTPUT_DIR = "gen"

os.makedirs(OUTPUT_DIR, exist_ok=True)
ds = SechenovCystoscopyDataset(DATASET_DIR)
for item in ds:
    videoname, track = item
    bbox_idx = 0
    src_video = f"{ds.root}/videos/{videoname}.mp4"
    cap = cv2.VideoCapture(src_video)
    cur_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cur_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    cur_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cur_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    src_frames = track["frame_start"]

    # Jump to sequence start
    cap.set(cv2.CAP_PROP_POS_FRAMES, src_frames)

    output = cv2.VideoWriter(
        f"{OUTPUT_DIR}/{videoname}_mark.mp4", cv2.VideoWriter_fourcc(*"mp4v"), cur_frame_rate, (cur_width, cur_height)
    )

    res = True
    while res and bbox_idx < len(track["boxes"][0]):
        res, frame = cap.read()
        if not res:
            print("CANTREAD!!!!")
            break
        frame_id = int(cap.get(1))  # get current frame ID

        if frame_id >= src_frames:
            for bbox_item_idx in range(len(track["boxes"])):
                bbox = track["boxes"][bbox_item_idx][bbox_idx]
                if not isinstance(bbox, int):
                    is_outside = bbox[4]
                    if not is_outside:
                        rotated_rect = cv2.RotatedRect(
                            (bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2),
                            (float(bbox[2] - bbox[0]), float(bbox[3] - bbox[1])),
                            float(bbox[5]),
                        )

                        # Get the four vertices of the rectangle
                        box_points = cv2.boxPoints(rotated_rect).astype(np.int32)
                        cv2.putText(
                            frame,
                            "tumor",
                            (box_points[1][0], box_points[1][1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2,
                        )
                        frame = cv2.drawContours(frame, [box_points], 0, (255, 0, 0), 2)
            output.write(frame)
            bbox_idx += 1
    output.release()
    cap.release()
