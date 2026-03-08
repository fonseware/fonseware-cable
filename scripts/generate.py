import json
import os
import requests
import random
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

def fetch_external_epg(url, master_channel_id):
    """fetches the broadcaster's epg, checks if it's outdated, and assigns the correct channel id."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tree = ET.fromstring(response.content)
        
        programmes = []
        latest_stop = None
        now = datetime.now(timezone.utc)
        
        for prog in tree.findall("programme"):
            stop_str = prog.get("stop")
            if stop_str:
                try:
                    # parse xmltv date format (e.g., "20260308120000 +0000")
                    stop_time = datetime.strptime(stop_str, "%Y%m%d%H%M%S %z")
                    if latest_stop is None or stop_time > latest_stop:
                        latest_stop = stop_time
                except ValueError:
                    pass # ignore weirdly formatted dates for the max check
            
            # overwrite the source channel id with the official tvg_id
            prog.set("channel", master_channel_id)
            programmes.append(prog)
            
        # smart check: if all programs ended in the past, the epg is outdated
        if latest_stop and latest_stop < now:
            print(f"epg for {master_channel_id} is outdated (last program ended at {latest_stop}). switching to placeholders.")
            return None
            
        # if the list is completely empty, also fallback
        if not programmes:
            return None
            
        return programmes
    except Exception as e:
        print(f"error: failed to fetch epg for {master_channel_id} at {url}: {e}")
        return None

def generate_fallback_placeholders(channel_id, channel_name, logo_url):
    """generates exactly one day (12:00 am to 12:00 am next day) of placeholders."""
    programmes = []
    now = datetime.now(timezone.utc)
    
    # strictly lock the timeframe from 12:00 am today to 12:00 am tomorrow
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    placeholders = ["placeholder1.jpg", "placeholder2.jpg", "placeholder3.jpg"]
    
    # check if it's one of the static broadcast channels (case-insensitive)
    name_lower = channel_name.lower()
    is_static_channel = "cable tv" in name_lower or "cable fm" in name_lower or "no channel" in name_lower

    desc_text = f"The broadcaster for {channel_name} has not set a programme block yet. Right now you are seeing a placeholder block. Please wait while we or the broadcaster settle this."

    if is_static_channel:
        # generate a single 24-hour block from 12:00 am to 12:00 am next day
        start_time = start_of_day
        end_time = start_time + timedelta(hours=24)

        prog = ET.Element("programme", 
                          start=start_time.strftime("%Y%m%d%H%M%S +0000"), 
                          stop=end_time.strftime("%Y%m%d%H%M%S +0000"), 
                          channel=channel_id)

        title = ET.SubElement(prog, "title", lang="en")
        title.text = "No programme set"

        desc = ET.SubElement(prog, "desc", lang="en")
        desc.text = desc_text

        category = ET.SubElement(prog, "category", lang="en")
        category.text = "General"

        date = ET.SubElement(prog, "date")
        date.text = start_time.strftime("%Y")

        chosen_pic = random.choice(placeholders)
        pic_url = f"http://cable.fnswe.me/media/{chosen_pic}"
        ET.SubElement(prog, "icon", src=pic_url)

        ep_num = ET.SubElement(prog, "episode-num", system="xmltv_ns")
        ep_num.text = "0.0.0/1"

        programmes.append(prog)

    else:
        # 24 hours = 48 half-hour blocks from 12:00 am to 12:00 am
        for i in range(48):
            start_time = start_of_day + timedelta(minutes=30 * i)
            end_time = start_time + timedelta(minutes=30)

            prog = ET.Element("programme", 
                              start=start_time.strftime("%Y%m%d%H%M%S +0000"), 
                              stop=end_time.strftime("%Y%m%d%H%M%S +0000"), 
                              channel=channel_id)

            title = ET.SubElement(prog, "title", lang="en")
            title.text = "No program set"

            desc = ET.SubElement(prog, "desc", lang="en")
            desc.text = desc_text

            category = ET.SubElement(prog, "category", lang="en")
            category.text = "General"

            date = ET.SubElement(prog, "date")
            date.text = start_time.strftime("%Y")

            chosen_pic = random.choice(placeholders)
            pic_url = f"http://cable.fnswe.me/media/{chosen_pic}"
            ET.SubElement(prog, "icon", src=pic_url)

            ep_num = ET.SubElement(prog, "episode-num", system="xmltv_ns")
            ep_num.text = "0.0.0/1"

            programmes.append(prog)

    return programmes

def generate_playlists():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tv_json_path = os.path.join(script_dir, "tv.json")
    fm_json_path = os.path.join(script_dir, "fm.json")
    
    # output paths 
    master_m3u_path = os.path.join(script_dir, "..", "ch.m3u")
    jellyfin_m3u_path = os.path.join(script_dir, "..", "chjf.m3u")
    master_epg_path = os.path.join(script_dir, "..", "epg.xml")
    jellyfin_epg_path = os.path.join(script_dir, "..", "epgjf.xml")
    radio_dir = os.path.join(script_dir, "..", "radio")

    # load the data
    tv_channels = []
    fm_channels = []
    
    if os.path.exists(tv_json_path):
        with open(tv_json_path, 'r', encoding='utf-8') as f:
            tv_channels = json.load(f)
            
    if os.path.exists(fm_json_path):
        with open(fm_json_path, 'r', encoding='utf-8') as f:
            fm_channels = json.load(f)

    # 1. setup xml trees
    master_xml = ET.Element("tv", {"generator-info-name": "fonseware network", "source-info-name": "fonseware-cable"})
    jellyfin_xml = ET.Element("tv", {"generator-info-name": "fonseware jellyfin", "source-info-name": "fonseware-cable"})

    # 2. build the channel headers
    for ch in tv_channels + fm_channels:
        ch_elem = ET.Element("channel", id=ch["tvg_id"])
        display_name = ET.SubElement(ch_elem, "display-name")
        display_name.text = ch["display_name"]
        if ch.get("tvg_logo"):
            ET.SubElement(ch_elem, "icon", src=ch["tvg_logo"])

        master_xml.append(ch_elem)
        
        # mirror tv channels to jellyfin
        if ch in tv_channels:
            ch_elem_jf = ET.Element("channel", id=ch["tvg_id"])
            display_name_jf = ET.SubElement(ch_elem_jf, "display-name")
            display_name_jf.text = ch["display_name"]
            if ch.get("tvg_logo"):
                ET.SubElement(ch_elem_jf, "icon", src=ch["tvg_logo"])
            jellyfin_xml.append(ch_elem_jf)

    # 3. fetch or generate programmes
    for ch in tv_channels + fm_channels:
        programmes = None
        epg_url = ch.get("epg_url")
        
        if epg_url:
            print(f"fetching schedule for {ch['display_name']}...")
            programmes = fetch_external_epg(epg_url, ch["tvg_id"])
            
        if not programmes:
            print(f"generating fallback placeholders for {ch['display_name']}...")
            programmes = generate_fallback_placeholders(ch["tvg_id"], ch["display_name"], ch.get("tvg_logo"))

        for prog in programmes:
            master_xml.append(prog)
            # strictly only append to jellyfin if it's a tv channel
            if ch in tv_channels:
                jf_prog = ET.fromstring(ET.tostring(prog))
                jellyfin_xml.append(jf_prog)

    # 4. write the xml files
    tree_master = ET.ElementTree(master_xml)
    ET.indent(tree_master, space="  ", level=0) 
    tree_master.write(master_epg_path, encoding="utf-8", xml_declaration=True)

    tree_jellyfin = ET.ElementTree(jellyfin_xml)
    ET.indent(tree_jellyfin, space="  ", level=0)
    tree_jellyfin.write(jellyfin_epg_path, encoding="utf-8", xml_declaration=True)

    # 5. generate the m3u playlists
    master_epg_link = "http://cable.fnswe.me/epg.xml"
    jellyfin_epg_link = "http://cable.fnswe.me/epgjf.xml"

    with open(os.path.normpath(master_m3u_path), 'w', encoding='utf-8') as f:
        f.write(f'#EXTM3U x-tvg-url="{master_epg_link}"\n')
        for ch in tv_channels + fm_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["tvg_logo"]}" group-title="{ch["group_title"]}" tvg-chno="{ch["tvg_chno"]}" tvg-country="{ch["tvg_country"]}" tvg-language="{ch["tvg_language"]}" tvg-name="{ch["tvg_name"]}" radio="{ch["radio"]}",{ch["display_name"]}\n{ch["url"]}\n\n')

    with open(os.path.normpath(jellyfin_m3u_path), 'w', encoding='utf-8') as f:
        f.write(f'#EXTM3U x-tvg-url="{jellyfin_epg_link}"\n')
        for ch in tv_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["tvg_logo"]}" group-title="{ch["group_title"]}" tvg-chno="{ch["tvg_chno"]}" tvg-country="{ch["tvg_country"]}" tvg-language="{ch["tvg_language"]}" tvg-name="{ch["tvg_name"]}" radio="{ch["radio"]}",{ch["display_name"]}\n{ch["url"]}\n\n')

    # 6. radio files
    if not os.path.exists(os.path.normpath(radio_dir)):
        os.makedirs(os.path.normpath(radio_dir))

    for ch in fm_channels:
        safe_name = "".join([c for c in ch["display_name"] if c.isalnum() or c.isspace()]).rstrip()
        strm_path = os.path.join(radio_dir, f"{safe_name}.strm")
        nfo_path = os.path.join(radio_dir, f"{safe_name}.nfo")

        with open(os.path.normpath(strm_path), 'w', encoding='utf-8') as f:
            f.write(ch["url"])

        with open(os.path.normpath(nfo_path), 'w', encoding='utf-8') as f:
            f.write(f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<track>
  <title>{ch["display_name"]}</title>
  <tracknumber>{ch["tvg_chno"]}</tracknumber>
  <thumb>{ch["tvg_logo"]}</thumb>
  <genre>{ch["group_title"]}</genre>
</track>''')

    print("generation complete. epg files fetched, placeholders drafted, and playlists compiled successfully.")

if __name__ == "__main__":
    generate_playlists()