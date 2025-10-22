import sys
import os
import struct
import imageio
import numpy as np
MARKER = b"VIDEOIFYv1"
MARKER_LEN = len(MARKER)
LEN_FMT = "<Q"
def make_minimal_mp4(path, width=1280, height=720, seconds=1, fps=30):
    """Create a minimal MP4"""
    writer = imageio.get_writer(path, fps=fps, codec="libx264", ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "28"])
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frames = int(seconds * fps)
    for i in range(frames):
        writer.append_data(frame)
    writer.close()
def write_mode(infile, out_mp4=None, make_video=True):
    """Write infile -> out_mp4 and append raw bytes after MP4."""
    if not os.path.exists(infile):
        print("Input file not found:", infile); return
    if out_mp4 is None:
        out_mp4 = infile + ".mp4"
    if make_video:
        make_minimal_mp4(out_mp4)
        print(f"Created playable MP4: {out_mp4}")
    else:
        if not os.path.exists(out_mp4):
            raise FileNotFoundError("out_mp4 not found and make_video=False")
    with open(infile, "rb") as f:
        data = f.read()
    with open(out_mp4, "ab") as out:
        out.write(MARKER)
        out.write(struct.pack(LEN_FMT, len(data)))
        out.write(data)
    print(f"Appended {len(data)} bytes to {out_mp4}. Final size: {os.path.getsize(out_mp4)} bytes")
def read_mode(mp4path, outpath=None):
    """Read appended data from mp4path and write to outpath (or mp4path.decoded)."""
    if not os.path.exists(mp4path):
        print("MP4 not found:", mp4path); return
    filesize = os.path.getsize(mp4path)
    tail_read = min(filesize, 200 * 1024 * 1024)  # 200 MB cap for safety
    with open(mp4path, "rb") as f:
        f.seek(filesize - tail_read)
        tail = f.read()
    idx = tail.rfind(MARKER)
    if idx == -1:
        print("File is not a supported VIDEOIFY video.")
        return
    marker_pos = (filesize - tail_read) + idx
    len_pos = marker_pos + MARKER_LEN
    with open(mp4path, "rb") as f:
        f.seek(len_pos)
        len_bytes = f.read(struct.calcsize(LEN_FMT))
        if len(len_bytes) != struct.calcsize(LEN_FMT):
            print("Failed to read length field after marker.")
            return
        data_len = struct.unpack(LEN_FMT, len_bytes)[0]
        data_pos = len_pos + struct.calcsize(LEN_FMT)
        f.seek(data_pos)
        data = f.read(data_len)
        if len(data) != data_len:
            print(f"Warning: expected {data_len} bytes but read {len(data)} bytes (file may be truncated).")
    if outpath is None:
        outpath = mp4path + ".decoded"
    with open(outpath, "wb") as out:
        out.write(data)
    print(f"Extracted {len(data)} bytes to {outpath}")
def usage():
    print("Usage:")
    print("  python3 videoify.py write <input-file> [out.mp4]")
    print("  python3 videoify.py read <mp4-with-trailer> [out-file]")
    print()
    print("Notes:")
    print("- The script creates a playable MP4 and appends the raw bytes after it.")
    print("- The trailer format: MARKER + 8-byte length + raw bytes.")
    print("- Players usually ignore the trailer; the file remains a standard MP4.")
if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage(); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "write":
        infile = sys.argv[2]
        out_mp4 = sys.argv[3] if len(sys.argv) >= 4 else None
        write_mode(infile, out_mp4)
    elif cmd == "read":
        mp4path = sys.argv[2]
        outpath = sys.argv[3] if len(sys.argv) >= 4 else None
        read_mode(mp4path, outpath)
    else:
        usage()
