import os
import subprocess
import time
import cv2
import pandas as pd


# Command returners based on presets used
def base_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def base_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def crf51_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-crf",
        "51",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def crf51_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-crf",
        "51",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def fastdecode_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "fastdecode",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def fastdecode_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "fastdecode",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def grain_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "grain",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def grain_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "grain",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def slow_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "slow",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def slow_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "slow",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def veryfast_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "veryfast",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def veryfast_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "veryfast",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def veryslow_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "veryslow",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def veryslow_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-preset",
        "veryslow",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def zerolatency_265_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx265",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "zerolatency",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


def zerolatency_264_cmd(original_path, compressed_path):
    return [
        "ffmpeg",
        "-i",
        original_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=in_range=full:out_range=tv",
        "-color_range",
        "tv",
        "-tune",
        "zerolatency",
        "-movflags",
        "+faststart",
        compressed_path + ".tmp.mp4",
    ]


functions = [
    base_264_cmd,
    base_265_cmd,
    crf51_264_cmd,
    crf51_265_cmd,
    fastdecode_264_cmd,
    fastdecode_265_cmd,
    grain_264_cmd,
    grain_265_cmd,
    slow_264_cmd,
    slow_265_cmd,
    veryfast_264_cmd,
    veryfast_265_cmd,
    veryslow_264_cmd,
    veryslow_265_cmd,
    zerolatency_264_cmd,
    zerolatency_265_cmd,
]

# Directory with your videos
video_dir = "/home/shashank/Projects/Research-temp/videos"
compressed_dir = "/home/shashank/Projects/Research-temp/compressed"

# Iterate over each video in the directory
for video in os.listdir(video_dir):
    if video.endswith(".mp4"):  # or whatever your video format is
        original_path = os.path.join(video_dir, video)

        # Apply each function to the video
        for function in functions:
            # Create a directory for this function if it doesn't exist
            dir_path = os.path.join(compressed_dir, function.__name__)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # Compress the video using this function
            compressed_path = os.path.join(dir_path, video)
            cmd = function(original_path, compressed_path)

            # Run the command and wait for it to complete
            process = subprocess.run(cmd, check=True)

            # Rename the temporary file to the final file name
            os.rename(compressed_path + ".tmp.mp4", compressed_path)
