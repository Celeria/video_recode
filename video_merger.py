import os
import subprocess
import datetime

def process_dashcam_footage(input_folder):
    # Get all files in the input folder
    all_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Filter for video files (you might need to adjust this based on your file extensions)
    video_files = [f for f in all_files if f.endswith('.mp4') or f.endswith('.avi')] 

    # Group files based on their creation timestamp (assuming your dashcam names files with timestamps)
    grouped_files = {}
    for file in video_files:
        timestamp_str = file.split('_')[0]  # Adjust this based on your dashcam's file naming convention
        try:
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except ValueError:
            continue  # Skip files with invalid timestamps

        # Group files within a 5-minute window (adjust as needed)
        group_key = timestamp - datetime.timedelta(minutes=timestamp.minute % 5,
                                                  seconds=timestamp.second,
                                                  microseconds=timestamp.microsecond)
        grouped_files.setdefault(group_key, []).append(file)

    for group in grouped_files.values():
        # Generate a new file name based on the first file in the group
        first_file = group[0]
        new_file_name = f"concatenated_{first_file}"

        # Concatenate videos using FFmpeg
        input_files = [os.path.join(input_folder, f) for f in group]
        ffmpeg_command = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', '-', '-c', 'copy', new_file_name]

        with open('input_list.txt', 'w') as f:
            for input_file in input_files:
                f.write(f"file '{input_file}'\n")

        with open('input_list.txt', 'r') as f:
            subprocess.run(ffmpeg_command, stdin=f)

        os.remove('input_list.txt')

        print(f"Concatenated videos into: {new_file_name}")

# Example usage
input_folder = 'path/to/your/dashcam/footage'
process_dashcam_footage(input_folder)