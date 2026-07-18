import importlib.util, os, tempfile, subprocess
spec = importlib.util.spec_from_file_location("bt", r"R:\YouTube-Channel\tools\video\build_tour.py")
bt = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt)
real = r"C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents\Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Latitude Margaritaville Watersound\Models\Island Collection - Single-Family Homes\Trinidad Bay\gallery\Kitchen.jpg"
w = tempfile.mkdtemp()
kb = os.path.join(w, "kb.mp4"); bt.make_kenburns(real, "Cap", kb, 4.6, True, False)
o = subprocess.run(["ffprobe","-v","error","-show_entries","stream=nb_frames,duration","-of","default=nw=1",kb], capture_output=True, text=True).stdout
print("REAL image kenburns:", o.replace("\n", "  "))
