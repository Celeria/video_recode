# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 11:18:20 2024

@author: patm3
"""

import os
import datetime
import subprocess

def concatenate_sessions(target_directory, output_directory):
    video_files = sorted(os.listdir(target_directory))
    output_folder = os.path.join(output_directory, "concatenated_sessions")  # Updated line
    os.makedirs(output_folder, exist_ok=True)

    current_session = []
    last_video_end = None

    for video_file in video_files:
        video_path = os.path.join(target_directory, video_file)

        # Use ffprobe to get video duration
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        video_duration = float(result.stdout)

        filename_parts = video_file.split('_')
        video_timestamp = datetime.datetime.strptime(f"{filename_parts[0]}_{filename_parts[1]}_{filename_parts[2]}", "%Y_%m%d_%H%M%S")

        if last_video_end is None:
            current_session.append(video_file)
            last_video_end = video_timestamp + datetime.timedelta(seconds=video_duration)
        else:
            time_difference = video_timestamp - last_video_end
            if time_difference.total_seconds() <= 60:
                current_session.append(video_file)
                last_video_end = video_timestamp + datetime.timedelta(seconds=video_duration)
            else:
                if time_difference.total_seconds() > 300:  # 5 minutes
                    session_file_name = f"{current_session[0].split('_')[0]}_{current_session[0].split('_')[1]}_{current_session[0].split('_')[2]}.txt"
                    session_file_path = os.path.join(output_folder, session_file_name)
                    with open(session_file_path, "w") as session_file:
                        for file_to_concatenate in current_session:
                            session_file.write(file_to_concatenate + "\n")
                    current_session = [video_file]
                    last_video_end = video_timestamp + datetime.timedelta(seconds=video_duration)

    # Handle the last session
    if current_session:
        session_file_name = f"{current_session[0].split('_')[0]}_{current_session[0].split('_')[1]}_{current_session[0].split('_')[2]}.txt"
        session_file_path = os.path.join(output_folder, session_file_name)
        with open(session_file_path, "w") as session_file:
            for file_to_concatenate in current_session:
                session_file.write(file_to_concatenate + "\n")

# Example usage
target_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\Hawaii Trip"
output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"  # Specify your desired output directory
concatenate_sessions(target_directory, output_directory)