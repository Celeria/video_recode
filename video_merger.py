import os
import datetime
import subprocess

def concatenate_sessions(target_directory, output_directory):
    video_files = sorted(os.listdir(target_directory))
    os.makedirs(output_directory, exist_ok=True)

    current_session = []
    last_video_end = None
    total_duration = 0

    for video_file in video_files:
        video_path = os.path.join(target_directory, video_file)

        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                                 'default=noprint_wrappers=1:nokey=1', video_path],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        video_duration = float(result.stdout)
        total_duration += video_duration

        filename_parts = video_file.split('_')
        video_timestamp_eastern = datetime.datetime.strptime(
            f"{filename_parts[0]}_{filename_parts[1]}_{filename_parts[2]}", "%Y_%m%d_%H%M%S")

        # Manually adjust timestamp from Eastern to Hawaii time (subtract 5 hours)
        video_timestamp_hawaii = video_timestamp_eastern - datetime.timedelta(hours=5)

        print(
            f"Processing: {video_file} (Timestamp in Hawaii: {video_timestamp_hawaii.strftime('%Y_%m%d_%H%M%S')})")

        if last_video_end is None:
            current_session.append(video_file)
            last_video_end = video_timestamp_hawaii + datetime.timedelta(seconds=video_duration)
            print(f"  - Starting a new session")
        else:
            time_difference = video_timestamp_hawaii - last_video_end
            if time_difference.total_seconds() <= 60:
                current_session.append(video_file)
                last_video_end = video_timestamp_hawaii + datetime.timedelta(seconds=video_duration)
                print(f"  - Adding to current session")
            else:
                if time_difference.total_seconds() > 300:
                    # Format the date and time for the output file name
                    session_start_time = current_session[0].split('_')[2]
                    session_start_datetime = datetime.datetime.strptime(session_start_time, "%H%M%S")
                    formatted_time = session_start_datetime.strftime("%I-%M%p")  # 12-hour time with AM/PM

                    # Extract year, month, and day from the first video file in the session
                    year = current_session[0].split('_')[0]
                    month = datetime.datetime.strptime(current_session[0].split('_')[1][:2], "%m").strftime("%b")
                    day = current_session[0].split('_')[1][2:]

                    session_file_name = f"{year} {month} {day} {formatted_time}.txt"
                    session_file_path = os.path.join(output_directory, session_file_name)

                    # Concatenate videos using ffmpeg
                    output_video_name = f"{year} {month} {day} {formatted_time}.mp4"
                    output_video_path = os.path.join(output_directory, output_video_name)

                    with open(session_file_path, "w") as session_file:
                        minutes, seconds = divmod(total_duration, 60)
                        session_file.write(f"Total Duration: {int(minutes)} minutes {seconds:.2f} seconds\n")
                        
                        # Create the ffmpeg command
                        ffmpeg_command = ['ffmpeg']
                        for file_to_concatenate in current_session:
                            session_file.write(file_to_concatenate + "\n")
                            ffmpeg_command.extend(['-i', os.path.join(target_directory, file_to_concatenate)])
                        ffmpeg_command.extend(['-filter_complex', '[0:v] [0:a] [1:v] [1:a] concat=n={}:v=1:a=1 [v] [a]'.format(len(current_session))])
                        ffmpeg_command.extend(['-map', '[v]', '-map', '[a]', output_video_path])

                        # Execute ffmpeg
                        subprocess.run(ffmpeg_command)

                    print(f"  - Ending session, created session file: {session_file_name} and video: {output_video_name}")
                    current_session = [video_file]
                    last_video_end = video_timestamp_hawaii + datetime.timedelta(seconds=video_duration)
                    total_duration = video_duration
                    print(f"  - Starting a new session")

    # Handle the last session
    if current_session:
        # Format the date and time for the output file name
        session_start_time = current_session[0].split('_')[2]
        session_start_datetime = datetime.datetime.strptime(session_start_time, "%H%M%S")
        formatted_time = session_start_datetime.strftime("%I-%M%p")  # 12-hour time with AM/PM

        # Extract year, month, and day from the first video file in the session
        year = current_session[0].split('_')[0]
        month = datetime.datetime.strptime(current_session[0].split('_')[1][:2], "%m").strftime("%b")
        day = current_session[0].split('_')[1][2:]

        session_file_name = f"{year} {month} {day} {formatted_time}.txt"
        session_file_path = os.path.join(output_directory, session_file_name)

        # Concatenate videos for the last session
        output_video_name = f"{year} {month} {day} {formatted_time}.mp4"
        output_video_path = os.path.join(output_directory, output_video_name)

        with open(session_file_path, "w") as session_file:
            minutes, seconds = divmod(total_duration, 60)
            session_file.write(f"Total Duration: {int(minutes)} minutes {seconds:.2f} seconds\n")

            ffmpeg_command = ['ffmpeg']
            for file_to_concatenate in current_session:
                session_file.write(file_to_concatenate + "\n")
                ffmpeg_command.extend(['-i', os.path.join(target_directory, file_to_concatenate)])
            ffmpeg_command.extend(['-filter_complex', '[0:v] [0:a] [1:v] [1:a] concat=n={}:v=1:a=1 [v] [a]'.format(len(current_session))])
            ffmpeg_command.extend(['-map', '[v]', '-map', '[a]', output_video_path])

            subprocess.run(ffmpeg_command)

        print(f"  - Ending session, created session file: {session_file_name} and video: {output_video_name}")

# Example usage (replace with your paths)
target_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_video_hvenc_slower_5_20_all"
output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"
concatenate_sessions(target_directory, output_directory)