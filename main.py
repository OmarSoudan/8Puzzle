import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from puzzle import GOAL_STATE, is_solvable
import search


class Comprehensive8PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle")
        self.root.geometry("1060x780")
        self.root.minsize(980, 720)

        # Initial puzzle state (example from assignment)
        self.current_state = (1, 2, 5, 3, 4, 0, 6, 7, 8)
        self.solution_states = [self.current_state]
        self.current_step = 0
        self.is_playing = False
        self.play_job = None
        self.step_delay_ms = 400

        self._apply_styles()
        self._build_layout()
        self.update_board(self.current_state)

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Consolas", 10), rowheight=24)

    def _build_layout(self):
        # Top Configuration Bar
        top_bar = ttk.LabelFrame(self.root, text=" Board Initialization ", padding=10)
        top_bar.pack(fill=tk.X, padx=12, pady=(10, 6))

        ttk.Label(top_bar, text="Initial State (0-8 comma separated):", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.state_entry = ttk.Entry(top_bar, width=24, font=("Consolas", 10))
        self.state_entry.insert(0, "1,2,5,3,4,0,6,7,8")
        self.state_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(top_bar, text="Load State", command=self.load_custom_state).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Random Shuffle", command=self.generate_random_state).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Reset Goal", command=self.reset_to_goal).pack(side=tk.LEFT, padx=3)

        self.status_lbl = ttk.Label(top_bar, text="Status: Ready", font=("Helvetica", 10, "bold"), foreground="#2e7d32")
        self.status_lbl.pack(side=tk.RIGHT, padx=5)

        # Notebook Tabs (Visualizer & Solver | Comparative Table & Analysis)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        self.tab_visualizer = ttk.Frame(self.notebook, padding=10)
        self.tab_analytics = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_visualizer, text=" Interactive Visualizer & Single Search ")
        self.notebook.add(self.tab_analytics, text=" Algorithm Comparison & Heuristic Analysis ")

        self._build_visualizer_tab()
        self._build_analytics_tab()

    # ================= TAB 1: VISUALIZER & SINGLE SOLVER =================
    def _build_visualizer_tab(self):
        pane = ttk.PanedWindow(self.tab_visualizer, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # Left: 3x3 Puzzle Board & Playback
        board_box = ttk.LabelFrame(pane, text=" Puzzle Board Visualization ", padding=10)
        pane.add(board_box, weight=1)

        self.grid_frame = tk.Frame(board_box, bg="#2b2b2b", bd=3, relief=tk.RIDGE)
        self.grid_frame.pack(expand=True, pady=10)

        self.tile_labels = []
        for r in range(3):
            row_lbls = []
            for c in range(3):
                lbl = tk.Label(
                    self.grid_frame,
                    text="",
                    font=("Helvetica", 24, "bold"),
                    width=4,
                    height=2,
                    relief=tk.RAISED,
                    bd=3
                )
                lbl.grid(row=r, column=c, padx=4, pady=4)
                row_lbls.append(lbl)
            self.tile_labels.append(row_lbls)

        # Controls & Stepper
        ctrl_frame = ttk.Frame(board_box)
        ctrl_frame.pack(fill=tk.X, pady=4)

        self.btn_prev = ttk.Button(ctrl_frame, text="◀ Step Back", command=self.step_prev, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_play = ttk.Button(ctrl_frame, text="▶ Auto Play", command=self.toggle_play, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_next = ttk.Button(ctrl_frame, text="Step Next ▶", command=self.step_next, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Speed slider & counter
        sub_ctrl = ttk.Frame(board_box)
        sub_ctrl.pack(fill=tk.X, pady=(4, 0))

        self.step_info_lbl = ttk.Label(sub_ctrl, text="Step: 0 / 0", font=("Helvetica", 11, "bold"))
        self.step_info_lbl.pack(side=tk.LEFT, padx=5)

        ttk.Label(sub_ctrl, text="Speed:").pack(side=tk.RIGHT, padx=(5, 0))
        self.speed_slider = ttk.Scale(sub_ctrl, from_=100, to=1000, value=400, command=self._on_speed_change)
        self.speed_slider.pack(side=tk.RIGHT, padx=5)

        # Right: Algorithm Launcher & Execution Stats
        action_box = ttk.LabelFrame(pane, text=" Single Algorithm Execution ", padding=10)
        pane.add(action_box, weight=1)

        sel_frame = ttk.Frame(action_box)
        sel_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(sel_frame, text="Select Algorithm:", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.algo_var = tk.StringVar(value="A* Manhattan")
        self.algo_combo = ttk.Combobox(
            sel_frame,
            textvariable=self.algo_var,
            state="readonly",
            values=["BFS", "DFS", "Iterative DFS", "A* Manhattan", "A* Euclidean"]
        )
        self.algo_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_row = ttk.Frame(action_box)
        btn_row.pack(fill=tk.X, pady=6)

        self.solve_btn = ttk.Button(btn_row, text="Run Single Algorithm", command=self.run_single_solver)
        self.solve_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.compare_btn = ttk.Button(btn_row, text="⚡ Compare All Algorithms", command=self.run_all_comparisons)
        self.compare_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # Metrics Box
        stat_frame = ttk.LabelFrame(action_box, text=" Execution Metrics ", padding=8)
        stat_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.stats_text = tk.Text(stat_frame, wrap=tk.WORD, font=("Consolas", 10), relief=tk.FLAT)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.insert(tk.END, "Select an algorithm and click 'Run Single Algorithm' or 'Compare All Algorithms'.")
        self.stats_text.config(state=tk.DISABLED)

    # ================= TAB 2: COMPARISON TABLE & ANALYSIS =================
    def _build_analytics_tab(self):
        # Comparative Table
        tbl_box = ttk.LabelFrame(self.tab_analytics, text=" Algorithm Benchmark Summary (Current Board) ", padding=8)
        tbl_box.pack(fill=tk.X, pady=(0, 10))

        columns = ("algo", "cost", "expanded", "depth", "time")
        self.tree = ttk.Treeview(tbl_box, columns=columns, show="headings", height=5)
        self.tree.heading("algo", text="Algorithm")
        self.tree.heading("cost", text="Cost of Path")
        self.tree.heading("expanded", text="Nodes Expanded")
        self.tree.heading("depth", text="Search Depth")
        self.tree.heading("time", text="Running Time (s)")

        self.tree.column("algo", width=180, anchor=tk.W)
        self.tree.column("cost", width=110, anchor=tk.CENTER)
        self.tree.column("expanded", width=130, anchor=tk.CENTER)
        self.tree.column("depth", width=110, anchor=tk.CENTER)
        self.tree.column("time", width=130, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, expand=True)

        # Admissibility and Theoretical Report Section
        analysis_box = ttk.LabelFrame(self.tab_analytics, text=" Theoretical Findings & Report Guide (Section 2.2 & 3.1) ", padding=8)
        analysis_box.pack(fill=tk.BOTH, expand=True)

        guide_text = tk.Text(analysis_box, wrap=tk.WORD, font=("Segoe UI", 10), relief=tk.FLAT)
        guide_text.pack(fill=tk.BOTH, expand=True)

        analysis_content = (
            "1. HEURISTIC ADMISSIBILITY COMPARISON (Section 2.2):\n"
            "   • Admissibility: A heuristic h(n) is admissible if h(n) <= h*(n) for all n (never overestimates).\n"
            "   • Both Manhattan Distance and Euclidean Distance are admissible because any legal tile move\n"
            "     transfers a tile by exactly 1 grid step (cost = 1).\n"
            "   • Euclidean distance represents the straight-line distance: sqrt((x1 - x2)^2 + (y1 - y2)^2).\n"
            "   • Manhattan distance represents the grid-constrained distance: |x1 - x2| + |y1 - y2|.\n"
            "   • By the triangle inequality on a Cartesian grid: h_Euclidean(n) <= h_Manhattan(n) <= h*(n).\n"
            "   • Conclusion: Manhattan distance DOMINATES Euclidean distance. It provides a strictly tighter\n"
            "     lower bound, causing A* to prune more paths and expand significantly fewer search nodes.\n\n"
            "2. DATA STRUCTURES EMPLOYED (Section 3.1):\n"
            "   • BFS: FIFO Queue (collections.deque) + Visited Hash Set.\n"
            "   • DFS: LIFO Stack (Python list) + Visited Hash Set (bounded by depth).\n"
            "   • Iterative DFS: Iterative Depth-Limited Search recursion stack + branch ancestor-cycle checking.\n"
            "   • A* Search: Min-Priority Queue (heapq) keyed on f(n) = g(n) + h(n) + Closed Cost Map (dict).\n\n"
            "3. ALGORITHM OBSERVATIONS:\n"
            "   • BFS, IDDFS, and A* are guaranteed to find the optimal path length (shortest cost).\n"
            "   • Standard DFS does not guarantee optimality and often traverses deep paths, yielding high costs.\n"
            "   • IDDFS combines the low memory overhead of DFS (O(bd)) with the optimality guarantee of BFS.\n"
        )
        guide_text.insert(tk.END, analysis_content)
        guide_text.config(state=tk.DISABLED)

    # ================= BOARD & PLAYBACK LOGIC =================
    def update_board(self, state):
        for idx, val in enumerate(state):
            r, c = idx // 3, idx % 3
            lbl = self.tile_labels[r][c]
            if val == 0:
                lbl.config(text="", bg="#e0e0e0", relief=tk.SUNKEN)
            else:
                lbl.config(text=str(val), bg="#1976d2", fg="white", relief=tk.RAISED)

    def _on_speed_change(self, val):
        self.step_delay_ms = int(float(val))

    def load_custom_state(self):
        raw = self.state_entry.get().strip()
        try:
            parsed = tuple(map(int, [x.strip() for x in raw.split(",")]))
            if len(parsed) != 9 or set(parsed) != set(range(9)):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please provide 9 distinct comma-separated integers (0 through 8).")
            return

        if not is_solvable(parsed):
            messagebox.showwarning("Unsolvable State", "This configuration has odd inversion parity and cannot reach 0,1,2,3,4,5,6,7,8.")
            return

        self._reset_playback([parsed])

    def generate_random_state(self):
        items = list(range(9))
        while True:
            random.shuffle(items)
            cand = tuple(items)
            if is_solvable(cand):
                break
        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(0, ",".join(map(str, cand)))
        self._reset_playback([cand])

    def reset_to_goal(self):
        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(0, ",".join(map(str, GOAL_STATE)))
        self._reset_playback([GOAL_STATE])

    def _reset_playback(self, states):
        if self.play_job:
            self.root.after_cancel(self.play_job)
        self.is_playing = False
        self.btn_play.config(text="▶ Auto Play")
        self.solution_states = states
        self.current_step = 0
        self.update_board(self.solution_states[0])
        self.update_step_controls()

    def update_step_controls(self):
        total = len(self.solution_states) - 1
        self.step_info_lbl.config(text=f"Step: {self.current_step} / {total}")
        self.btn_prev.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_step < total else tk.DISABLED)
        self.btn_play.config(state=tk.NORMAL if total > 0 else tk.DISABLED)

    def step_next(self):
        if self.current_step < len(self.solution_states) - 1:
            self.current_step += 1
            self.update_board(self.solution_states[self.current_step])
            self.update_step_controls()

    def step_prev(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_board(self.solution_states[self.current_step])
            self.update_step_controls()

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="▶ Auto Play")
            if self.play_job:
                self.root.after_cancel(self.play_job)
        else:
            self.is_playing = True
            self.btn_play.config(text="❚❚ Pause")
            self._playback_loop()

    def _playback_loop(self):
        if not self.is_playing:
            return
        if self.current_step < len(self.solution_states) - 1:
            self.step_next()
            self.play_job = self.root.after(self.step_delay_ms, self._playback_loop)
        else:
            self.is_playing = False
            self.btn_play.config(text="▶ Auto Play")

    # ================= SEARCH EXECUTION =================
    def _parse_input_state(self):
        raw = self.state_entry.get().strip()
        try:
            parsed = tuple(map(int, [x.strip() for x in raw.split(",")]))
            if len(parsed) != 9 or set(parsed) != set(range(9)):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please provide 9 distinct comma-separated integers (0 through 8).")
            return None

        if not is_solvable(parsed):
            messagebox.showwarning("Unsolvable Board", "This board is mathematically unsolvable for goal (0,1,2,3,4,5,6,7,8).")
            return None

        return parsed

    def run_single_solver(self):
        state = self._parse_input_state()
        if not state:
            return

        algo = self.algo_var.get()
        self._set_ui_busy(True, f"Running {algo}...")

        def worker():
            res = self._execute_algo(algo, state)
            self.root.after(0, self._on_single_solved, algo, res)

        threading.Thread(target=worker, daemon=True).start()

    def _execute_algo(self, algo_name, state):
        if algo_name == "BFS":
            return search.bfs(state)
        elif algo_name == "DFS":
            return search.dfs(state)
        elif algo_name == "Iterative DFS":
            return search.iddfs(state)
        elif algo_name == "A* Manhattan":
            return search.a_star_manhattan(state)
        elif algo_name == "A* Euclidean":
            return search.a_star_euclidean(state)
        return None

    def _on_single_solved(self, algo, result):
        self._set_ui_busy(False, "Status: Solution Ready!")
        if not result:
            messagebox.showinfo("Result", "No solution was found within bounds.")
            return

        self._reset_playback(result['states'])

        # Populate single metrics box
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        path_str = " -> ".join(result['path']) if result['path'] else "Initial state is goal"
        report = (
            f"Algorithm:       {algo}\n"
            f"=========================================\n"
            f"Cost of Path:    {result['cost_of_path']}\n"
            f"Nodes Expanded:  {result['nodes_expanded']}\n"
            f"Search Depth:    {result['search_depth']}\n"
            f"Running Time:    {result['running_time']:.6f} seconds\n"
            f"=========================================\n"
            f"Path to Goal:\n{path_str}\n"
        )
        self.stats_text.insert(tk.END, report)
        self.stats_text.config(state=tk.DISABLED)

    def run_all_comparisons(self):
        state = self._parse_input_state()
        if not state:
            return

        self._set_ui_busy(True, "Running all 5 algorithms benchmark...")

        def worker():
            algos = ["BFS", "DFS", "Iterative DFS", "A* Manhattan", "A* Euclidean"]
            results = []
            for name in algos:
                r = self._execute_algo(name, state)
                results.append((name, r))
            self.root.after(0, self._on_comparison_complete, results)

        threading.Thread(target=worker, daemon=True).start()

    def _on_comparison_complete(self, results):
        self._set_ui_busy(False, "Status: Comparison Completed!")

        # Clear existing rows in Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new benchmark rows
        for name, res in results:
            if res:
                self.tree.insert("", tk.END, values=(
                    name,
                    res['cost_of_path'],
                    res['nodes_expanded'],
                    res['search_depth'],
                    f"{res['running_time']:.6f}"
                ))
            else:
                self.tree.insert("", tk.END, values=(name, "N/A", "N/A", "N/A", "Timeout/Fail"))

        # Switch to analytics tab to show the populated table
        self.notebook.select(self.tab_analytics)

    def _set_ui_busy(self, is_busy, status_msg):
        self.status_lbl.config(
            text=status_msg,
            foreground="#d32f2f" if is_busy else "#2e7d32"
        )
        state_mode = tk.DISABLED if is_busy else tk.NORMAL
        self.solve_btn.config(state=state_mode)
        self.compare_btn.config(state=state_mode)


if __name__ == "__main__":
    root = tk.Tk()
    app = Comprehensive8PuzzleGUI(root)
    root.mainloop()
