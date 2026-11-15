"""Builds the 28 s Reel from the 4 carousel slides (ffmpeg): 9:16 canvas, slow zoom, crossfades, silent AAC track.
Slides: 01 cover (3 s), 02 top 10 (6 s), 03 what moved (8 s), 05 method + CTA (6 s), then a screenshot of the live FR tier list page (5 s, "Ta spé est où ? Lien en bio"). Output: RS/reels/."""
import subprocess
from pathlib import Path

RS = Path(r"D:\Site internet\RS")
OUT = RS / "reels" / "reel-tierlist-dps-niveau60-nov15.mp4"
SLIDES = [("carrousel-tierlist-dps-01-couverture.png", 3), ("carrousel-tierlist-dps-02-top10.png", 6),
          ("carrousel-tierlist-dps-03-ce-qui-a-bouge.png", 8), ("carrousel-tierlist-dps-05-methode.png", 6),
          (str(Path(__file__).parent / "reel_assets" / "reel_page_tierlist.png"), 5)]
X = 0.4
FPS = 30

args = ["ffmpeg", "-y", "-loglevel", "error"]
fc = []
for i, (f, d) in enumerate(SLIDES):
    dur = d + (X if i < len(SLIDES) - 1 else 0)
    args += ["-loop", "1", "-t", f"{dur:.2f}", "-framerate", str(FPS), "-i", str((RS / f).resolve())]
    n = int(dur * FPS)
    if f.endswith("reel_page_tierlist.png"):  # full-frame 9:16 page capture + on-screen call to action
        vf = ("scale=1080:1920,drawbox=x=40:y=1450:w=1000:h=150:color=0x1f5bff@0.95:t=fill,"
              "drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='Ta spé est où ? Lien en bio':fontcolor=white:fontsize=56:x=(w-text_w)/2:y=1500,")
    else:
        vf = "scale=1080:1350,pad=1080:1920:0:285:color=0x070a2b,"
    fc.append(f"[{i}:v]{vf}"
              f"zoompan=z='min(1+0.0004*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS},"
              f"format=yuv420p,setsar=1[v{i}]")
prev, t = "v0", SLIDES[0][1]
for i in range(1, len(SLIDES)):
    fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={X}:offset={t:.2f}[x{i}]")
    prev, t = f"x{i}", t + SLIDES[i][1]
args += ["-f", "lavfi", "-t", f"{t + 1:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
args += ["-filter_complex", ";".join(fc), "-map", f"[{prev}]", "-map", f"{len(SLIDES)}:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(OUT)]
subprocess.run(args, check=True)
print(OUT)
