#### contribute to fonseware-cable

**we accept submissions from original broadcasters only.** if you have a stream that meets the requirements below, we welcome you to submit it and share it with the world.

#### 🌶️ content guidelines

> any language is completely fine. broadcast in whatever language you prefer. however, we do have some ground rules:
> - **the good stuff:** indie and original content is highly encouraged. university television, community channels, and generic networks are a huge yes. sports, movies, and drama are acceptable _only if_ you actually have the legal coverage and rights to broadcast them.
> - **nsfw content:** porn and nudity are allowed, but you _must_ clearly mention it, group them appropriately, and place them at the very bottom of the channel list. illegal porn or illegal adult broadcasts are strictly prohibited and will result in an immediate ban.
> - **religious content:** religious content is acceptable, but keep it respectful. there is absolutely zero tolerance for racism, hate speech, or dehumanising any group of people. if your stream contains this, you will be blocked.
> - **the absolute no-gos:** no terrorism. period. there are no exceptions to this rule.

#### 📋 suggested channel order

> while contributors can submit their stream to any vacant channel slot they prefer, we highly encourage following this general order to keep the guide organised, similar to a traditional tv service:

| ch. no                         | use                                                           |
| ------------------------------ | ------------------------------------------------------------- |
| **001 - 020**                  | local & community channels (including university tv)          |
| **021 - 040**                 | news & information                                            |
| **041 - 060**                 | music & radio streams                                         |
| **061 - 080**                 | kids & family                                                 |
| **081 - 100**                 | edutainment & documentaries                                   |
| **101 - 120**                 | sports (legal broadcasts only)                                |
| **121 - 140**                 | movies & entertainment                                        |
| **141 - 160**                 | regional & international languages (e.g., hindi, tamil, etc.) |
| **161 - 180**                 | high definition (hd) showcases & generic networks             |
| **181 - 199**                 | vacant / overflow channels                                    |
| **200+ (bottom of playlist)** | adult, nsfw, and porn channels (strictly legal content only)  |

#### 📩 submission requirements

> 1.  **originality:** you must own the content or have explicit permission to restream it.
> 2.  **format:** streams must be **hls (.m3u8)**. (rtmp/rtsp are not supported directly by most players).
> 3.  **stability:** your stream must be 24/7 (or have a scheduled loop). dead streams will have their channel number revoked.
> 4.  **metadata:** you must provide a logo (png) and a channel name.

#### 🎖️ proof of ownership

> to prevent scraping and stealing, you must prove you control the stream source.
> 
> **method a: the domain check**
> the stream url domain matches your github profile website or email domain.
> 
> **method b: the text file check**
> if you are hosting on a vps or 3rd party, upload a text file to your server at: `http://your-stream-domain.com/fonseware.txt`
> 
> ```txt
> verified for fonseware-cable by [yourgithubusername]
> ```

#### 📲 how to submit

> you can submit your channel by opening an issue, sending an email to hello@fonseware.com, or submitting a pull request (pr).
> 
> whichever way you choose to submit, you **must** provide your channel data in this exact json format:
> go to the scripts folder and edit the tv.json or fm.json. any other edits in other files will not be accepted in the pr. 
> 
> please note that once the channel is added an evaluation will take place to meet the criteria and then the channel will be added to the list at the next playlist generation cycle.
> 
> ```json
> {
>   "tvg_id": "002",
>   "tvg_logo": "http://cable.fnswe.me/media/> fw-teve-logo2-light.png",
>   "group_title": "General",
>   "tvg_chno": "02",
>   "tvg_country": "LK",
>   "tvg_language": "English",
>   "tvg_name": "FBS teve",
>   "radio": "false",
>   "display_name": "FBS teve",
>   "url": "https://host.fonseware.com/hls/stream.m3u8",
>   "epg_url": "https://host.fonseware.com/epg/> fbs_schedule.xml"
> }
> ```

#### 📅 providing an epg (electronic program guide)

> if you have a custom broadcast schedule, you can host your own epg xml file and provide the link in the `epg_url` field of your json submission.
> your epg must be in standard xmltv format. the `channel id` in your xml **must** match the `tvg_id` you are claiming in your json submission. if your epg fetch fails or you leave the `epg_url` blank, our system will automatically generate 30-minute fallback placeholder blocks so your channel doesn't appear empty.
> 
> **example epg format:**
> 
> ```xml
> <?xml version="1.0" encoding="UTF-8"?>
> <tv generator-info-name="fonseware network" > source-info-name="fonseware-cable">
>   <channel id="002"<display-name>FBS teve</display-name>
>     <icon src="http://cable.fnswe.me/media/> fw-teve-logo2-light.png"/>
>   </channel>
> 
>   <programme start="20260308120000 +0000" > stop="20260308140000 +0000" channel="002">
>     <title lang="en">Afternoon Movie Feature</title>
>     <desc lang="en">A broadcast of an independent short > film.</desc>
>     <category lang="en">Movies &amp; Entertainment</> category>
>     <date>2026</date>
>     <icon src="http://cable.fnswe.me/media/placeholder1.> jpg"/>
>     <episode-num system="xmltv_ns">0.0.0/1</episode-num>
>   </programme>
> 
>   <programme start="20260308140000 +0000" > stop="20260308150000 +0000" channel="002">
>     <title lang="en">Community News</title>
>     <desc lang="en">Daily updates from the local > community.</desc>
>     <category lang="en">News &amp; Information</> category>
>     <date>2026</date>
>     </programme>
> </tv>
> ```

#### 💁🏻‍♂️ **want to submit a pr? here are the steps:**

> 1. fork this repository.
> 2. add your logo to the `/media` folder.
> 3. navigate to `scripts/tv.json`.
> 4. find the first `[vacant]` channel block you like.
> 5. replace the stock data in that block with your custom json data (like the example above).
> 6. run `generate.py` in that same folder to update the  playlists.
> 7. submit your pr. i will review it manually and process it.

#### ⚖️ directory management & rights

> please note that our goal of 200 channels is not a  strict limit. multiple channels can continue to be  added beyond this number. once the directory reaches a self-sufficient number of  active channels, we reserve the right to reorder the  channel list accordingly to maintain a structured  guide. furthermore, we reserve the right to make  changes to the directory, modify listings, or terminate  any stream at any time, with or without reason.