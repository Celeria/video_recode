# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:57:20 2024

@author: patm3
"""
import os
import datetime

# Hardcoded directories (use absolute paths)
source_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\Hawaii Trip"
output_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\concatenated_output"

# Maximum length of each video in minutes
video_length_max = 4

def get_video_time(filename):
  """Extracts the date and time from the filename and returns a datetime object."""
  try:
    date_time_str = filename.split('_')[0] + filename.split('_')[1]
    return datetime.datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
  except:
    print(f"Error parsing filename: {filename}")
    return None

def concatenate_videos(video_list, output_filename):
  """Concatenates the videos in the list and saves the result to the output filename."""
  with open("mylist.txt", "w") as f:
    for video in video_list:
      f.write(f"file '{os.path.abspath(video)}'\n") # Use absolute path here
  os.system(f'ffmpeg -f concat -safe 0 -i mylist.txt -c copy "{output_filename}"')
  os.remove("mylist.txt")

def main():
  """Main function to process the video files."""
  video_files = [f for f in os.listdir(source_dir) if f.endswith('.mp4')]
  video_files.sort(key=get_video_time)

  current_sequence = []
  start_time = None

  for i, video_file in enumerate(video_files):
    video_time = get_video_time(video_file)
    if video_time is None:
      continue

    if not current_sequence:
      current_sequence.append(os.path.join(os.path.abspath(source_dir), video_file))  # Use absolute path here
      start_time = video_time
    else:
      time_diff = video_time - start_time
      if time_diff <= datetime.timedelta(minutes=video_length_max):
        current_sequence.append(os.path.join(os.path.abspath(source_dir), video_file)) # Use absolute path here
      else:
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
        concatenate_videos(current_sequence, output_filename)
        current_sequence = [os.path.join(os.path.abspath(source_dir), video_file)] # Use absolute path here
        start_time = video_time

    # Concatenate the last sequence
    if i == len(video_files) - 1:
      output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
      concatenate_videos(current_sequence, output_filename)

if __name__ == "__main__":
  main()