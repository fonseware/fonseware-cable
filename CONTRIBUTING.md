#### contribute to fonseware-cable
**we accept pull requests from original broadcasters only.** if you have a stream that meets the requirements below, we welcome you to submit it and share it with the world.

#### submission requirements
1.  **originality:** you must own the content or have explicit permission to restream it.
2.  **format:** streams must be **hls (.m3u8)**. (rtmp/rtsp are not supported directly by most players).
3.  **stability:** your stream must be 24/7 (or have a scheduled loop). dead streams will have their channel number revoked.
4.  **metadata:** you must provide a logo (png) and a channel name.

#### proof of ownership
to prevent scraping/stealing, you must prove you control the stream source.

**method a: the domain check**
the stream url domain matches your github profile website or email domain.

**method b: the text file check**
if you are hosting on a vps or 3rd party, upload a text file to your server at:
`http://your-stream-domain.com/fonseware.txt`
* *content of file:* `verified for fonseware-cable by [yourgithubusername]`

#### how to submit
1.  fork this repository.
2.  add your logo to the `/media` folder.
3.  edit `tv.m3u` or `fm.m3u`.
4.  find the first `[vacant]` slot you like.
5.  replace the placeholder with your details.

