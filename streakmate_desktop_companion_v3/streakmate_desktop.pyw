import json, os, threading, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime
import tkinter as tk

APP_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "StreakMate"
STATE_FILE = APP_DIR / "state.json"
PREFS_FILE = APP_DIR / "preferences.json"
HOST, PORT = "127.0.0.1", 8765
LEETCODE_URL = "https://leetcode.com/problemset/"
APP_DIR.mkdir(parents=True, exist_ok=True)

def read_json(path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default

def write_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_GET(self):
        if self.path.split("?")[0] != "/state":
            self.send_error(404); return
        body=json.dumps(read_json(STATE_FILE,{"streakCount":0,"lastCompletedDate":"","lastAcceptedAt":"","mood":"chill"})).encode()
        self.send_response(200); self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Content-Length",str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        if self.path.split("?")[0] != "/state": self.send_error(404); return
        try:
            n=int(self.headers.get("Content-Length","0")); d=json.loads(self.rfile.read(n).decode())
            safe={"streakCount":max(0,int(d.get("streakCount",0))),
                  "lastCompletedDate":str(d.get("lastCompletedDate",""))[:10],
                  "lastAcceptedAt":str(d.get("lastAcceptedAt",""))[:40],
                  "mood":d.get("mood") if d.get("mood") in ("chill","panic","happy") else "chill",
                  "updatedAt":str(d.get("updatedAt",""))[:40]}
            write_json(STATE_FILE,safe); body=b'{"ok":true}'
            self.send_response(200); self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Content-Length",str(len(body)))
            self.end_headers(); self.wfile.write(body)
        except Exception: self.send_error(400)
    def log_message(self,*args): pass

def start_server():
    try: HTTPServer((HOST,PORT),Handler).serve_forever()
    except OSError: pass

class StreakMate:
    MIN_W, MIN_H = 190, 145
    EDGE = 7
    def __init__(self):
        self.root=tk.Tk()
        self.prefs=read_json(PREFS_FILE,{"mode":"corner","x":80,"y":100,"w":220,"h":150})
        self.mode=self.prefs.get("mode","corner")
        if self.mode not in ("floating","corner"): self.mode="corner"
        self.drag=None; self.resize_data=None
        self.root.overrideredirect(True)  # no title bar, minimize, maximize, or close buttons
        self.root.resizable(False,False)  # resizing is handled manually at the edges
        self.root.configure(bg="#252344")
        w=max(self.MIN_W,int(self.prefs.get("w",220))); h=max(self.MIN_H,int(self.prefs.get("h",150)))
        self.root.geometry(f"{w}x{h}+{self.prefs.get('x',80)}+{self.prefs.get('y',100)}")
        self.root.bind("<Escape>",lambda e:self.close_widget())
        self.root.protocol("WM_DELETE_WINDOW", self.close_widget)

        self.card=tk.Frame(self.root,bg="#252344",highlightthickness=1,highlightbackground="#8C7CF4")
        self.card.pack(fill="both",expand=True)
        self.header=tk.Frame(self.card,bg="#252344",height=24)
        self.header.pack(fill="x",padx=9,pady=(5,0))
        self.title=tk.Label(self.header,text="STREAKMATE",font=("Segoe UI",8,"bold"),fg="#DCD7FF",bg="#252344")
        self.title.pack(side="left")
        self.mode_btn=tk.Button(self.header,text="↔",command=self.toggle_mode,relief="flat",bg="#514A83",fg="white",
            activebackground="#6B60A7",activeforeground="white",font=("Segoe UI",10),padx=5,pady=0,borderwidth=0,cursor="hand2")
        self.mode_btn.pack(side="right")
        self.mascot=tk.Canvas(self.card,width=78,height=68,bg="#252344",highlightthickness=0,cursor="hand2")
        self.mascot.pack(pady=(1,0))
        self.count=tk.Label(self.card,text="🔥 0",font=("Segoe UI",15,"bold"),fg="white",bg="#252344",cursor="hand2")
        self.count.pack()
        self.status=tk.Label(self.card,text="Solve today",font=("Segoe UI",8),fg="#E9E5FF",bg="#252344",cursor="hand2")
        self.status.pack(pady=(1,5))
        for widget in (self.mascot,self.count,self.status):
            widget.bind("<Button-1>",lambda e:webbrowser.open(LEETCODE_URL))
        self.header.bind("<Button-1>",self.start_drag)
        self.title.bind("<Button-1>",self.start_drag)
        self.header.bind("<B1-Motion>",self.drag_window)
        self.title.bind("<B1-Motion>",self.drag_window)
        self.header.bind("<ButtonRelease-1>",self.stop_move)
        self.title.bind("<ButtonRelease-1>",self.stop_move)
        self.card.bind("<Motion>",self.set_cursor)
        self.card.bind("<Button-1>",self.begin_resize)
        self.card.bind("<B1-Motion>",self.resize_window)
        self.card.bind("<ButtonRelease-1>",self.end_resize)
        self.apply_mode()
        self.refresh()
        self.root.mainloop()

    def close_widget(self):
        self.save_prefs()
        self.root.destroy()

    def save_prefs(self):
        self.prefs.update({"mode":self.mode,"x":self.root.winfo_x(),"y":self.root.winfo_y(),
                           "w":self.root.winfo_width(),"h":self.root.winfo_height()})
        write_json(PREFS_FILE,self.prefs)

    def toggle_mode(self):
        self.mode="corner" if self.mode=="floating" else "floating"
        self.apply_mode(); self.save_prefs()

    def apply_mode(self):
        self.root.update_idletasks()
        w=max(self.MIN_W,self.root.winfo_width()); h=max(self.MIN_H,self.root.winfo_height())
        if self.mode=="corner":
            sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+{max(0,sw-w-22)}+{max(0,sh-h-85)}")
            self.mode_btn.config(text="↔")
        else:
            self.root.geometry(f"{w}x{h}+{int(self.prefs.get('x',80))}+{int(self.prefs.get('y',100))}")
            self.mode_btn.config(text="⌖")
        self.root.attributes("-topmost",False)

    def start_drag(self,event):
        if self.mode=="floating":
            self.drag=(event.x_root-self.root.winfo_x(),event.y_root-self.root.winfo_y())
    def drag_window(self,event):
        if self.mode=="floating" and self.drag and not self.resize_data:
            self.root.geometry(f"+{event.x_root-self.drag[0]}+{event.y_root-self.drag[1]}")
    def stop_move(self,event):
        self.drag=None; self.save_prefs()

    def edge_at(self,x,y):
        w,h=self.root.winfo_width(),self.root.winfo_height()
        left=x<self.EDGE; right=x>=w-self.EDGE
        top=y<self.EDGE; bottom=y>=h-self.EDGE
        return ("left" if left else "right" if right else "") + ("top" if top else "bottom" if bottom else "")
    def set_cursor(self,event):
        edge=self.edge_at(event.x,event.y)
        cursor="size_nw_se" if edge in ("lefttop","rightbottom") else "size_ne_sw" if edge in ("righttop","leftbottom") else "size_we" if edge in ("left","right") else "size_ns" if edge in ("top","bottom") else "arrow"
        try: self.root.configure(cursor=cursor)
        except Exception: pass
    def begin_resize(self,event):
        edge=self.edge_at(event.x,event.y)
        if edge:
            self.resize_data={"edge":edge,"x":event.x_root,"y":event.y_root,
                "wx":self.root.winfo_x(),"wy":self.root.winfo_y(),
                "ww":self.root.winfo_width(),"wh":self.root.winfo_height()}
    def resize_window(self,event):
        if not self.resize_data: return
        d=self.resize_data; dx=event.x_root-d["x"]; dy=event.y_root-d["y"]
        x,y,w,h=d["wx"],d["wy"],d["ww"],d["wh"]; edge=d["edge"]
        if "right" in edge: w=max(self.MIN_W,d["ww"]+dx)
        if "bottom" in edge: h=max(self.MIN_H,d["wh"]+dy)
        if "left" in edge:
            w=max(self.MIN_W,d["ww"]-dx); x=d["wx"]+d["ww"]-w
        if "top" in edge:
            h=max(self.MIN_H,d["wh"]-dy); y=d["wy"]+d["wh"]-h
        self.root.geometry(f"{w}x{h}+{x}+{y}")
    def end_resize(self,event):
        self.resize_data=None; self.save_prefs()

    def draw_mascot(self,mood):
        c=self.mascot; c.delete("all")
        # Draw a custom little lilac creature with headphones; no system emoji font required.
        face={"chill":"😌","panic":"😟","happy":"☺"}.get(mood,"☺")
        c.create_oval(15,5,63,57,fill="#B7A4FF",outline="#E3DBFF",width=2)
        # headphone band + ear cups
        c.create_arc(18,0,60,43,start=5,extent=170,style="arc",outline="#72D8F5",width=5)
        c.create_rectangle(8,23,21,43,fill="#72D8F5",outline="#D7F8FF",width=1)
        c.create_rectangle(57,23,70,43,fill="#72D8F5",outline="#D7F8FF",width=1)
        if mood=="panic":
            c.create_oval(27,24,33,31,fill="#332A6D",outline="")
            c.create_oval(45,24,51,31,fill="#332A6D",outline="")
            c.create_oval(36,38,43,46,fill="#332A6D",outline="#332A6D")
            c.create_line(25,19,33,17,fill="#332A6D",width=2)
            c.create_line(45,17,53,19,fill="#332A6D",width=2)
        elif mood=="happy":
            c.create_arc(25,22,36,34,start=200,extent=140,style="arc",outline="#332A6D",width=3)
            c.create_arc(42,22,53,34,start=200,extent=140,style="arc",outline="#332A6D",width=3)
            c.create_arc(30,31,49,48,start=200,extent=140,style="arc",outline="#332A6D",width=3)
            c.create_oval(22,35,28,40,fill="#F28EB5",outline="")
            c.create_oval(50,35,56,40,fill="#F28EB5",outline="")
        else:
            c.create_oval(27,23,34,32,fill="#332A6D",outline="")
            c.create_oval(44,23,51,32,fill="#332A6D",outline="")
            c.create_oval(29,24,31,26,fill="white",outline="")
            c.create_oval(46,24,48,26,fill="white",outline="")
            c.create_arc(31,32,48,44,start=200,extent=140,style="arc",outline="#332A6D",width=2)

    def refresh(self):
        state=read_json(STATE_FILE,{})
        count=int(state.get("streakCount",0) or 0)
        mood=state.get("mood","chill")
        today=datetime.now().astimezone().strftime("%Y-%m-%d")
        if state.get("lastCompletedDate","")==today: mood="happy"
        else:
            last=state.get("lastAcceptedAt","")
            if last:
                try:
                    dt=datetime.fromisoformat(last.replace("Z","+00:00"))
                    if dt.tzinfo is None: dt=dt.astimezone()
                    mood="panic" if (datetime.now().astimezone()-dt.astimezone()).total_seconds()>=23*3600 else "chill"
                except Exception: pass
        self.draw_mascot(mood)
        self.count.config(text=f"🔥 {count}")
        if mood=="happy": bg,edge,fg,msg="#173F32","#38D996","#D5FFEA","Saved ✓"
        elif mood=="panic": bg,edge,fg,msg="#4A242D","#FF675C","#FFE0DD","Save your streak!"
        else: bg,edge,fg,msg="#252344","#8C7CF4","#E9E5FF","Solve today"
        self.root.configure(bg=bg); self.card.configure(bg=bg,highlightbackground=edge)
        self.header.configure(bg=bg); self.title.configure(bg=bg)
        self.mascot.configure(bg=bg); self.count.configure(bg=bg); self.status.configure(bg=bg)
        self.status.config(text=msg,fg=fg); self.mode_btn.configure(bg="#514A83")
        self.root.after(5000,self.refresh)

if __name__=="__main__":
    threading.Thread(target=start_server,daemon=True).start()
    StreakMate()
