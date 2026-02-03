import pandas as pd
import subprocess
import json

def create_highlight(input_file, start_time, duration, output_name):
    command = f"ffmpeg -ss {start_time} -i {input_file} -t {duration} -c copy -avoid_negative_ts make_zero {output_name}.mp4"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Highlight saved: {output_name}.mp4")
    except subprocess.CalledProcessError:
        print("Error: Make sure FFmpeg is installed and the input file exists.")

def process_highlights(csv_path, input_video, output_dir):
    df = pd.read_csv(csv_path)
    manifest = {
        "game_title": "Your Game Title",
        "highlights": []
    }

    for idx, row in df.iterrows():
        clip_id = row['clip_id']
        start_time = row['start_time']
        duration = str(row['duration'])
        output_name = f"{output_dir}/{clip_id}_clip"

        create_highlight(input_video, start_time, duration, output_name)

        highlight = {
            "clip_id": clip_id,
            "title": row['title'],
            "subtitle": row.get('subtitle', ''),
            "period": row['period'],
            "clock": row['clock'],
            "duration": row['duration'],
            "tags": [tag.strip() for tag in str(row['tags']).split(',') if tag.strip()],
            "scoreA": int(row['scoreA']),
            "scoreB": int(row['scoreB']),
            "context": row.get('context', '')
        }
        manifest["highlights"].append(highlight)

    # Save manifest JSON
    with open(f"{output_dir}/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest saved to {output_dir}/manifest.json")

# Example usage:
process_highlights("highlights_log.csv", "game_video.mp4", "./highlights")
