# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 22:26:30 2024

@author: patm3
"""

import os
import datetime
import subprocess
import re

def fix_outputs(original_output_directory, fixed_output_directory):
    os.makedirs(fixed_output_directory, exist_ok=True)

    for filename in os.listdir(original_output_directory):
        if filename.endswith(".mp4"):
            match = re.match(r"(\d{4}) (\w{3}) (\d{2}) (\d{1,2}-\d{2}[AP]M)\.mp4", filename)
            if match:
                year, month_abbr, day, time_str = match.groups()
                time_str = time_str.replace("-", ":")
                original_timestamp = datetime.datetime.strptime(f"{year} {month_abbr} {day} {time_str}", "%Y %b %d %I:%M%p")

                adjusted_timestamp = original_timestamp + datetime.timedelta(hours=5)
                new_formatted_time = adjusted_timestamp.strftime("%I-%M%p")

                new_filename = f"{year} {month_abbr} {day} {new_formatted_time}.mp4"

                original_filepath = os.path.join(original_output_directory, filename)
                new_filepath = os.path.join(original_output_directory, new_filename)
                os.rename(original_filepath, new_filepath)
                print(f"Renamed {filename} to {new_filename}")

                fixed_video_path = os.path.join(fixed_output_directory, new_filename)
                subprocess.run(['ffmpeg', '-i', new_filepath, '-c', 'copy', '-map_metadata', '0', fixed_video_path],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                print(f"Fixed metadata for {new_filename}")

# Example usage
original_output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"
fixed_output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\fixed_merged_vids" # New output directory
fix_outputs(original_output_directory, fixed_output_directory)