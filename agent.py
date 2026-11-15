import ctypes, json, os, sys, time, math, threading, urllib.request, tkinter as tk, winreg
from ctypes import wintypes
import psutil
EVERY, IDLE_AFTER = 10, 120
DIR = os.path.join(os.environ["APPDATA"], "TeamTime"); CFG = os.path.join(DIR, "config.json")
u, k = ctypes.windll.user32, ctypes.windll.kernel32
class LII(ctypes.Structure): _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]
def idle_secs():
    i = LII(); i.cbSize = ctypes.sizeof(i); u.GetLastInputInfo(ctypes.byref(i))
    return (k.GetTickCount() - i.dwTime) / 1000
def front_app():
    pid = wintypes.DWORD(); u.GetWindowThreadProcessId(u.GetForegroundWindow(), ctypes.byref(pid))
    try: return psutil.Process(pid.value).name().removesuffix(".exe")
    except Exception: return "Unknown"
def set_startup(on):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    cmd = f'"{sys.executable}"' if getattr(sys, "frozen", False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    if on: winreg.SetValueEx(key, "TeamTime", 0, winreg.REG_SZ, cmd)
    else:
        try: winreg.DeleteValue(key, "TeamTime")
        except FileNotFoundError: pass
def send(cfg, app, idle):
    data = json.dumps({"app": app, "idle": idle, "secs": EVERY}).encode()
    req = urllib.request.Request(cfg["server"].rstrip("/") + "/api/track", data,
        {"Authorization": "Bearer " + cfg["token"], "Content-Type": "application/json"})
    try: urllib.request.urlopen(req, timeout=5)
    except Exception: pass

def light():
    try: return winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"), "AppsUseLightTheme")[0] == 1
    except Exception: return False
PAL = {"light": ("#f4f5fb", "#1c1f2e", "#ffffff", "#6c5ce7", "#6b7089"), "dark": ("#0f1117", "#e8eaf2", "#232736", "#7c6cff", "#8b90a5")}
TF = os.path.join(DIR, "theme.txt")
def setpal(n):
    global BG, FG, CARD, ACC, MUT, THEME
    THEME = n; BG, FG, CARD, ACC, MUT = PAL[n]
try: setpal(open(TF).read().strip())
except Exception: setpal("light" if light() else "dark")
T = {"en": dict(welcome="Welcome to TeamTime", srv="Server URL (from your admin)", tok="Your token (from your admin)", start="Start", startup="Start with Windows",
  consent="I understand this app shares the app I'm using and my active/idle time with my admin. It does not record keystrokes, screenshots or window titles.",
  tick="Please tick the consent box first.", fill="Enter the server URL and token.", today="Time worked today", brk="Break time ", out="Clocked out", working="Working: ", onbreak="On a break", idle="Idle",
  cin="Clock in", brkb="Take a break", res="Resume work", cout="Clock out", gm="Good morning", ga="Good afternoon", ge="Good evening", gn="Good night",
  note="While you are working, your admin sees the app in front and active/idle time. Nothing else: no keystrokes, screenshots or window titles. On a break or clocked out, nothing is sent."),
 "mk": dict(welcome="Добредојдовте во TeamTime", srv="URL на серверот (од вашиот админ)", tok="Вашиот токен (од вашиот админ)", start="Почни", startup="Стартувај со Windows",
  consent="Разбирам дека апликацијата му ги споделува на мојот админ апликацијата што ја користам и времето на активност/неактивност. Не снима притисоци на тастатура, екрани ниту наслови на прозорци.",
  tick="Прво штиклирајте го полето за согласност.", fill="Внесете URL на серверот и токен.", today="Работено денес", brk="Време на пауза ", out="Одјавен", working="Работи: ", onbreak="На пауза", idle="Неактивен",
  cin="Пријави се", brkb="Земи пауза", res="Продолжи со работа", cout="Одјави се", gm="Добро утро", ga="Добар ден", ge="Добра вечер", gn="Добра ноќ",
  note="Додека работите, вашиот админ ја гледа апликацијата пред вас и времето на активност/неактивност. Ништо повеќе: без притисоци на тастатура, екрани или наслови на прозорци. На пауза или одјавени, ништо не се испраќа.")}
T["en"].update(act="Active", idl="Idle", tip="You've been working for a while. Time for a break!")
T["mk"].update(act="Активно", idl="Неактивно", tip="Работите веќе подолго. Време е за пауза!")
T["en"].update(goal="of daily goal (8h)", left="left to reach goal", topapps="Top apps today", noapps="No activity yet")
T["mk"].update(goal="од дневната цел (8ч)", left="уште до целта", topapps="Најкористени апликации денес", noapps="Сè уште нема активност")
LF = os.path.join(DIR, "lang.txt")
def deflang():
    try: return open(LF).read().strip() or "en"
    except Exception:
        try: return "mk" if (k.GetUserDefaultUILanguage() & 0x3ff) == 0x2f else "en"
        except Exception: return "en"
LANG = [deflang()]
def t(x): return T[LANG[0]][x]
root = tk.Tk(); root.title("TeamTime"); root.geometry("400x570"); root.configure(bg=BG); root.resizable(False, False)
def label(txt, size=10, color=FG): return tk.Label(root, text=txt, bg=BG, fg=color, font=("Segoe UI", size), wraplength=360, justify="center")
def clear():
    for w in root.winfo_children(): w.destroy()
def button(txt, cmd): return tk.Button(root, text=txt, command=cmd, bg=ACC, fg="white", relief="flat", padx=22, pady=7, font=("Segoe UI", 10, "bold"))
def langbtn(redraw):
    def sw():
        LANG[0] = "mk" if LANG[0] == "en" else "en"; os.makedirs(DIR, exist_ok=True); open(LF, "w").write(LANG[0]); redraw()
    tk.Button(root, text="MK" if LANG[0] == "en" else "EN", command=sw, bg=CARD, fg=FG, relief="flat", font=("Segoe UI", 8, "bold"), padx=8).place(x=345, y=8)
def call(cfg, path, body=None):
    req = urllib.request.Request(cfg["server"].rstrip("/") + path, json.dumps(body).encode() if body is not None else None,
        {"Authorization": "Bearer " + cfg["token"], "Content-Type": "application/json"})
    try: return json.loads(urllib.request.urlopen(req, timeout=5).read())
    except Exception: return None
def greet(name):
    h = time.localtime().tm_hour
    return t("gm" if 5 <= h < 12 else "ga" if 12 <= h < 18 else "ge" if 18 <= h < 22 else "gn") + ", " + name
def hm(s): s = int(s); return f"{s//3600}h {s%3600//60}m" if s >= 3600 else f"{s//60}m"
def hms(s): s = int(s); return f"{s//3600:02}:{s%3600//60:02}:{s%60:02}"
def setimg(lbl, d):
    try: im = tk.PhotoImage(data=d.split(",", 1)[1]).subsample(2, 2) if d else None
    except Exception: im = None
    lbl.image = im; lbl.config(image=im if im else "")
state = {"status": "out", "worked": 0, "brk": 0, "t": 0, "name": "", "now": "", "pic": "", "team": {"name": "", "pic": ""}}
def sync(r):
    if r and "status" in r: state.update(r, t=time.time())
GEN, NET, Q = [0], [False], []

import io, base64
try: from PIL import Image, ImageDraw, ImageTk
except Exception: Image = None
def circ(d, s):
    im = Image.open(io.BytesIO(base64.b64decode(d.split(",", 1)[1]))).convert("RGBA").resize((s*4, s*4))
    m = Image.new("L", (s*4, s*4), 0); ImageDraw.Draw(m).ellipse((0, 0, s*4-1, s*4-1), fill=255); im.putalpha(m)
    return ImageTk.PhotoImage(im.resize((s, s), Image.LANCZOS))
def pill(c, x1, y1, x2, y2, fill, outline=None):
    h, ym = y2 - y1, (y1 + y2) / 2
    if outline: c.create_line(x1 + h/2, ym, x2 - h/2, ym, width=h, capstyle="round", fill=outline)
    i = 2 if outline else 0
    c.create_line(x1 + h/2, ym, x2 - h/2, ym, width=h - i*2, capstyle="round", fill=fill)
def F(n, bold=False): return ("Segoe UI", n, "bold") if bold else ("Segoe UI", n)
def mix(a, b, k):
    x = [int(a[i:i+2], 16) for i in (1, 3, 5)]; y = [int(b[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(p + (q - p) * k) for p, q in zip(x, y))
def rr(c, x1, y1, x2, y2, r, **kw):
    p = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return c.create_polygon(p, smooth=True, **kw)

def tracking(cfg):
    clear(); GEN[0] += 1; gen = GEN[0]; root.geometry("400x660"); root.configure(bg=BG)
    c = tk.Canvas(root, width=400, height=660, bg=BG, highlightthickness=0); c.pack()
    regs, hover, press, mode, an, cache = [], [None], [None], [0], {"ang": 0, "bars": {}}, {}
    GOAL = 8 * 3600
    def go(a): threading.Thread(target=lambda: sync(call(cfg, "/api/clock", {"action": a})), daemon=True).start()
    def img(key, d, s):
        if not d: return None
        if cache.get(key, (None,))[0] != d:
            try: cache[key] = (d, circ(d, s) if Image else tk.PhotoImage(data=d.split(",", 1)[1]).subsample(2, 2))
            except Exception: cache[key] = (d, None)
        return cache[key][1]
    def avatar(x, y, s, key, d, ch, big):
        im = img(key, d, s)
        c.create_oval(x-3, y-3, x+s+3, y+s+3, outline=ACC, width=2)
        if im: c.create_image(x, y, image=im, anchor="nw")
        else: c.create_oval(x, y, x+s, y+s, fill=ACC, outline=""); c.create_text(x+s/2, y+s/2, text=ch, fill="white", font=F(big, True))
    def btn(x1, y1, x2, y2, name, txt, primary=False, size=10):
        hov, dn = hover[0] == name, press[0] == name
        base = ACC if primary else CARD
        fill = mix(base, "#ffffff" if primary or THEME == "dark" else ACC, .2) if hov else base
        d = 2 if dn else 0
        if not dn: pill(c, x1, y1 + 3, x2, y2 + 3, mix(BG, "#000000", .14))
        pill(c, x1, y1 + d, x2, y2 + d, fill, None if primary else mix(MUT, BG, .7))
        c.create_text((x1 + x2) / 2, (y1 + y2) / 2 + d, text=txt, fill="white" if primary else FG, font=F(size, True))
        regs.append((x1, y1, x2, y2, name))
    def act(n):
        if n in ("in", "break", "resume", "out"): go(n)
        elif n == "ring": mode[0] = (mode[0] + 1) % 3
        elif n == "lang":
            LANG[0] = "mk" if LANG[0] == "en" else "en"; os.makedirs(DIR, exist_ok=True); open(LF, "w").write(LANG[0])
        elif n == "theme":
            setpal("dark" if THEME == "light" else "light"); os.makedirs(DIR, exist_ok=True); open(TF, "w").write(THEME)
            root.configure(bg=BG); c.configure(bg=BG)
    def at(e): return next((n for x1, y1, x2, y2, n in regs if x1 <= e.x <= x2 and y1 <= e.y <= y2), None)
    def motion(e): n = at(e); hover[0] = n; c.config(cursor="hand2" if n else "")
    def release(e):
        n = at(e)
        if n and n == press[0]: act(n)
        press[0] = None
    c.bind("<Motion>", motion); c.bind("<Leave>", lambda e: hover.__setitem__(0, None))
    c.bind("<ButtonPress-1>", lambda e: press.__setitem__(0, at(e))); c.bind("<ButtonRelease-1>", release)
    def net():
        while True:
            sync(call(cfg, "/api/me"))
            if state["status"] == "working":
                idle, app = idle_secs() > IDLE_AFTER, front_app()
                state["now"] = t("idle") if idle else app
                item = {"app": app, "idle": idle, "secs": EVERY}
                while Q and call(cfg, "/api/track", Q[0]) is not None: Q.pop(0)
                if Q or call(cfg, "/api/track", item) is None: Q.append(item); del Q[:-360]
            time.sleep(EVERY)
    def frame():
        if gen != GEN[0]: return
        try:
            now = time.time(); s = state["status"]; el = now - state["t"] if state["t"] else 0
            w = state["worked"] + (el if s == "working" else 0); b = state["brk"] + (el if s == "break" else 0)
            c.delete("all"); regs.clear()
            for i, (ox, oy, rad, col) in enumerate(((60, 90, 150, ACC), (350, 570, 180, "#00b894"), (390, 250, 110, "#ff9ff3"))):
                px, py = ox + 18 * math.sin(now * .35 + i * 2), oy + 18 * math.cos(now * .3 + i)
                c.create_oval(px - rad, py - rad, px + rad, py + rad, fill=mix(col, BG, .9), outline="")
            avatar(16, 12, 48, "team", state["team"].get("pic"), "👥", 16)
            c.create_text(78, 36, text=state["team"].get("name") or "TeamTime", anchor="w", fill=FG, font=F(13, True))
            btn(300, 20, 340, 52, "theme", "☀" if THEME == "dark" else "🌙", size=11); btn(348, 20, 390, 52, "lang", "MK" if LANG[0] == "en" else "EN", size=9)
            avatar(16, 78, 52, "me", state["pic"], (state["name"] or "?")[0].upper(), 18)
            c.create_text(82, 94, text=greet(state["name"]), anchor="w", fill=ACC, font=F(14, True))
            c.create_text(82, 116, text=time.strftime("%H:%M"), anchor="w", fill=MUT, font=F(10))
            cx, cy, R = 200, 236, 84; pr = (1 + math.sin(now * 4)) / 2 if s == "working" else 0
            if s == "working":
                rr_ = R + 20 + pr * 4; c.create_oval(cx - rr_, cy - rr_, cx + rr_, cy + rr_, outline=mix(ACC, BG, .82 - .1 * pr), width=2)
            c.create_oval(cx - R + 8, cy - R + 12, cx + R - 8, cy + R - 4, fill=mix(BG, "#000000", .08), outline="")
            c.create_oval(cx - R + 10, cy - R + 10, cx + R - 10, cy + R - 10, fill=CARD, outline=mix(MUT, BG, .85))
            c.create_oval(cx - R - 7, cy - R - 7, cx + R + 7, cy + R + 7, outline=mix(MUT, BG, .82), width=14)
            an["ang"] += (min(w / GOAL, 1) * 359.9 - an["ang"]) * .12
            if an["ang"] > .5:
                pc = "#00b894" if w >= GOAL else ACC; th = math.radians(90 - an["ang"])
                c.create_arc(cx - R, cy - R, cx + R, cy + R, start=90, extent=-an["ang"], style="arc", outline=pc, width=14)
                ex, ey = cx + R * math.cos(th), cy - R * math.sin(th)
                c.create_oval(cx - 7, cy - R - 7, cx + 7, cy - R + 7, fill=pc, outline="")
                c.create_oval(ex - 7, ey - 7, ex + 7, ey + 7, fill=pc, outline=""); c.create_oval(ex - 3, ey - 3, ex + 3, ey + 3, fill="white", outline="")
            m = mode[0]
            c.create_text(cx, cy - 6, text=hms(w) if m == 0 else f"{int(w / GOAL * 100)}%" if m == 1 else hm(max(GOAL - w, 0)), fill=FG, font=F(26 if m == 0 else 30, True))
            c.create_text(cx, cy + 28, text=t(("today", "goal", "left")[m]), fill=MUT, font=F(9))
            regs.append((cx - R, cy - R, cx + R, cy + R, "ring"))
            col = {"out": MUT, "working": "#00b894", "break": "#f5a623"}[s]
            txt = {"out": t("out"), "working": t("working") + state["now"], "break": t("onbreak")}[s]
            wpx = len(txt) * 7 + 46; x1 = 200 - wpx / 2
            pill(c, x1, 332, x1 + wpx, 360, mix(col, BG, .85), mix(col, BG, .55))
            c.create_oval(x1 + 18 - 8 - pr * 3, 346 - 8 - pr * 3, x1 + 18 + 8 + pr * 3, 346 + 8 + pr * 3, fill=mix(col, BG, .7), outline="")
            c.create_oval(x1 + 13, 341, x1 + 23, 351, fill=col, outline="")
            c.create_text(x1 + 32, 346, text=txt, anchor="w", fill=FG, font=F(10, True))
            if s == "out": btn(100, 370, 300, 414, "in", t("cin"), True, 11)
            else:
                btn(56, 370, 196, 414, "break" if s == "working" else "resume", t("brkb") if s == "working" else t("res"), s != "working")
                btn(204, 370, 344, 414, "out", t("cout"))
            if s == "working" and state.get("stretch", 0) + el >= 5400:
                pill(c, 16, 424, 384, 454, mix("#f5a623", BG, .82), "#f5a623"); c.create_text(200, 439, text=t("tip"), fill=FG, font=F(9, True))
            for i, (k, v) in enumerate((("act", state.get("active", 0)), ("idl", state.get("idle", 0)), ("brk", b))):
                x = 16 + i * 124
                rr(c, x, 465, x + 112, 521, 20, fill=mix(BG, "#000000", .1)); rr(c, x, 462, x + 112, 518, 20, fill=CARD, outline=mix(MUT, BG, .82))
                c.create_text(x + 56, 478, text=t(k).strip(), fill=MUT, font=F(8)); c.create_text(x + 56, 499, text=hm(v), fill=FG, font=F(14, True))
            c.create_text(18, 538, text=t("topapps"), anchor="w", fill=FG, font=F(10, True))
            top = sorted(state.get("apps", {}).items(), key=lambda x: -x[1])[:3]
            if not top: c.create_text(18, 566, text=t("noapps"), anchor="w", fill=MUT, font=F(9))
            for i, (a, v) in enumerate(top):
                y = 560 + i * 34; wd = an["bars"].get(a, 0); wd += (v / top[0][1] * 360 - wd) * .15; an["bars"][a] = wd
                c.create_text(18, y, text=a, anchor="w", fill=FG, font=F(9)); c.create_text(382, y, text=hm(v), anchor="e", fill=MUT, font=F(9))
                c.create_line(20, y + 16, 380, y + 16, width=8, capstyle="round", fill=mix(MUT, BG, .82))
                if wd > 8: c.create_line(20, y + 16, 20 + wd, y + 16, width=8, capstyle="round", fill=ACC)
        finally: root.after(50, frame)
    if not NET[0]: NET[0] = True; threading.Thread(target=net, daemon=True).start()
    frame()

def setup():
    clear(); langbtn(setup)
    label(t("welcome"), 16, ACC).pack(pady=(24, 8))
    label(t("srv")).pack(); s = tk.Entry(root, width=44); s.insert(0, "http://"); s.pack(pady=(2, 8))
    label(t("tok")).pack(); tk_ = tk.Entry(root, width=44); tk_.pack(pady=(2, 10))
    c, st = tk.IntVar(), tk.IntVar(value=1)
    opt = dict(bg=BG, fg=FG, selectcolor=BG, activebackground=BG, activeforeground=FG, wraplength=340, justify="left")
    tk.Checkbutton(root, text=t("consent"), variable=c, **opt).pack(padx=20, anchor="w")
    tk.Checkbutton(root, text=t("startup"), variable=st, **opt).pack(padx=20, anchor="w", pady=4)
    err = label("", 9, "#ff6b81"); err.pack()
    def go():
        if not c.get(): return err.config(text=t("tick"))
        if not tk_.get().strip() or len(s.get()) < 10: return err.config(text=t("fill"))
        cfg = {"server": s.get().strip(), "token": tk_.get().strip()}
        os.makedirs(DIR, exist_ok=True); json.dump(cfg, open(CFG, "w")); set_startup(bool(st.get())); tracking(cfg)
    button(t("start"), go).pack(pady=8)

tracking(json.load(open(CFG))) if os.path.exists(CFG) else setup()
root.mainloop()