import os
import subprocess
import time
import cv2
import pandas as pd


def measure_video_quality(compressed_dir, original_dir):
    results = []
    for compressed_file in os.listdir(compressed_dir):
        if compressed_file.endswith(".mp4"):
            compressed_path = os.path.join(compressed_dir, compressed_file)
            original_path = os.path.join(original_dir, compressed_file)
            # Measure video length
            video_length = get_video_length(compressed_path)
            # Measure file size
            file_size = os.path.getsize(compressed_path)
            # Measure resolution and average RGB values
            resolution, avg_rgb = get_video_resolution_and_rgb(compressed_path)
            # Measure bit depth and bit rate
            bit_depth, bit_rate = get_bit_depth_and_bit_rate(compressed_path)
            # Measure frame rate
            frame_rate = get_frame_rate(compressed_path)
            # Measure PSNR and SSIM
            psnr = get_psnr(compressed_path, original_path)
            ssim = get_ssim(compressed_path, original_path)
            # Get encoding command function based on directory
            dir_name = os.path.basename(compressed_dir)
            command_func = encoding_commands[dir_name]
            # Measure encoding time
            encoding_time = measure_encoding_time(
                original_path, compressed_path, command_func
            )

            results.append(
                {
                    "file_name": compressed_file,
                    "video_length": video_length,
                    "file_size": file_size,
                    "resolution": resolution,
                    "avg_rgb": avg_rgb,
                    "bit_depth": bit_depth,
                    "bit_rate": bit_rate,
                    "frame_rate": frame_rate,
                    "psnr": psnr,
                    "ssim": ssim,
                    "encoding_time": encoding_time,
                }
            )

    df = pd.DataFrame(results)
    return df


def get_video_length(video_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        video_length = float(result.stdout.strip())
    except ValueError:
        video_length = None
    return video_length


def get_video_resolution_and_rgb(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    resolution = (width, height)

    avg_rgb = None
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            avg_rgb = cv2.mean(frame)[:3]
    cap.release()

    return resolution, avg_rgb


def get_bit_depth_and_bit_rate(video_path):
    result_bit_depth = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=bits_per_raw_sample",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    print(result_bit_depth.stdout.strip())
    bit_depth = (
        int(result_bit_depth.stdout.strip())
        if result_bit_depth.stdout.strip().isdigit()
        else None
    )

    result_bit_rate = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=bit_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    bit_rate = (
        int(result_bit_rate.stdout.strip())
        if result_bit_rate.stdout.strip().isdigit()
        else None
    )

    return bit_depth, bit_rate


def get_frame_rate(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    return frame_rate


def get_psnr(compressed_video, original_video):
    result_psnr = subprocess.run(
        [
            "ffmpeg",
            "-i",
            compressed_video,
            "-i",
            original_video,
            "-filter_complex",
            "psnr",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    psnr_line = [line for line in result_psnr.stderr.split("\n") if "PSNR" in line][-1]

    psnr_value_str = psnr_line.split(" ")[-3]

    psnr_value_str_no_units = psnr_value_str.split(":")[1]
    psnr_value_float = float(psnr_value_str_no_units)

    return psnr_value_float


def get_ssim(compressed_video, original_video):
    result_ssim = subprocess.run(
        [
            "ffmpeg",
            "-i",
            compressed_video,
            "-i",
            original_video,
            "-filter_complex",
            "ssim",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    ssim_line = [line for line in result_ssim.stderr.split("\n") if "SSIM" in line][-1]
    # print("1.", ssim_line)
    ssim_value_str = ssim_line.split(" ")[-2]
    ssim_value_str_no_units = ssim_value_str.split(":")[1]
    # print("2. ", ssim_value_str_no_units)
    ssim_value_float = float(ssim_value_str_no_units)

    return ssim_value_float


def measure_encoding_time(original_path, compressed_path, command_func):
    start_time = time.time()
    command = command_func(original_path, compressed_path)
    subprocess.run(command, capture_output=True, text=True)
    end_time = time.time()
    encoding_time = end_time - start_time
    os.remove(compressed_path + ".tmp.mp4")

    return encoding_time


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


encoding_commands = {
    "base_264_cmd": base_264_cmd,
    "base_265_cmd": base_265_cmd,
    "crf51_264_cmd": crf51_264_cmd,
    "crf51_265_cmd": crf51_265_cmd,
    "fastdecode_264_cmd": fastdecode_264_cmd,
    "fastdecode_265_cmd": fastdecode_265_cmd,
    "grain_264_cmd": grain_264_cmd,
    "grain_265_cmd": grain_265_cmd,
    "slow_264_cmd": slow_264_cmd,
    "slow_265_cmd": slow_265_cmd,
    "veryfast_264_cmd": veryfast_264_cmd,
    "veryfast_265_cmd": veryfast_265_cmd,
    "veryslow_264_cmd": veryslow_264_cmd,
    "veryslow_265_cmd": veryslow_265_cmd,
    "zerolatency_264_cmd": zerolatency_264_cmd,
    "zerolatency_265_cmd": zerolatency_265_cmd,
}
if __name__ == "__main__":
    compressed_directory_list = [
        "/home/shashank/Projects/Research-temp/compressed/base_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/base_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/crf51_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/crf51_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/fastdecode_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/fastdecode_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/grain_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/grain_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/slow_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/slow_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/veryfast_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/veryfast_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/veryslow_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/veryslow_265_cmd",
        "/home/shashank/Projects/Research-temp/compressed/zerolatency_264_cmd",
        "/home/shashank/Projects/Research-temp/compressed/zerolatency_265_cmd",
    ]
    fn_list = []
    og_directory = "/home/shashank/Projects/Research-temp/videos"
    for directory in compressed_directory_list:
        print("processing", directory.split("/")[-1])
        df = measure_video_quality(directory, og_directory)
        print(df)
        df.to_csv(f"csvfiles/{directory.split('/')[-1]}.csv", index=False)
