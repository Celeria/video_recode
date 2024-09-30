# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 22:26:30 2024

@author: patm3
"""

import os
import subprocess
import re
import json

def fix_outputs(original_output_directory, fixed_output_directory):
    os.makedirs(fixed_output_directory, exist_ok=True)

    for filename in os.listdir(original_output_directory):
        if filename.endswith(".mp4"):
            original_filepath = os.path.join(original_output_directory, filename)

            # Read total duration from the text file
            text_file_name = filename.replace(".mp4", ".txt")
            text_file_path = os.path.join(original_output_directory, text_file_name)
            with open(text_file_path, 'r') as f:
                first_line = f.readline().strip()
                total_duration_str = first_line.split(": ")[1]
                minutes, seconds = total_duration_str.split(" minutes ")
                total_duration_seconds = int(minutes) * 60 + float(seconds)

            # Fix metadata using ffmpeg, setting the correct duration
            fixed_video_path = os.path.join(fixed_output_directory, filename) 

            # Use ffprobe to get metadata from the original video
            result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                                     '-show_streams', original_filepath],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            probe_data = json.loads(result.stdout)
            video_stream = next(
                (stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next(
                (stream for stream in probe_data['streams'] if stream['codec_type'] == 'audio'), None)

            # Build the ffmpeg command to copy streams and set duration
            ffmpeg_command = ['ffmpeg', '-i', original_filepath]

            if video_stream:
                ffmpeg_command.extend(['-c:v', 'copy'])
            if audio_stream:
                ffmpeg_command.extend(['-c:a', 'copy'])

            ffmpeg_command.extend(['-map_metadata', '0', '-t', str(total_duration_seconds), fixed_video_path])
            ffmpeg_command.append('-y')

            subprocess.run(ffmpeg_command)

            print(f"Fixed metadata for {filename}")

# Example usage
original_output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"
fixed_output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\fixed_merged_vids"
fix_outputs(original_output_directory, fixed_output_directory)