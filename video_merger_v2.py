# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:57:20 2024

@author: patm3
"""
import os
import datetime
import subprocess
import sys

# Hardcoded directories (use absolute paths with raw strings)
source_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\Hawaii Trip"
output_dir = r"D:\Patrick's Documents\Other Things\Video\Dashcam\concatenated_output"

# Maximum length of each video in minutes
video_length_max = 4

def get_video_time(filename):
  """Extracts the date and time from the filename and returns a datetime object."""
  try:
    # Extract the relevant part of the filename (YYYY_MMDD_HHMMSS)
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    date_time_str = base_filename.replace("_", "")[:14]  # Remove underscores and take first 14 characters (YYYYMMDDHHMMSS)
    return datetime.datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
  except Exception as e:
    print(f"Error parsing filename: {filename} - {e}")
    sys.exit(1)  # Exit the script if there's an error parsing the filename

def concatenate_videos(video_list, output_filename):
  """Concatenates the videos using ffmpeg with hardware acceleration."""
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
          "-c:v", "hevc_nvenc",  # Use hardware encoder for H.265
          "-c:a", "aac",    # Re-encode audio to AAC
          "-ac", "2",       # Set audio channels to 2 (stereo)
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

def main():
  """Main function to process the video files."""
  try:
    print(f"Source directory: {source_dir}")

    video_files = []
    for file in os.listdir(source_dir):
      if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')):
        video_files.append(os.path.join(source_dir, file))

    video_files.sort(key=get_video_time)
    print(f"Video files found: {video_files}")

    current_sequence = []
    prev_video_time = None

    for i, video_file in enumerate(video_files):
      video_time = get_video_time(video_file)

      if prev_video_time is None:  # First video
        current_sequence.append(video_file)
      else:
        time_diff = video_time - prev_video_time
        # Consider seconds in the comparison
        if time_diff <= datetime.timedelta(minutes=video_length_max, seconds=time_diff.seconds % 60):  
          current_sequence.append(video_file)
        else:  # New sequence
          output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
          concatenate_videos(current_sequence, output_filename)
          current_sequence = [video_file]  # Start a new sequence

      prev_video_time = video_time  # Update previous video time

      # Concatenate the last sequence
      if i == len(video_files) - 1:
        output_filename = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(current_sequence[0]))[0]}.mp4")
        concatenate_videos(current_sequence, output_filename)

  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  main()