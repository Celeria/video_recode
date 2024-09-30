import os
import datetime
import subprocess
import json
import ffmpeg

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
                    session_start_time = current_session[0].split('_')[2]
                    session_start_datetime = datetime.datetime.strptime(session_start_time, "%H%M%S")
                    formatted_time = session_start_datetime.strftime("%I-%M%p") 

                    year = current_session[0].split('_')[0]
                    month = datetime.datetime.strptime(current_session[0].split('_')[1][:2], "%m").strftime("%b")
                    day = current_session[0].split('_')[1][2:]

                    session_file_name = f"{year} {month} {day} {formatted_time}.txt"
                    session_file_path = os.path.join(output_directory, session_file_name)

                    output_video_name = f"{year} {month} {day} {formatted_time}.mp4"
                    output_video_path = os.path.join(output_directory, output_video_name)

                    with open(output_video_path, 'wb') as output_video:
                        for file_to_concatenate in current_session:
                            with open(os.path.join(target_directory, file_to_concatenate), 'rb') as input_video:
                                output_video.write(input_video.read())

                    first_video_path = os.path.join(target_directory, current_session[0])
                    result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', first_video_path],
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    probe_data = json.loads(result.stdout)
                    video_stream = next((stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'), None)
                    audio_stream = next((stream for stream in probe_data['streams'] if stream['codec_type'] == 'audio'), None)

                    in_stream = ffmpeg.input(first_video_path)
                    out_stream = ffmpeg.output(in_stream, output_video_path, format='mp4')

                    if video_stream:
                        out_stream = out_stream.video.codec('copy')
                    if audio_stream:
                        out_stream = out_stream.audio.codec('copy')

                    ffmpeg.run(out_stream, overwrite_output=True)

                    with open(session_file_path, "w") as session_file:
                        minutes, seconds = divmod(total_duration, 60)
                        session_file.write(f"Total Duration: {int(minutes)} minutes {seconds:.2f} seconds\n")
                        for file_to_concatenate in current_session:
                            session_file.write(file_to_concatenate + "\n")
                    print(f"  - Ending session, created session file: {session_file_name} and video: {output_video_name}")
                    current_session = [video_file]
                    last_video_end = video_timestamp_hawaii + datetime.timedelta(seconds=video_duration)
                    total_duration = video_duration
                    print(f"  - Starting a new session")

    # Handle the last session
    if current_session:
        session_start_time = current_session[0].split('_')[2]
        session_start_datetime = datetime.datetime.strptime(session_start_time, "%H%M%S")
        formatted_time = session_start_datetime.strftime("%I-%M%p")

        year = current_session[0].split('_')[0]
        month = datetime.datetime.strptime(current_session[0].split('_')[1][:2], "%m").strftime("%b")
        day = current_session[0].split('_')[1][2:]

        session_file_name = f"{year} {month} {day} {formatted_time}.txt"
        session_file_path = os.path.join(output_directory, session_file_name)

        output_video_name = f"{year} {month} {day} {formatted_time}.mp4"
        output_video_path = os.path.join(output_directory, output_video_name)

        with open(output_video_path, 'wb') as output_video:
            for file_to_concatenate in current_session:
                with open(os.path.join(target_directory, file_to_concatenate), 'rb') as input_video:
                    output_video.write(input_video.read())

        first_video_path = os.path.join(target_directory, current_session[0])
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                                 '-show_streams', first_video_path],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        probe_data = json.loads(result.stdout)
        video_stream = next((stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe_data['streams'] if stream['codec_type'] == 'audio'), None)

        in_stream = ffmpeg.input(first_video_path)
        out_stream = ffmpeg.output(in_stream, output_video_path, format='mp4')

        if video_stream:
            out_stream = out_stream.video.codec('copy')
        if audio_stream:
            out_stream = out_stream.audio.codec('copy')

        ffmpeg.run(out_stream, overwrite_output=True)

        with open(session_file_path, "w") as session_file:
            minutes, seconds = divmod(total_duration, 60)
            session_file.write(f"Total Duration: {int(minutes)} minutes {seconds:.2f} seconds\n")
            for file_to_concatenate in current_session:
                session_file.write(file_to_concatenate + "\n")
        print(f"  - Ending session, created session file: {session_file_name} and video: {output_video_name}")

# Example usage (replace with your paths)
target_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_video_hvenc_slower_5_20_all"
output_directory = r"D:\Patrick's Documents\Other Things\Video\Dashcam\test_merged_vids"
concatenate_sessions(target_directory, output_directory)