#!/usr/bin/env python3
"""
Pomodoro Timer — ターミナルで動くポモドーロタイマー
キー操作: [ENTER] 開始/一時停止  [s] スキップ  [q] 終了
"""

import sys
import time
import os
import msvcrt
import threading
import winsound
from datetime import datetime

# --- 設定 ---
WORK_MINUTES = 25
SHORT_BREAK_MINUTES = 5
LONG_BREAK_MINUTES = 15
LONG_BREAK_INTERVAL = 4  # 4ポモドーロごとに長い休憩

# --- カラー (ANSI) ---
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def enable_ansi():
    """Windows で ANSI エスケープを有効化"""
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()

def beep_work_done():
    """作業終了ビープ: 高音3回"""
    for _ in range(3):
        winsound.Beep(880, 200)
        time.sleep(0.1)

def beep_break_done():
    """休憩終了ビープ: 低音2回"""
    for _ in range(2):
        winsound.Beep(440, 300)
        time.sleep(0.15)

def beep_start():
    winsound.Beep(660, 150)

def render_bar(elapsed, total, width=30):
    filled = int(width * elapsed / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * elapsed / total)
    return f"[{bar}] {pct:3d}%"

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def phase_label(phase):
    if phase == "work":
        return f"{RED}{BOLD}🍅 作業中{RESET}"
    elif phase == "short":
        return f"{GREEN}{BOLD}☕ 短い休憩{RESET}"
    else:
        return f"{CYAN}{BOLD}🌿 長い休憩{RESET}"

def phase_duration(phase):
    if phase == "work":
        return WORK_MINUTES * 60
    elif phase == "short":
        return SHORT_BREAK_MINUTES * 60
    else:
        return LONG_BREAK_MINUTES * 60

def get_next_phase(current_phase, pomodoro_count):
    if current_phase == "work":
        if pomodoro_count % LONG_BREAK_INTERVAL == 0:
            return "long"
        return "short"
    else:
        return "work"

def print_header():
    os.system("cls")
    print(f"{BOLD}{CYAN}{'═'*50}{RESET}")
    print(f"{BOLD}{CYAN}         🍅  ポモドーロタイマー  🍅{RESET}")
    print(f"{BOLD}{CYAN}{'═'*50}{RESET}")
    print(f"{DIM}  [ENTER] 開始/一時停止  [s] スキップ  [q] 終了{RESET}")
    print()

class PomodoroTimer:
    def __init__(self):
        self.phase = "work"
        self.pomodoro_count = 0
        self.elapsed = 0.0
        self.running = False
        self.skip = False
        self.quit = False
        self.paused = True
        self.start_time = None
        self.history = []

    def input_thread(self):
        while not self.quit:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b'\r', b'\n', b' '):
                    if self.paused:
                        self.paused = False
                        self.running = True
                    else:
                        self.paused = True
                elif ch == b's':
                    self.skip = True
                elif ch == b'q':
                    self.quit = True
            time.sleep(0.05)  # ビジーループを避けて CPU 使用率を抑える

    def run(self):
        enable_ansi()
        print_header()

        t = threading.Thread(target=self.input_thread, daemon=True)
        t.start()

        print(f"  {YELLOW}[ENTER] を押して開始してください...{RESET}\n")

        while not self.quit:
            duration = phase_duration(self.phase)

            # フェーズ開始前の待機
            while self.paused and not self.skip and not self.quit:
                time.sleep(0.05)

            if self.quit:
                break
            if self.skip:
                self.skip = False
                self._advance_phase()
                print_header()
                print(f"  {YELLOW}[ENTER] を押して続けてください...{RESET}\n")
                self.paused = True
                continue

            # タイマー実行
            beep_start()
            self.elapsed = 0.0
            loop_start = time.time()

            while self.elapsed < duration and not self.skip and not self.quit:
                if self.paused:
                    loop_start = time.time() - self.elapsed
                    self._render(duration)
                    time.sleep(0.05)
                    continue

                self.elapsed = time.time() - loop_start
                self._render(duration)
                time.sleep(0.05)

            if self.quit:
                break

            # フェーズ完了
            self.skip = False
            self._on_phase_complete()
            self._advance_phase()

            print_header()
            self._print_summary()
            print(f"\n  {YELLOW}[ENTER] を押して次のフェーズを開始...{RESET}\n")
            self.paused = True

        clear_line()
        print(f"\n{BOLD}お疲れ様でした！ 今日は {self.pomodoro_count} ポモドーロ達成しました 🎉{RESET}\n")

    def _render(self, duration):
        remaining = max(0, duration - self.elapsed)
        bar = render_bar(self.elapsed, duration)
        label = phase_label(self.phase)
        pause_indicator = f" {YELLOW}[一時停止]{RESET}" if self.paused else ""
        pomo_str = f"{BOLD}#{self.pomodoro_count + 1}{RESET}" if self.phase == "work" else ""
        clear_line()
        sys.stdout.write(
            f"  {label} {pomo_str}  残り {BOLD}{format_time(remaining)}{RESET}  "
            f"{bar}{pause_indicator}"
        )
        sys.stdout.flush()

    def _on_phase_complete(self):
        clear_line()
        if self.phase == "work":
            self.pomodoro_count += 1
            ts = datetime.now().strftime("%H:%M")
            self.history.append(f"#{self.pomodoro_count} 完了 ({ts})")
            print(f"\n  {GREEN}{BOLD}✅ ポモドーロ #{self.pomodoro_count} 完了！{RESET}")
            threading.Thread(target=beep_work_done, daemon=True).start()
        else:
            print(f"\n  {CYAN}{BOLD}⏰ 休憩終了！{RESET}")
            threading.Thread(target=beep_break_done, daemon=True).start()
        time.sleep(0.5)

    def _advance_phase(self):
        self.phase = get_next_phase(self.phase, self.pomodoro_count)

    def _print_summary(self):
        if not self.history:
            return
        print(f"  {DIM}{'─'*44}{RESET}")
        print(f"  {DIM}今日の記録:{RESET}")
        for entry in self.history[-5:]:
            print(f"    {DIM}• {entry}{RESET}")
        print(f"  {DIM}{'─'*44}{RESET}")

if __name__ == "__main__":
    try:
        PomodoroTimer().run()
    except KeyboardInterrupt:
        print("\n\n終了しました。")
