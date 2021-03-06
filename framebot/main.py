import functools
import os
import time
from pathlib import Path

import facebook
import schedule

import extract_frames

fps = int(os.environ.get('FPS'))
interval = int(os.environ.get('INTERVAL'))


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback

                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    return catch_exceptions_decorator


def main():
    frame_dirs = sorted(
        [f for f in os.listdir("./frames") if not f.startswith(".")],
        key=lambda f: f.lower(),
    )

    for frame_dir in frame_dirs:
        # First folder is always the current episode
        inframe_dir = sorted(
            [f for f in os.listdir(f"./frames/{frame_dir}") if not f.startswith(".")],
            key=lambda f: f.lower(),
        )

        # Empty folder means that episode is done
        if len(inframe_dir) == 0:
            continue

        # New Episode
        # Save temporary data about amount of frame
        with open("./tmp_data", "a+") as f:
            f.seek(0)
            filled = f.read(1)
            if not filled:
                total_frames = str(len(inframe_dir))
                f.write(total_frames)
            else:
                f.seek(0)
                total_frames = str(f.readline())
        break

    if len(inframe_dir) == 1:
        os.remove("./tmp_data")
    elif len(inframe_dir) == 0:
        print("There is no more episode to post.")
        raise SystemExit

    final_frame_dir = f"./frames/{frame_dir}/{inframe_dir[0]}"

    # Get file name, replace "e" with empty string to get episode number
    episode = frame_dir.split(".")[0].replace("e", "")
    return post(final_frame_dir, total_frames, episode)


@catch_exceptions()
def post(frame_dir, total_frames, episode):
    fb_token = os.environ.get('FB_TOKEN')
    prefix = os.environ.get('PREFIX')
    frame_fname = Path(frame_dir).name
    current_frame_num = os.path.splitext(frame_fname)[0].lstrip("0")

    message = f"{prefix} | Epiz??d: {episode} | K??pkocka: {current_frame_num}/{str(total_frames)}"
    graph = facebook.GraphAPI(fb_token)
    graph.put_photo(image=open(frame_dir, "rb"), message=message)
    print(f"Posted: {message}")
    os.remove(frame_dir)


def init_frame():
    videos_dir = sorted(
        [
            f
            for f in os.listdir("./videos")
            if not f.startswith(".") and f.startswith("e")
        ],
        key=lambda f: f.lower(),
    )

    for video in videos_dir:
        if os.path.exists(f"./frames/{video}"):
            continue
        extract_frames.video_to_frames(
            video_path=f"./videos/{video}",
            frames_dir="frames",
            overwrite=False,
            every=fps,
        )


if __name__ == "__main__":
    init_frame()
    schedule.every(interval).minutes.do(main).run()
    while True:
        schedule.run_pending()
        time.sleep(1)
