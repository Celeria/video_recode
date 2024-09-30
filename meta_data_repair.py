# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 22:48:16 2024

@author: patm3
"""

import os
import re
import shutil
import moviepy.editor as mp

def fix_video_duration(video_path, duration_text, output_dir):
    """Fixes the duration of a video file and copies it to the output directory."""

    # Extract duration in seconds using regex
    match = re.search(r"Total Duration:\s*(\d+)\s*minutes\s*([\d.]+)\s*seconds", duration_text)
    if match:
        minutes, seconds = int(match.group(1)), float(match.group(2))
        total_seconds = minutes * 60 + seconds
        
        # Load the video
        video = mp.VideoFileClip(video_path)

        # Set the correct duration (rounded down)
        video.duration = int(total_seconds)

        # Construct the output file path
        output_path = os.path.join(output_dir, os.path.basename(video_path))

        # Write the video with updated metadata to the output directory
        video.write_videofile(output_path)
        print(f"Fixed duration and copied to {output_path}")
    else:
        print(f"Could not parse duration from {video_path}.txt")

# Hardcoded target and output directories
target_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids" 
output_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\fixed_merged_vids"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process files in the directory
for filename in os.listdir(target_dir):
    base_name, extension = os.path.splitext(filename)
    if extension == ".txt":
        txt_path = os.path.join(target_dir, filename)
        video_path = os.path.join(target_dir, base_name + ".mp4")

        if os.path.exists(video_path):
            with open(txt_path, "r") as f:
                duration_text = f.readline()
            fix_video_duration(video_path, duration_text, output_dir)