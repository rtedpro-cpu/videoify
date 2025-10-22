# Videoify

A tool which hides a specified file at the end of a video file.


# Getting Started

Download the videoify.py script and use Python 3 to execute it.


```bash
Usage:
  python3 videoify.py write <input-file> [out.mp4]
  python3 videoify.py read <mp4-with-trailer> [out-file]
Notes:
- The script creates a playable MP4 and appends the raw bytes after it.
- The trailer format: MARKER + 8-byte length + raw bytes.
- Players usually ignore the trailer; the file remains a standard MP4.
```
