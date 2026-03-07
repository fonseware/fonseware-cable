import json
import os
import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

def fetch_external_epg(url, master_channel_id):
    """snatches the broadcaster's epg and forces it to use our channel id"""
    try:
        # 10 second timeout so a dead broadcaster server doesn't hold up the whole network
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tree = ET.fromstring(response.content)
        
        programmes = []
        for prog in tree.findall("programme"):
            # overwrite whatever channel id they use with our official tvg_id
            prog.set("channel", master_channel_id)
            programmes.append(prog)
        return programmes
    except Exception as e:
        print(f"oop! failed to scrape epg for {master_channel_id} at {url}: {e}")
        return None

def generate_floptropica_placeholders(channel_id, channel_name, logo_url):
    """whips up 48 hours of 30-minute dummy blocks so the tv guide never looks empty"""
    programmes = []
    now = datetime.now(timezone.utc)
    # snap to the nearest 30-minute mark so the grid looks perfectly aligned
    now = now - timedelta(minutes=now.minute % 30, seconds=now.second, microseconds=now.microsecond)

    # 48 hours = 96 half-hour blocks
    for i in range(96):
        start_time = now + timedelta(minutes=30 * i)
        end_time = start_time + timedelta(minutes=30)

        # format: YYYYMMDDHHMMSS +0000
        prog = ET.Element("programme", 
                          start=start_time.strftime("%Y%m%d%H%M%S +0000"), 
                          stop=end_time.strftime("%Y%m%d%H%M%S +0000"), 
                          channel=channel_id)

        title = ET.SubElement(prog, "title", lang="en")
        title.text = "No program set"

        desc = ET.SubElement(prog, "desc", lang="en")
        desc.text = f"schedule information for {channel_name} is currently unavailable. please hold while we fix the badussy."

        category = ET.SubElement(prog, "category", lang="en")
        category.text = "General"

        date = ET.SubElement(prog, "date")
        date.text = start_time.strftime("%Y")

        if logo_url:
            ET.SubElement(prog, "icon", src=logo_url)

        # throwing in a dummy season/episode number using xmltv standard (0-indexed)
        ep_num = ET.SubElement(prog, "episode-num", system="xmltv_ns")
        ep_num.text = "0.0.0/1"

        programmes.append(prog)

    return programmes

def build_the_broadcasting_empire():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tv_json_path = os.path.join(script_dir, "tv.json")
    fm_json_path = os.path.join(script_dir, "fm.json")
    
    # output paths going up one directory
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

    # 1. SETUP XML TREES
    master_xml = ET.Element("tv", {"generator-info-name": "fonseware empire", "source-info-name": "fonseware-cable"})
    jellyfin_xml = ET.Element("tv", {"generator-info-name": "fonseware jellyfin", "source-info-name": "fonseware-cable"})

    # 2. BUILD THE CHANNEL HEADERS
    for ch in tv_channels + fm_channels:
        ch_elem = ET.Element("channel", id=ch["tvg_id"])
        display_name = ET.SubElement(ch_elem, "display-name")
        display_name.text = ch["display_name"]
        if ch.get("tvg_logo"):
            ET.SubElement(ch_elem, "icon", src=ch["tvg_logo"])

        master_xml.append(ch_elem)
        
        # mirror it to the jellyfin specific file if it's a tv channel
        if ch in tv_channels:
            # creating a fresh element to avoid weird xml reference overlaps
            ch_elem_jf = ET.Element("channel", id=ch["tvg_id"])
            display_name_jf = ET.SubElement(ch_elem_jf, "display-name")
            display_name_jf.text = ch["display_name"]
            if ch.get("tvg_logo"):
                ET.SubElement(ch_elem_jf, "icon", src=ch["tvg_logo"])
            jellyfin_xml.append(ch_elem_jf)

    # 3. FETCH OR GENERATE PROGRAMMES
    for ch in tv_channels + fm_channels:
        programmes = None
        epg_url = ch.get("epg_url")
        
        if epg_url:
            print(f"fetching schedule for {ch['display_name']}...")
            programmes = fetch_external_epg(epg_url, ch["tvg_id"])
            
        # if the fetch failed or there was no url to begin with, run the placeholder generator
        if not programmes:
            print(f"generating fallback placeholders for {ch['display_name']}...")
            programmes = generate_floptropica_placeholders(ch["tvg_id"], ch["display_name"], ch.get("tvg_logo"))

        # append the snatched or generated blocks to our master xmls
        for prog in programmes:
            master_xml.append(prog)
            if ch in tv_channels:
                # deep copy the element by converting to string and back so jellyfin gets a clean clone
                jf_prog = ET.fromstring(ET.tostring(prog))
                jellyfin_xml.append(jf_prog)

    # 4. WRITE THE XML FILES
    tree_master = ET.ElementTree(master_xml)
    ET.indent(tree_master, space="  ", level=0) # makes the xml pretty instead of a one-line block
    tree_master.write(master_epg_path, encoding="utf-8", xml_declaration=True)

    tree_jellyfin = ET.ElementTree(jellyfin_xml)
    ET.indent(tree_jellyfin, space="  ", level=0)
    tree_jellyfin.write(jellyfin_epg_path, encoding="utf-8", xml_declaration=True)

    # 5. GENERATE THE M3U PLAYLISTS WITH THE NEW EPG LINKS
    # assuming you host these on cable.fnswe.me
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

    # 6. RADIO FILES
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

    print("the script absolutely devoured and left no crumbs. epgs fetched, placeholders drafted, and playlists compiled.")

if __name__ == "__main__":
    build_the_broadcasting_empire()