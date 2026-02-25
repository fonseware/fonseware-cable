import json
import os

def build_the_playlist():
    json_file = "channels.json"

    # the '..' tells the system to go up one folder level
    m3u_file = os.path.join('..', "ch.m3u")

    # check if the file is actually there before we put the cart before the horse
    if not os.path.exists(json_file):
        print(f"error: {json_file} is missing in action. make sure it is in the same folder as this script.")
        return

    # open the json and load it up
    with open(json_file, 'r', encoding='utf-8') as file:
        try:
            channels = json.load(file)
        except json.JSONDecodeError:
            print(f"your {json_file} is busted. you probably missed a comma somewhere!")
            return

    # write out the m3u
    with open(m3u_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")

        for ch in channels:
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

    print(f"purr! your playlist has been generated and saved one folder up at: {m3u_file}")

if __name__ == "__main__":
    build_the_playlist()