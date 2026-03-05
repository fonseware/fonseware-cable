import json
import os

def build_the_playlist():
    # find exactly where this script lives, hunty
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # build the absolute paths to your json files so python doesn't get lost
    files_to_scan = [
        os.path.join(script_dir, "tv.json"),
        os.path.join(script_dir, "fm.json")
    ]

    # put the m3u file one folder up from the script's directory
    m3u_file = os.path.join(script_dir, "..", "ch.m3u")

    # this will hold all our channels from both files
    all_channels = []

    for json_file in files_to_scan:
        if not os.path.exists(json_file):
            print(f"warning: {os.path.basename(json_file)} is missing in action. skipping it so we don't throw a wrench in the works.")
            continue

        # open the json and load it up
        with open(json_file, 'r', encoding='utf-8') as file:
            try:
                channels = json.load(file)
                # add the channels to our master list
                all_channels.extend(channels)
                print(f"ate! successfully swallowed {os.path.basename(json_file)}.")
            except json.JSONDecodeError:
                print(f"your {os.path.basename(json_file)} is busted. you probably missed a comma somewhere! skipping...")
                continue

    # if we came up empty-handed after checking both files, abandon ship
    if not all_channels:
        print("error: both json files are awol or empty. we are dead in the water. aborting.")
        return

    # write out the master m3u
    # normalize path just to make it look pretty in the terminal output
    m3u_file_clean = os.path.normpath(m3u_file)
    with open(m3u_file_clean, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")

        for ch in all_channels:
            try:
                extinf = (f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" '
                          f'tvg-logo="{ch["tvg_logo"]}" '
                          f'group-title="{ch["group_title"]}" '
                          f'tvg-chno="{ch["tvg_chno"]}" '
                          f'tvg-country="{ch["tvg_country"]}" '
                          f'tvg-language="{ch["tvg_language"]}" '
                          f'tvg-name="{ch["tvg_name"]}" '
                          f'radio="{ch["radio"]}",{ch["display_name"]}\n')

                f.write(extinf)
                f.write(f'{ch["url"]}\n\n')
            except KeyError as e:
                print(f"missing an attribute in your json! you dropped the ball on: {e}")
                return

    print(f"purr! your master playlist has been generated and saved at: {m3u_file_clean}")

if __name__ == "__main__":
    build_the_playlist()