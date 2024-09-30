# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 23:01:42 2024

@author: patm3
"""

import os
import moviepy.editor as mp

def concatenate_videos(txt_file_path, source_dir, output_dir):
  """Concatenates videos listed in a text file and saves the result in the output directory."""

  video_clips = []
  with open(txt_file_path, 'r') as f:
      next(f)  # Skip the first line (duration information)
      for line in f:
          video_filename = line.strip() + '.MP4'  # Assuming .MP4 extension
          video_path = os.path.join(source_dir, video_filename)
          if os.path.exists(video_path):
              video_clips.append(mp.VideoFileClip(video_path))

  if video_clips:
      final_clip = mp.concatenate_videoclips(video_clips, method="compose")
      output_path = os.path.join(output_dir, os.path.basename(txt_file_path).replace('.txt', '.mp4'))
      final_clip.write_videofile(output_path)
      print(f"Concatenated videos saved to: {output_path}")
  else:
      print(f"No valid video files found for {txt_file_path}")

# Hardcoded directories
target_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"
source_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_video_hvenc_slower_5_20_all"
output_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\concatenated_output"  # Adjust as needed

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each text file in the target directory
for filename in os.listdir(target_dir):
  if filename.endswith(".txt"):
      txt_file_path = os.path.join(target_dir, filename)
      concatenate_videos(txt_file_path, source_dir, output_dir)