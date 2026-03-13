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
from collections import OrderedDict, defaultdict, namedtuple
from typing import Any
from xml.etree.ElementTree import parse as ET_parse

import numpy as np

FrameBox = namedtuple("FrameBox", ["xtl", "ytl", "xbr", "ybr", "outside", "rotation"])

FrameInfo = namedtuple("FrameInfo", ["frame_id", "frame_box"])


Track = namedtuple("Track", ["task_id", "track_id", "frames"])


def merge_tracks(relations):
    """
    Merge tracks from different sequences to one sequence.
    Input -  Array of single tracks in one video.
    Output - multiple tracks in one video

    :param relations: Array of tracks
    """
    result = {}

    items = list(relations.items())
    while items:
        key, values = items.pop(0)
        merged_key = key
        merged_values = set(values)

        i = 0
        while i < len(items):
            other_key, other_values = items[i]

            if (
                merged_key == other_key
                or merged_key in other_values
                or other_key in merged_values
                or any(v in merged_values for v in other_values)
                or any(v in other_values for v in merged_values)
            ):

                merged_values.update(other_values)
                merged_values.add(other_key)
                items.pop(i)
            else:
                i += 1

        result[merged_key] = set(sorted(list(merged_values)))

    return result


def read_track(track: Track):
    """
    Get frame ranges and box ranges of selected object

    :param track: Description
    :type track: Track
    :return frange, brange - frame ranges and box ranges. -1 if no Box
    """
    frange = []
    brange = []

    for fr in track.frames:
        frange.append(fr.frame_id)
        brange.append(
            np.floor(
                np.array(
                    [
                        fr.frame_box.xtl,
                        fr.frame_box.ytl,
                        fr.frame_box.xbr,
                        fr.frame_box.ybr,
                        fr.frame_box.outside,
                        fr.frame_box.rotation,
                    ]
                )
            ).astype(np.int32)
        )
    return np.array(frange), np.array(brange)


def find_intersections(tracks: list[Track]):

    frame_to_tracks = defaultdict(list)

    for tidx, track in enumerate(tracks):
        for frame_info in track.frames:
            frame_to_tracks[str(track.task_id) + "_" + str(frame_info.frame_id)].append((tidx, len(track.frames)))

    minimize_keys = []
    for k, v in frame_to_tracks.items():
        if len(v) == 1:
            minimize_keys.append(k)
    singleton_tracks = []
    tmp_singleton_tumors = set()

    for k in minimize_keys:
        v = frame_to_tracks.pop(k)[0]
        singleton_tracks.append(v)
        tmp_singleton_tumors.add(v[0])

    tmp_multiple_tumors = set()
    intersected_tracks = defaultdict(set)
    for mulv in frame_to_tracks.values():
        tmp_multiple_tumors.add(mulv[0][0])
        mutual_keys = []
        for v in mulv[1:]:
            intersected_tracks[mulv[0][0]].add(v[0])
            if v[0] not in intersected_tracks:
                mutual_keys.append(v[0])
            tmp_multiple_tumors.add(v[0])
    intersected_tracks = merge_tracks(intersected_tracks)

    singleton_tumors = tmp_singleton_tumors - tmp_multiple_tumors

    # Create output
    track_boxes_map = OrderedDict()
    for k, v in intersected_tracks.items():
        frame_ranges = []
        boxes_frames = []
        track_ids_ranges = [tracks[k].track_id]
        frange, brange = read_track(tracks[k])
        boxes_frames.append(brange)
        frame_ranges.append(frange)

        for kv in v:
            frange, brange = read_track(tracks[kv])
            track_ids_ranges.append(tracks[kv].track_id)
            boxes_frames.append(brange)
            frame_ranges.append(frange)

        result_boxs = []
        minitem = np.min([ar[0] for ar in frame_ranges])
        maxlen = np.max([np.max(ar - minitem) for ar in frame_ranges]) + 1

        for fr, brange in zip(frame_ranges, boxes_frames):
            tmp = [-1 for _ in range(maxlen)]
            for bidx, bval in enumerate(fr - minitem):
                tmp[bval] = brange[bidx]
            result_boxs.append(tmp)

        track_boxes_map[k] = {
            "videoname": tracks[k].task_id,
            "frame_start": minitem,
            "boxes": result_boxs,
            "track_ids": track_ids_ranges,
        }

    for singleton_track in singleton_tumors:
        frange, brange = read_track(tracks[singleton_track])

        result_boxs = []
        minitem = frange[0]
        maxlen = np.max(frange - minitem) + 1

        result_boxs = [-1 for _ in range(maxlen)]

        for bidx, bval in enumerate(frange - minitem):
            result_boxs[bval] = brange[bidx]

        track_boxes_map[singleton_track] = {
            "videoname": tracks[singleton_track].task_id,
            "frame_start": minitem,
            "boxes": [result_boxs],
            "track_ids": [tracks[singleton_track].track_id],
        }

    return track_boxes_map


class SechenovCystoscopyDataset:
    def __init__(self, root: str, ext: str = ".mp4", sanity_mode: bool = False, sanity_size: int = 4):
        """
        :param root: path to dataset directory
        :type root: str
        :param ext: extensions of videofile
        :type ext: str
        :param sanity_mode: Return only `sanity_size` first tracks
        :type sanity_mode: bool
        :param sanity_size: Size of sanity mode batch
        :type sanity_size: bool
        """
        super().__init__()
        self.root = root
        self.ext = ext
        self.sanity_mode = sanity_mode
        self.sanity_size = sanity_size
        videos_dir = "videos"

        if not os.path.isdir(os.path.join(root, videos_dir)):
            raise RuntimeError("Dataset video dir not found or corrupted.")

        videos_dir = os.path.join(root, videos_dir)

        self.images = [os.path.join(videos_dir, x) for x in filter(lambda x: x[-4:] == ext, os.listdir(videos_dir))]

        rootxml = ET_parse(f"{self.root}/annotations.xml").getroot()
        tracks = []
        for track in list(rootxml):
            if track.tag == "track":
                frames = []
                if track.get("label") == "tumor":
                    for box in list(track):
                        frames.append(
                            FrameInfo(
                                int(box.get("frame")),
                                FrameBox(
                                    float(box.get("xtl", -1)),
                                    float(box.get("ytl", -1)),
                                    float(box.get("xbr", -1)),
                                    float(box.get("ybr", -1)),
                                    bool(int(box.get("outside", 1))),
                                    float(box.get("rotation", 0.0)),
                                ),
                            )
                        )
                    tracks.append(Track(str(track.get("task_id")), int(track.get("id")), frames))
        self.tracks_map = find_intersections(tracks)

    def __len__(self) -> int:
        return len(self.tracks_map) if not self.sanity_mode else self.sanity_size

    @property
    def annotations(self) -> list[str]:
        return self.targets

    def __getitem__(self, index: int) -> tuple[str, Any]:
        key = list(self.tracks_map.keys())[index]
        return self.tracks_map[key]["videoname"], self.tracks_map[key]
