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
    filename = filename.lower()
    # Extract the relevant part of the filename (YYYY_MM_DD_hhmmss)
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    date_time_str = '_'.join(base_filename.split('_')[:3]).replace("_", "")  # Join only the first 3 parts
    return datetime.datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
  except Exception as e:
    print(f"Error parsing filename: {filename} - {e}")
    return None

def concatenate_videos(video_list, output_filename):
  """Concatenates the videos in the list and saves the result to the output filename."""
  with open("mylist.txt", "w") as f:
    for video in video_list:
      f.write(f"file '{os.path.abspath(video)}'\n") # Use absolute path here
  command = f'ffmpeg -f concat -safe 0 -i mylist.txt -c copy "{output_filename}"'
  print(f"Executing ffmpeg command: {command}") # Print the command being executed
  exit_code = os.system(command)
  print(f"ffmpeg exit code: {exit_code}") # Print the exit code
  os.remove("mylist.txt")

def main():
  """Main function to process the video files."""
  print(f"Source directory: {source_dir}") # Print the source directory

  video_files = []
  for file in os.listdir(source_dir):
    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')): # Check for common video file extensions
      video_files.append(os.path.join(source_dir, file))

  video_files.sort(key=get_video_time)

  print(f"Video files found: {video_files}") # Print the list of video files

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
        print(f"Concatenating sequence: {current_sequence}") # Print the sequence being concatenated
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
        concatenate_videos(current_sequence, output_filename)
        current_sequence = [os.path.join(os.path.abspath(source_dir), video_file)] # Use absolute path here
        start_time = video_time

    # Concatenate the last sequence
    if i == len(video_files) - 1:
      print(f"Concatenating sequence: {current_sequence}") # Print the sequence being concatenated
      output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
      concatenate_videos(current_sequence, output_filename)

if __name__ == "__main__":
  main()