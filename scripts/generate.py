import json
import os

def build_the_broadcasting_empire():
    # find exactly where this script lives
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # input files
    tv_json_path = os.path.join(script_dir, "tv.json")
    fm_json_path = os.path.join(script_dir, "fm.json")

    # output destinations (one folder up)
    master_m3u_path = os.path.join(script_dir, "..", "ch.m3u")
    jellyfin_m3u_path = os.path.join(script_dir, "..", "chjf.m3u")
    radio_dir = os.path.join(script_dir, "..", "radio")

    # load the data
    tv_channels = []
    fm_channels = []

    if os.path.exists(tv_json_path):
        with open(tv_json_path, 'r', encoding='utf-8') as f:
            tv_channels = json.load(f)
    else:
        print("oop! tv.json is missing.")

    if os.path.exists(fm_json_path):
        with open(fm_json_path, 'r', encoding='utf-8') as f:
            fm_channels = json.load(f)
    else:
        print("oop! fm.json is missing.")

    # 1. create the master ch.m3u (for kodi, includes everything)
    with open(os.path.normpath(master_m3u_path), 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for ch in tv_channels + fm_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["tvg_logo"]}" group-title="{ch["group_title"]}" tvg-chno="{ch["tvg_chno"]}" tvg-country="{ch["tvg_country"]}" tvg-language="{ch["tvg_language"]}" tvg-name="{ch["tvg_name"]}" radio="{ch["radio"]}",{ch["display_name"]}\n{ch["url"]}\n\n')

    # 2. create the jellyfin-specific chjf.m3u (tv only, ignores fm.json)
    with open(os.path.normpath(jellyfin_m3u_path), 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for ch in tv_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["tvg_logo"]}" group-title="{ch["group_title"]}" tvg-chno="{ch["tvg_chno"]}" tvg-country="{ch["tvg_country"]}" tvg-language="{ch["tvg_language"]}" tvg-name="{ch["tvg_name"]}" radio="{ch["radio"]}",{ch["display_name"]}\n{ch["url"]}\n\n')

    # 3. create the radio directory and strm files
    if not os.path.exists(os.path.normpath(radio_dir)):
        os.makedirs(os.path.normpath(radio_dir))

    for ch in fm_channels:
        # clean the filename so windows/linux don't throw a fit over weird characters
        safe_name = "".join([c for c in ch["display_name"] if c.isalnum() or c.isspace()]).rstrip()
        
        strm_path = os.path.join(radio_dir, f"{safe_name}.strm")
        nfo_path = os.path.join(radio_dir, f"{safe_name}.nfo")

        # write the strm file (just the raw url, exactly what jellyfin wants)
        with open(os.path.normpath(strm_path), 'w', encoding='utf-8') as f:
            f.write(ch["url"])

        # write the nfo file (to inject the logo and name into jellyfin's database)
        with open(os.path.normpath(nfo_path), 'w', encoding='utf-8') as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<track>
  <title>{ch["display_name"]}</title>
  <tracknumber>{ch["tvg_chno"]}</tracknumber>
  <thumb>{ch["tvg_logo"]}</thumb>
  <genre>{ch["group_title"]}</genre>
</track>''')

    print("purr! the script ate and left no crumbs. ch.m3u, chjf.m3u, and the radio folder have been generated successfully.")

if __name__ == "__main__":
    build_the_broadcasting_empire()