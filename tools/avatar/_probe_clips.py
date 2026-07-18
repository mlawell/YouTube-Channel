import importlib.util, os, tempfile, subprocess
spec = importlib.util.spec_from_file_location("bt", r"R:\YouTube-Channel\tools\video\build_tour.py")
bt = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt)
w = tempfile.mkdtemp()
img = os.path.join(w, "r.jpg")
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=blue:s=1600x1000:d=1","-frames:v","1",img], capture_output=True)
webm = os.path.join(w, "p.webm")
subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=orange:s=200x360:d=3:r=30","-vf","format=yuva420p","-c:v","libvpx-vp9","-pix_fmt","yuva420p","-b:v","0","-crf","30",webm], capture_output=True)
kb = os.path.join(w, "kb.mp4"); bt.make_kenburns(img, "Cap", kb, 4.6, True, False)
pr = os.path.join(w, "pr.mp4"); bt.make_kenburns_presenter(img, "Cap", pr, 3.0, True, webm, 0.62, "bottom-right")
for f in (kb, pr):
    o = subprocess.run(["ffprobe","-v","error","-show_entries","stream=nb_frames,duration","-of","default=nw=1",f], capture_output=True, text=True).stdout
    print(os.path.basename(f), o.replace("\n", "  "))
