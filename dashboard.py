import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from backend import SmartScanEngine
from benchmark import run_benchmark
from config import *

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False


class SmartScanDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('1540x940')
        self.minsize(1220, 760)
        self.configure(bg=BG)
        self.engine = SmartScanEngine()
        self.auto = False
        self.bench = None
        self.bench_figures = []
        self.style()
        self.build()
        self.refresh()

    def style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('TButton', background=PANEL_2, foreground=TEXT, borderwidth=0,
                    padding=(12, 8), font=(FONT, 9, 'bold'))
        s.map('TButton', background=[('active', CYAN_DARK)], foreground=[('active', WHITE)])
        s.configure('Treeview', background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, rowheight=28, borderwidth=0, font=(FONT, 9))
        s.configure('Treeview.Heading', background=PANEL_2, foreground=CYAN,
                    font=(FONT, 8, 'bold'), borderwidth=0)
        s.configure('TNotebook', background=BG, borderwidth=0)
        s.configure('TNotebook.Tab', background=BG_2, foreground=MUTED,
                    padding=(14, 7), font=(FONT, 8, 'bold'))
        s.map('TNotebook.Tab', background=[('selected', PANEL_2)],
              foreground=[('selected', CYAN)])

    def label(self, p, t, size=9, color=TEXT, bold=False):
        return tk.Label(p, text=t, bg=p.cget('bg'), fg=color,
                        font=(FONT, size, 'bold' if bold else 'normal'))

    def panel(self, p, title, sub=''):
        f = tk.Frame(p, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        h = tk.Frame(f, bg=PANEL)
        h.pack(fill='x', padx=16, pady=(12, 0))
        self.label(h, title.upper(), 9, CYAN, True).pack(side='left')
        self.label(h, sub, 8, MUTED).pack(side='right')
        return f

    def build(self):
        h = tk.Frame(self, bg=BG)
        h.pack(fill='x', padx=26, pady=(18, 8))
        tk.Label(h, text='SMART SCAN PRO', bg=BG, fg=CYAN,
                 font=(FONT, 24, 'bold')).pack(side='left')
        tk.Label(h, text='  V2  /  ADAPTIVE SCAN INTELLIGENCE', bg=BG, fg=MUTED,
                 font=(FONT, 9, 'bold')).pack(side='left', pady=(12, 0))
        self.status = tk.Label(h, text='● SYSTEM READY', bg=BG, fg=GREEN,
                               font=(FONT, 9, 'bold'))
        self.status.pack(side='right', padx=10)
        for t, c in [('RUN SCAN', self.scan), ('AUTO RUN', self.toggle),
                     ('BENCHMARK', self.benchmark), ('RESET', self.reset)]:
            ttk.Button(h, text=t, command=c).pack(side='right', padx=3)

        m = tk.Frame(self, bg=BG)
        m.pack(fill='both', expand=True, padx=26, pady=6)
        m.grid_columnconfigure(0, weight=5)
        m.grid_columnconfigure(1, weight=3)
        m.grid_rowconfigure(0, weight=3)
        m.grid_rowconfigure(1, weight=2)

        sp = self.panel(m, 'RF ACTIVITY MAP', 'PREDICTED / CURRENT')
        sp.grid(row=0, column=0, sticky='nsew', padx=(0, 7), pady=(0, 7))
        self.spec = tk.Canvas(sp, bg=PANEL, highlightthickness=0)
        self.spec.pack(fill='both', expand=True, padx=12, pady=12)

        dc = self.panel(m, 'AI DECISION CORE', 'CLOSED LOOP')
        dc.grid(row=0, column=1, sticky='nsew', padx=(7, 0), pady=(0, 7))
        self.band = tk.Label(dc, text='BAND --', bg=PANEL, fg=CYAN, font=(FONT, 38, 'bold'))
        self.band.pack(anchor='w', padx=18, pady=(22, 0))
        self.prob = tk.Label(dc, text='Activity estimate --', bg=PANEL, fg=WHITE, font=(FONT, 12))
        self.prob.pack(anchor='w', padx=18, pady=4)
        self.mode = tk.Label(dc, text='STANDBY', bg='#12343D', fg=CYAN,
                             font=(FONT, 8, 'bold'), padx=9, pady=5)
        self.mode.pack(anchor='w', padx=18, pady=8)
        tk.Frame(dc, bg=BORDER, height=1).pack(fill='x', padx=18, pady=8)
        self.state = tk.Label(dc, text='Waiting for scan', bg=PANEL, fg=TEXT,
                              justify='left', font=(MONO, 9))
        self.state.pack(anchor='w', padx=18, pady=8)

        pr = self.panel(m, 'ACTIVITY PREDICTION', 'PROBABILITY BY BAND')
        pr.grid(row=1, column=0, sticky='nsew', padx=(0, 7))
        self.pred = tk.Canvas(pr, bg=PANEL, highlightthickness=0)
        self.pred.pack(fill='both', expand=True, padx=12, pady=10)

        op = self.panel(m, 'OPERATIONS FEED', 'EVENTS / BENCHMARK')
        op.grid(row=1, column=1, sticky='nsew', padx=(7, 0))
        nb = ttk.Notebook(op)
        nb.pack(fill='both', expand=True, padx=9, pady=9)
        self.nb = nb

        ev = tk.Frame(nb, bg=PANEL)
        nb.add(ev, text='  LIVE EVENTS  ')
        self.result = tk.Label(ev, text='READY', bg=PANEL, fg=WHITE, font=(FONT, 25, 'bold'))
        self.result.pack(anchor='w', padx=14, pady=(12, 0))
        self.reward = tk.Label(ev, text='Reward —', bg=PANEL, fg=MUTED, font=(MONO, 9))
        self.reward.pack(anchor='w', padx=14)
        self.log = tk.Text(ev, bg=BG_2, fg=TEXT, relief='flat', font=(MONO, 8), padx=8, pady=8)
        self.log.pack(fill='both', expand=True, padx=9, pady=9)

        # Upgraded benchmark tab
        self.build_benchmark_tab(nb)

        foot = tk.Frame(self, bg=BG)
        foot.pack(fill='x', padx=26, pady=(4, 16))
        self.k = {}
        for n, v in [('Pd', '0.0%'), ('Pfa proxy', '0.0%'), ('Prediction', '0.0%'),
                     ('Efficiency', '0.0%'), ('Reward', '0.00'), ('Clusters', '0')]:
            c = tk.Frame(foot, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            c.pack(side='left', fill='x', expand=True, padx=3)
            tk.Label(c, text=n.upper(), bg=PANEL, fg=MUTED, font=(FONT, 7, 'bold')).pack(pady=(6, 0))
            x = tk.Label(c, text=v, bg=PANEL, fg=WHITE, font=(FONT, 16, 'bold'))
            x.pack(pady=(1, 7))
            self.k[n] = x

    def build_benchmark_tab(self, nb):
        bv = tk.Frame(nb, bg=BG_2)
        nb.add(bv, text='  BENCHMARK LAB  ')
        bv.grid_rowconfigure(1, weight=1)
        bv.grid_columnconfigure(0, weight=1)

        top = tk.Frame(bv, bg=BG_2)
        top.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1)
        title_box = tk.Frame(top, bg=BG_2)
        title_box.grid(row=0, column=0, sticky='w')
        tk.Label(title_box, text='SMART SCAN BENCHMARK', bg=BG_2, fg=WHITE,
                 font=(FONT, 14, 'bold')).pack(anchor='w')
        self.bench_status = tk.Label(title_box,
            text='Sequential vs Random vs Smart — run a benchmark to populate live results.',
            bg=BG_2, fg=MUTED, font=(FONT, 8))
        self.bench_status.pack(anchor='w', pady=(2, 0))
        ttk.Button(top, text='RUN COMPARISON', command=self.benchmark).grid(row=0, column=1, padx=(8, 0))

        self.bench_body = tk.Frame(bv, bg=BG_2)
        self.bench_body.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        self.bench_body.grid_columnconfigure(0, weight=3)
        self.bench_body.grid_columnconfigure(1, weight=2)
        self.bench_body.grid_rowconfigure(1, weight=1)
        self.bench_body.grid_rowconfigure(2, weight=1)

        self.bench_kpi_frame = tk.Frame(self.bench_body, bg=BG_2)
        self.bench_kpi_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 8))
        self.bench_kpis = {}
        for i, (key, label, value) in enumerate([
            ('best', 'BEST DETECTION', '—'),
            ('gain', 'SMART GAIN', '—'),
            ('reward', 'SMART REWARD', '—'),
            ('scanhit', 'SCANS / HIT', '—'),
        ]):
            card = tk.Frame(self.bench_kpi_frame, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=i, sticky='ew', padx=3)
            self.bench_kpi_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=label, bg=PANEL, fg=MUTED, font=(FONT, 7, 'bold')).pack(anchor='w', padx=12, pady=(8, 0))
            val = tk.Label(card, text=value, bg=PANEL, fg=CYAN, font=(FONT, 18, 'bold'))
            val.pack(anchor='w', padx=12, pady=(1, 8))
            self.bench_kpis[key] = val

        chart_left = tk.Frame(self.bench_body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        chart_left.grid(row=1, column=0, sticky='nsew', padx=(0, 4), pady=4)
        chart_right = tk.Frame(self.bench_body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        chart_right.grid(row=1, column=1, sticky='nsew', padx=(4, 0), pady=4)
        self.bench_chart_left = chart_left
        self.bench_chart_right = chart_right

        diagram = tk.Frame(self.bench_body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        diagram.grid(row=2, column=0, sticky='nsew', padx=(0, 4), pady=4)
        table = tk.Frame(self.bench_body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        table.grid(row=2, column=1, sticky='nsew', padx=(4, 0), pady=4)
        self.bench_diagram = diagram
        self.bench_table_frame = table
        self.build_benchmark_placeholder()

    def build_benchmark_placeholder(self):
        for f in (self.bench_chart_left, self.bench_chart_right, self.bench_diagram, self.bench_table_frame):
            for w in f.winfo_children(): w.destroy()
        self.label(self.bench_chart_left, 'DETECTION PROFILE', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        self.label(self.bench_chart_left, 'Run comparison to render measured strategy curves.', 8, MUTED).pack(anchor='w', padx=12, pady=2)
        self.label(self.bench_chart_right, 'EFFICIENCY / REWARD', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        self.label(self.bench_chart_right, 'Two-axis decision-quality view.', 8, MUTED).pack(anchor='w', padx=12, pady=2)
        self.label(self.bench_diagram, 'BENCHMARK DECISION PIPELINE', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        c = tk.Canvas(self.bench_diagram, bg=PANEL, highlightthickness=0, height=130)
        c.pack(fill='both', expand=True, padx=10, pady=5)
        self.draw_benchmark_pipeline(c)
        self.label(self.bench_table_frame, 'STRATEGY SCORECARD', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        self.label(self.bench_table_frame, 'Measured output will appear here.', 8, MUTED).pack(anchor='w', padx=12, pady=2)

    def draw_benchmark_pipeline(self, c, smart=False):
        c.delete('all')
        c.update_idletasks()
        w = max(c.winfo_width(), 420)
        y = 58
        steps = [('ENV', 'RF activity'), ('SCAN', 'Strategy'), ('HIT/MISS', 'Observation'), ('LEARN', 'Feedback'), ('NEXT', 'Decision')]
        boxw = min(105, (w - 70) / len(steps))
        start = 12
        for i, (a, b) in enumerate(steps):
            x = start + i * (boxw + 10)
            fill = '#10333C' if a != 'NEXT' else '#164651'
            c.create_rectangle(x, y-23, x+boxw, y+23, fill=fill, outline=CYAN_DARK, width=1)
            c.create_text(x+boxw/2, y-6, text=a, fill=CYAN, font=(FONT, 8, 'bold'))
            c.create_text(x+boxw/2, y+9, text=b, fill=MUTED, font=(FONT, 7))
            if i < len(steps)-1:
                c.create_line(x+boxw+2, y, x+boxw+9, y, fill=CYAN, width=2, arrow=tk.LAST)
        c.create_text(12, 108, anchor='w', text='Sequential = fixed order   •   Random = exploration   •   Smart = prediction + feedback',
                      fill=TEXT, font=(FONT, 8))

    def _clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def render_benchmark(self):
        if self.bench is None:
            return
        df = self.bench.copy()
        names = list(df['Strategy'])
        colors = [CYAN_DARK if n != 'Smart' else CYAN for n in names]
        smart_row = df[df['Strategy'] == 'Smart'].iloc[0]
        seq_row = df[df['Strategy'] == 'Sequential'].iloc[0]

        self.bench_kpis['best'].config(text=f"{smart_row['Detection Rate (%)']:.1f}%")
        self.bench_kpis['gain'].config(text=f"+{smart_row['Detection Rate (%)'] - seq_row['Detection Rate (%)']:.1f} pp")
        self.bench_kpis['reward'].config(text=f"{smart_row['Average Reward']:+.3f}")
        self.bench_kpis['scanhit'].config(text=f"{smart_row['Scans / Hit']:.2f}")
        self.bench_status.config(
            text=f"Complete • {len(df)} strategies • {int(df['Scans'].max())} scans/strategy • Smart leads detection and efficiency.",
            fg=GREEN)

        # Drop references to previous benchmark figures before drawing the new measured run.
        self.bench_figures.clear()

        if not MATPLOTLIB_OK:
            for f in (self.bench_chart_left, self.bench_chart_right):
                self._clear_frame(f)
                self.label(f, 'MATPLOTLIB NOT AVAILABLE', 9, YELLOW, True).pack(anchor='center', pady=35)
                self.label(f, 'Install requirements.txt and restart.', 8, MUTED).pack(anchor='center')
        else:
            self._render_chart(self.bench_chart_left, df, 'Detection Rate (%)', 'Prediction Accuracy (%)', 'Detection vs prediction', 'Performance (%)', [CYAN, '#168A9B'])
            self._render_chart(self.bench_chart_right, df, 'Efficiency (%)', 'Average Reward', 'Efficiency and reward', 'Metric value', [CYAN, '#168A9B'])

        self._render_pipeline_and_table(df)

    def _render_chart(self, parent, df, metric1, metric2, title, ylabel, bar_colors):
        self._clear_frame(parent)
        self.label(parent, title.upper(), 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        fig = Figure(figsize=(6, 2.35), dpi=100, facecolor=PANEL)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PANEL)
        x = np.arange(len(df))
        width = 0.34
        ax.bar(x - width/2, df[metric1].values, width, label=metric1.replace(' (%)',''), color=bar_colors[0], alpha=0.95)
        ax.bar(x + width/2, df[metric2].values, width, label=metric2.replace(' (%)',''), color=bar_colors[1], alpha=0.75)
        ax.set_xticks(x)
        ax.set_xticklabels(df['Strategy'].tolist(), color=TEXT, fontsize=8)
        ax.tick_params(axis='y', colors=MUTED, labelsize=7)
        ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
        ax.grid(axis='y', alpha=0.12)
        ax.spines[['top','right','left','bottom']].set_color(BORDER)
        ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=7, loc='upper left')
        for spine in ax.spines.values(): spine.set_linewidth(0.7)
        fig.tight_layout(pad=1.1)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=3)
        self.bench_figures.append((fig, canvas))

    def _render_pipeline_and_table(self, df):
        self._clear_frame(self.bench_diagram)
        self.label(self.bench_diagram, 'BENCHMARK DECISION PIPELINE', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        c = tk.Canvas(self.bench_diagram, bg=PANEL, highlightthickness=0, height=145)
        c.pack(fill='both', expand=True, padx=10, pady=5)
        self.draw_benchmark_pipeline(c, smart=True)

        self._clear_frame(self.bench_table_frame)
        self.label(self.bench_table_frame, 'STRATEGY SCORECARD', 8, MUTED, True).pack(anchor='w', padx=12, pady=(10, 0))
        cols = ('Strategy', 'Detection', 'Prediction', 'Efficiency', 'Reward', 'Scans/Hit')
        tree = ttk.Treeview(self.bench_table_frame, columns=cols, show='headings', height=5)
        for col in cols:
            tree.heading(col, text=col.upper())
            tree.column(col, width=86, anchor='center')
        for _, r in df.iterrows():
            tag = 'smart' if r['Strategy'] == 'Smart' else 'normal'
            tree.insert('', 'end', values=(r['Strategy'], f"{r['Detection Rate (%)']:.1f}%",
                f"{r['Prediction Accuracy (%)']:.1f}%", f"{r['Scan Efficiency (%)']:.1f}%",
                f"{r['Average Reward']:+.3f}", f"{r['Scans / Hit']:.2f}"), tags=(tag,))
        tree.tag_configure('smart', foreground=CYAN)
        tree.pack(fill='both', expand=True, padx=9, pady=7)
        self.label(self.bench_table_frame, 'Pd = detection rate in this simulation. Pfa proxy = miss rate; not calibrated receiver Pfa.',
                   7, MUTED).pack(anchor='w', padx=12, pady=(0, 8))

    def scan(self):
        self.engine.step()
        self.status.config(text='● LIVE SIMULATION', fg=CYAN)
        self.refresh()

    def toggle(self):
        self.auto = not self.auto
        self.status.config(text=('● AUTO RUNNING' if self.auto else '● PAUSED'),
                           fg=(GREEN if self.auto else YELLOW))
        if self.auto:
            self.auto_step()

    def auto_step(self):
        if not self.auto:
            return
        self.engine.step()
        self.refresh()
        self.after(550, self.auto_step)

    def reset(self):
        self.auto = False
        self.engine.reset()
        self.status.config(text='● SYSTEM READY', fg=GREEN)
        self.refresh()

    def benchmark(self):
        # Run the three strategies against the same measured synthetic RF/PDW timeline.
        # Results are rendered directly into the Benchmark Lab; no hidden/undefined
        # scorecard widgets are required.
        self.bench_status.config(text='RUNNING MEASURED COMPARISON • Sequential / Random / Smart', fg=CYAN)
        self.update_idletasks()
        try:
            self.bench = run_benchmark()
            if self.bench is None or self.bench.empty:
                raise RuntimeError('Benchmark returned no measured results.')
        except Exception as e:
            self.bench = None
            self.bench_status.config(text='BENCHMARK FAILED • see error dialog', fg=RED)
            messagebox.showerror('Benchmark Error', str(e))
            return

        # Render the actual measured dataframe into the benchmark tab.
        self.render_benchmark()
        self.nb.select(1)
        smart = self.bench[self.bench['Strategy'] == 'Smart'].iloc[0]
        self.bench_status.config(
            text=(f"MEASURED • {int(self.bench['Scans'].max())} scans/strategy • "
                  f"Smart detection {smart['Detection Rate (%)']:.1f}% • "
                  f"{int(smart['Hits'])} hits / {int(smart['Misses'])} misses"),
            fg=GREEN)

    def refresh(self):
        s = self.engine.status()
        p = s['p']
        b = s['last_band']
        if b is not None:
            self.band.config(text=f'BAND {b+1}')
            self.prob.config(text=f'Activity estimate  {s["last_prob"]*100:.1f}%')
            self.mode.config(text=s['mode'])
            self.state.config(text=f'Time slot     T{s["time"]:03d}\nScans         {s["scans"]}\nExploration   {s["epsilon"]*100:.1f}%\nHDBSCAN       {s["clusters"]} clusters / {s["noise"]} noise')
        self.result.config(text=('✓  HIT' if s['result'] == 'HIT' else ('×  MISS' if s['result'] == 'MISS' else 'READY')),
                           fg=(GREEN if s['result'] == 'HIT' else RED if s['result'] == 'MISS' else WHITE))
        self.reward.config(text=f'Reward  {s["reward"]:+.2f}')
        for n, v in [('Pd', s['pd']*100), ('Pfa proxy', s['pfa']*100),
                     ('Prediction', s['acc']*100), ('Efficiency', s['eff']*100)]:
            self.k[n].config(text=f'{v:.1f}%')
        self.k['Reward'].config(text=f'{s["total_reward"]:+.2f}')
        self.k['Clusters'].config(text=str(s['clusters']))
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, '\n'.join(s['log']))
        self.draw(self.spec, p, s['activity'])
        self.draw(self.pred, p, small=True)

    def draw(self, c, p, activity=None, small=False):
        c.delete('all')
        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 180)
        left, right = 45, 45
        if small:
            row = (h-15)/8
            x0, x1 = 70, w-45
            for b, v in enumerate(p):
                y = 6 + b*row
                c.create_text(10, y+7, anchor='w', text=f'B{b+1}', fill=WHITE, font=(FONT, 8, 'bold'))
                c.create_rectangle(x0, y, x1, y+14, fill='#08161C', outline=BORDER)
                c.create_rectangle(x0, y, x0+v*(x1-x0), y+14, fill=CYAN_DARK, outline='')
                c.create_text(x1+4, y+7, anchor='w', text=f'{v*100:.0f}%', fill=CYAN, font=(MONO, 8, 'bold'))
            return
        base, maxh, gap = h-35, h-90, 8
        bw = (w-left-right-gap*7)/8
        for b, v in enumerate(p):
            x1 = left+b*(bw+gap)
            x2 = x1+bw
            bh = max(3, v*maxh)
            y = base-bh
            c.create_rectangle(x1, base-maxh, x2, base, fill='#08161C', outline=BORDER)
            c.create_rectangle(x1, y, x2, base, fill=CYAN_DARK, outline='')
            if activity is not None and activity[b]:
                c.create_rectangle(x1, base-4, x2, base, fill=GREEN, outline='')
            c.create_text((x1+x2)/2, y-10, text=f'{v*100:.0f}%', fill=CYAN, font=(FONT, 8, 'bold'))
            c.create_text((x1+x2)/2, base+14, text=f'B{b+1}', fill=WHITE, font=(FONT, 8, 'bold'))


if __name__ == '__main__':
    SmartScanDashboard().mainloop()
