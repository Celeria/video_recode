# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 00:34:42 2024

@author: patm3
"""

import os
import subprocess

def check_av1_nvenc_support():
    try:
        subprocess.run(['ffmpeg', '-h', 'encoder=av1_nvenc'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True 
    except subprocess.CalledProcessError:
        return False 

def reencode_videos(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Check if the input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found.")
        return

    # Get all files in the input folder
    all_files = os.listdir(input_folder)
    if not all_files:
        print(f"No files found in '{input_folder}'.")
        return

    for filename in all_files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        print(f"Re-encoding {filename}...")

        ffmpeg_cmd = f'ffmpeg -hwaccel cuda -i "{input_path}" -c:v hevc_nvenc -preset slower "{output_path}" -y'

        try:
            result = subprocess.run(ffmpeg_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr if e.stderr else e.stdout 
            print(f'Error processing {filename}: {error_message}')

if __name__ == "__main__":
    input_folder = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_video"
    output_folder = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_video_highqual"

    if check_av1_nvenc_support():
        reencode_videos(input_folder, output_folder)
    else:
        print("AV1 encoding is not supported on this system. Consider using a different codec or updating your hardware/drivers.")