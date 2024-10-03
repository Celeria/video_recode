# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:39:03 2024

@author: patm3
"""

import os
import datetime
import subprocess

def concatenate_videos(video_list, output_filename):
  """Concatenates the videos using ffmpeg with hardware acceleration and stream copying."""
  try:
      first_video_filename = os.path.splitext(os.path.basename(video_list[0]))[0]
      # Extract creation time from the first video's filename
      creation_time_str = first_video_filename.replace("_", "")[:14]  # YYYYMMDDHHMMSS
      creation_time = datetime.datetime.strptime(creation_time_str, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')

      command = ["ffmpeg"]
      for video in video_list:
          command.extend(["-hwaccel", "cuda", "-i", video])  # Apply hwaccel to each input
      command.extend([
          "-filter_complex", 
              f"[0:v][1:v]concat=n={len(video_list)}:v=1[outv];"  # Concatenate video
              + ''.join([f"[{i}:a]" for i in range(len(video_list))])  # Gather all audio streams
              + f"amerge=inputs={len(video_list)}[outa]",  # Merge audio streams
          "-map", "[outv]",
          "-map", "[outa]",  # Map the merged audio stream
          "-c:v", "copy",  # Copy the video stream
          "-map_metadata", "-1",  # Remove existing metadata
          "-metadata", f"title={first_video_filename}",  # Set title to the first video's filename
          "-metadata", f"creation_time={creation_time}",  # Set creation time
          output_filename
      ])

      print(f"Executing ffmpeg command: {' '.join(command)}")
      subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
      print("Videos concatenated successfully!")

  except subprocess.CalledProcessError as e:
      print(f"FFmpeg error:\n{e.stderr}")
  except Exception as e:
      print(f"An error occurred during video concatenation: {e}")
