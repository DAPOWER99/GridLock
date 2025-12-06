import random
import threading
import time
import re
from enum import Enum
from typing import List, Tuple, Optional
import signal
import math  # For celebration animation - MOVED TO TOP
import ctypes
import os
import sys

title = "GridLock"

class Terminal:
    @staticmethod
    def set_terminal_title(title: str):
        """Set terminal window title - PowerShell compatible"""
        try:
            if os.name == 'nt':  # Windows (including PowerShell)
                # Method 1: PowerShell specific command (works best with pwsh)
                import subprocess
                
                # Try multiple PowerShell methods
                try:
                    # Method A: Direct PowerShell command
                    subprocess.run(
                        ['powershell', '-Command', f"$host.ui.RawUI.WindowTitle = '{title}'"],
                        shell=True,
                        capture_output=True,
                        timeout=1
                    )
                except:
                    pass
                
                try:
                    # Method B: For PowerShell 7+ (pwsh)
                    subprocess.run(
                        ['pwsh', '-Command', f"$host.ui.RawUI.WindowTitle = '{title}'"],
                        shell=True,
                        capture_output=True,
                        timeout=1
                    )
                except:
                    pass
                
                # Method 2: Windows API (works with cmd.exe)
                try:
                    ctypes.windll.kernel32.SetConsoleTitleW(title)
                except:
                    pass
                
                # Method 3: Direct call for immediate effect
                try:
                    os.system(f'title {title}')
                except:
                    pass
                    
            else:  # Unix/Linux/Mac
                # Multiple escape sequences for different terminals
                sequences = [
                    f"\033]0;{title}\007",  # Standard xterm
                    f"\033]2;{title}\007",  # Alternative
                    f"\033]1;{title}\007",  # Another alternative
                ]
                for seq in sequences:
                    sys.stdout.write(seq)
                sys.stdout.flush()
        except:
            pass  # Silently fail if title can't be set

    @staticmethod
    def save_cursor():
        """Save cursor position"""
        sys.stdout.write("\033[s")
        sys.stdout.flush()
    
    @staticmethod
    def restore_cursor():
        """Restore cursor position"""
        sys.stdout.write("\033[u")
        sys.stdout.flush()
    
    @staticmethod
    def move_cursor(x: int, y: int):
        """Move cursor to column x, row y (1-indexed)"""
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()
    
    @staticmethod
    def hide_cursor():
        """Hide the cursor"""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    
    @staticmethod
    def show_cursor():
        """Show the cursor"""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    
    @staticmethod
    def clear_screen():
        """Clear entire screen"""
        sys.stdout.write("\033[2J")
        sys.stdout.flush()
    
    @staticmethod
    def clear_line():
        """Clear current line"""
        sys.stdout.write("\033[2K")
        sys.stdout.flush()
    
    @staticmethod
    def clear_to_end_of_line():
        """Clear from cursor to end of line"""
        sys.stdout.write("\033[0K")
        sys.stdout.flush()
    
    @staticmethod
    def clear_to_end_of_screen():
        """Clear from cursor to end of screen"""
        sys.stdout.write("\033[0J")
        sys.stdout.flush()
    
    @staticmethod
    def enable_mouse():
        """Enable mouse tracking"""
        sys.stdout.write("\033[?1000h\033[?1002h\033[?1006h")
        sys.stdout.flush()
    
    @staticmethod
    def disable_mouse():
        """Disable mouse tracking"""
        sys.stdout.write("\033[?1000l\033[?1002l\033[?1006l")
        sys.stdout.flush()
    
    @staticmethod
    def use_alternate_screen():
        """Switch to alternate screen buffer (prevents scrollbar reset)"""
        sys.stdout.write("\033[?1049h")
        sys.stdout.flush()
    
    @staticmethod
    def use_main_screen():
        """Switch back to main screen buffer"""
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()
    
    @staticmethod
    def set_scroll_region(top: int, bottom: int):
        """Set scroll region from line top to bottom"""
        sys.stdout.write(f"\033[{top};{bottom}r")
        sys.stdout.flush()
    
    @staticmethod
    def reset_scroll_region():
        """Reset scroll region to full screen"""
        sys.stdout.write("\033[r")
        sys.stdout.flush()

# ======================
# ✅ SET TERMINAL TITLE HERE - OUTSIDE THE CLASS
# ======================
Terminal.set_terminal_title(f"💣 {title} - CLI Minesweeper")
print(f"Starting {title}...")

class Color:
    """ANSI color codes and styling"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Bright background colors
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"
    
    # Cursor highlight style - Blue background with white text
    CURSOR_HIGHLIGHT = BG_BRIGHT_BLUE + BRIGHT_WHITE + BOLD

# ======================
# Input Handler
# ======================

class InputHandler:
    """Platform-independent input handler"""
    
    def __init__(self):
        self.setup_terminal()
    
    def setup_terminal(self):
        """Setup terminal for raw input"""
        if os.name != "nt":
            import termios
            import tty
            
            # Save terminal settings
            self.fd = sys.stdin.fileno()
            self.old_term = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
    
    def restore_terminal(self):
        """Restore terminal settings"""
        if os.name != "nt":
            import termios
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_term)
    
    def get_input(self):
        """Get keyboard or mouse input"""
        if os.name == "nt":
            return self._get_windows_input()
        else:
            return self._get_unix_input()
    
    def _get_windows_input(self):
        import msvcrt
        
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            # Arrow keys
            if key == b'\xe0':
                key2 = msvcrt.getch()
                arrows = {
                    b'H': 'up',
                    b'P': 'down', 
                    b'K': 'left',
                    b'M': 'right'
                }
                return ('key', arrows.get(key2, None))
            
            # Special keys
            if key == b'\r':
                return ('key', 'enter')
            elif key == b' ':
                return ('key', 'space')
            elif key == b'\x03':  # Ctrl+C
                return ('key', 'ctrl+c')
            elif key == b'\x1b':  # Escape
                return ('key', 'escape')
            
            # Regular keys
            try:
                return ('key', key.decode().lower())
            except:
                return ('key', None)
        
        return ('none', None)
    
    def _get_unix_input(self):
        import select
        import termios
        import tty
        
        # Small timeout to prevent blocking
        timeout = 0.01
        
        if select.select([sys.stdin], [], [], timeout)[0]:
            ch = sys.stdin.read(1)
            
            # Escape sequence
            if ch == '\x1b':
                # Check for more input with timeout
                if select.select([sys.stdin], [], [], timeout)[0]:
                    ch2 = sys.stdin.read(1)
                    
                    if ch2 == '[':
                        # Check for mouse or arrow keys
                        if select.select([sys.stdin], [], [], timeout)[0]:
                            ch3 = sys.stdin.read(1)
                            
                            # Mouse input (SGR format)
                            if ch3 == '<':
                                # Read mouse sequence
                                seq = ''
                                while select.select([sys.stdin], [], [], timeout)[0]:
                                    c = sys.stdin.read(1)
                                    seq += c
                                    if c in 'Mm':
                                        break
                                
                                # Parse: <b;x;y[Mm]
                                match = re.match(r'(\d+);(\d+);(\d+)([Mm])', seq)
                                if match:
                                    button, x, y, event_type = match.groups()
                                    return ('mouse', (int(x) - 1, int(y) - 1, int(button), event_type))
                            
                            # Arrow keys
                            elif ch3 in 'ABCD':
                                arrows = {
                                    'A': 'up',
                                    'B': 'down',
                                    'C': 'right',
                                    'D': 'left'
                                }
                                return ('key', arrows.get(ch3, None))
                
                # Just escape key
                return ('key', 'escape')
            
            # Special keys
            elif ch == '\n':
                return ('key', 'enter')
            elif ch == ' ':
                return ('key', 'space')
            elif ch == '\x03':  # Ctrl+C
                return ('key', 'ctrl+c')
            
            # Regular keys
            else:
                return ('key', ch.lower())
        
        return ('none', None)

# ======================
# Game Components
# ======================

class Difficulty(Enum):
    BABY = ("baby", 5, 5, 5, "🟦")
    EASY = ("easy", 7, 7, 10, "🟩")
    NORMAL = ("normal", 9, 9, 15, "🟨")
    HARD = ("hard", 16, 16, 40, "🟥")
    EXPERT = ("expert", 30, 16, 99, "⛔")

    def __init__(self, mode, width, height, mines, icon):
        self.mode = mode
        self.width = width
        self.height = height
        self.mines = mines
        self.icon = icon

class Cell:
    """Represents a single cell on the game board"""
    
    def __init__(self):
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.question = False
        self.neighbor_mines = 0
    
    @property
    def char(self) -> str:
        """Get character representation of cell"""
        if self.revealed:
            if self.is_mine:
                return "💣"
            elif self.neighbor_mines > 0:
                return str(self.neighbor_mines)
            else:
                return "·"
        elif self.flagged:
            return "🚩"
        elif self.question:
            return "?"
        else:
            return "▒"
    
    @property
    def color(self) -> str:
        """Get ANSI color for this cell"""
        if not self.revealed:
            if self.flagged:
                return Color.BRIGHT_RED + Color.BOLD
            elif self.question:
                return Color.BRIGHT_YELLOW + Color.BOLD
            return Color.BRIGHT_WHITE
        
        if self.is_mine:
            return Color.BRIGHT_RED + Color.BOLD
        
        # Color by number
        colors = {
            0: Color.BRIGHT_BLACK,
            1: Color.BRIGHT_BLUE,
            2: Color.BRIGHT_GREEN,
            3: Color.BRIGHT_RED,
            4: Color.BRIGHT_MAGENTA,
            5: Color.BRIGHT_YELLOW,
            6: Color.BRIGHT_CYAN,
            7: Color.WHITE,
            8: Color.BRIGHT_BLACK
        }
        return colors.get(self.neighbor_mines, Color.RESET) + Color.BOLD

class Minesweeper:
    """Main game controller"""
    
    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.width = difficulty.width
        self.height = difficulty.height
        self.mine_count = difficulty.mines
        
        # Game state
        self.cursor_x = 0
        self.cursor_y = 0
        self.game_over = False
        self.victory = False
        self.first_move = True
        self.moves = 0
        self.start_time = time.time()
        self.flags_remaining = self.mine_count
        
        # Initialize board
        self.board = [[Cell() for _ in range(self.width)] 
                     for _ in range(self.height)]
        
        # Celebration animation
        self.celebration_active = False
        self.celebration_thread = None
    
    def place_mines(self, safe_x: int, safe_y: int):
        """Place mines, ensuring safe area around first click"""
        all_positions = [(x, y) for y in range(self.height) 
                        for x in range(self.width)]
        
        # Remove safe area (3x3 around first click)
        safe_area = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_area.append((nx, ny))
        
        mine_positions = [pos for pos in all_positions if pos not in safe_area]
        mine_positions = random.sample(mine_positions, self.mine_count)
        
        # Place mines
        for x, y in mine_positions:
            self.board[y][x].is_mine = True
        
        # Calculate neighbors
        self.calculate_neighbors()
    
    def calculate_neighbors(self):
        """Calculate number of neighboring mines for each cell"""
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x].is_mine:
                    continue
                
                count = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dy == 0 and dx == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.board[ny][nx].is_mine:
                                count += 1
                
                self.board[y][x].neighbor_mines = count
    
    def reveal(self, x: int, y: int):
        """Reveal a cell"""
        if self.game_over:
            return
        
        cell = self.board[y][x]
        
        if cell.revealed or cell.flagged:
            return
        
        # First move protection
        if self.first_move:
            self.place_mines(x, y)
            self.first_move = False
        
        cell.revealed = True
        self.moves += 1
        
        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return
        
        # Flood fill if empty
        if cell.neighbor_mines == 0:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if not self.board[ny][nx].revealed and not self.board[ny][nx].flagged:
                            self.reveal(nx, ny)
        
        # Check win
        self.check_victory()
    
    def toggle_flag(self, x: int, y: int):
        """Toggle flag/question mark"""
        if self.game_over:
            return
        
        cell = self.board[y][x]
        
        if cell.revealed:
            return
        
        if cell.flagged:
            cell.flagged = False
            cell.question = True
            self.flags_remaining += 1
        elif cell.question:
            cell.question = False
        elif self.flags_remaining > 0:
            cell.flagged = True
            self.flags_remaining -= 1
    
    def chord(self, x: int, y: int):
        """Reveal neighbors if flag count matches"""
        if self.game_over:
            return
        
        cell = self.board[y][x]
        
        if not cell.revealed or cell.neighbor_mines == 0:
            return
        
        # Count flags around
        flag_count = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.board[ny][nx].flagged:
                        flag_count += 1
        
        # Reveal if flags match
        if flag_count == cell.neighbor_mines:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue
                    
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if not self.board[ny][nx].flagged and not self.board[ny][nx].revealed:
                            self.reveal(nx, ny)
    
    def reveal_all_mines(self):
        """Reveal all mines when game is lost"""
        for row in self.board:
            for cell in row:
                if cell.is_mine:
                    cell.revealed = True
    
    def check_victory(self):
        """Check if player has won"""
        for row in self.board:
            for cell in row:
                if not cell.is_mine and not cell.revealed:
                    return
        
        self.victory = True
        self.game_over = True
        self.flags_remaining = 0
        
        # Start celebration in background
        if not self.celebration_active:
            self.celebration_active = True
            self.celebration_thread = threading.Thread(target=self.show_celebration, daemon=True)
            self.celebration_thread.start()
    
    def show_celebration(self):
        """Show a terminal-based celebration animation"""
        # Save current screen position
        Terminal.save_cursor()
        
        # Calculate center position for celebration
        center_x = 40
        center_y = 10
        
        celebration_messages = [
            "🎉 VICTORY! 🎉",
            "Mines cleared!",
            "Excellent work!",
            "You're a pro!",
            "Flawless victory!"
        ]
        
        colors = [Color.BRIGHT_RED, Color.BRIGHT_GREEN, Color.BRIGHT_YELLOW, 
                 Color.BRIGHT_BLUE, Color.BRIGHT_MAGENTA, Color.BRIGHT_CYAN]
        
        fireworks = ["✨", "🎇", "🎆", "💥", "🌟", "⭐", "💫", "🎊"]
        
        # Create fireworks particles
        particles = []
        for _ in range(20):
            x = random.randint(center_x - 20, center_x + 20)
            y = random.randint(center_y - 5, center_y + 5)
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            char = random.choice(fireworks)
            color = random.choice(colors)
            life = random.randint(30, 60)
            particles.append([x, y, dx, dy, char, color, life])
        
        # Animation loop
        for frame in range(60):  # 3 seconds at 20fps
            if not self.celebration_active:
                break
            
            # Move and update particles
            for i in range(len(particles)):
                particles[i][0] += particles[i][2]
                particles[i][1] += particles[i][3]
                particles[i][6] -= 1
                
                # Add gravity
                particles[i][3] += 0.05
                
                # Bounce off walls
                if particles[i][0] < 10 or particles[i][0] > 70:
                    particles[i][2] *= -0.8
                if particles[i][1] < 2 or particles[i][1] > 20:
                    particles[i][3] *= -0.8
            
            # Remove dead particles
            particles = [p for p in particles if p[6] > 0]
            
            # Add new particles occasionally
            if len(particles) < 20 and frame % 5 == 0:
                x = center_x
                y = center_y
                angle = random.uniform(0, 6.28)
                speed = random.uniform(1, 3)
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed
                char = random.choice(fireworks)
                color = random.choice(colors)
                life = random.randint(30, 60)
                particles.append([x, y, dx, dy, char, color, life])
            
            # Draw celebration
            Terminal.move_cursor(center_x - 10, center_y - 2)
            sys.stdout.write(" " * 40)
            
            # Draw message
            message = random.choice(celebration_messages)
            Terminal.move_cursor(center_x - len(message)//2, center_y)
            sys.stdout.write(f"{Color.BRIGHT_YELLOW}{Color.BOLD}{message}{Color.RESET}")
            
            # Draw particles
            for x, y, _, _, char, color, _ in particles:
                if 1 <= x <= 80 and 1 <= y <= 24:
                    Terminal.move_cursor(int(x), int(y))
                    sys.stdout.write(f"{color}{char}{Color.RESET}")
            
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Clean up
        self.celebration_active = False
        Terminal.restore_cursor()
    
    @property
    def elapsed_time(self):
        """Get elapsed time in seconds"""
        return int(time.time() - self.start_time)
    
    @property
    def face(self):
        """Get face emoji based on game state"""
        if self.victory:
            return "😎"
        elif self.game_over:
            return "💀"
        else:
            return "🙂"
    
    def render_cell(self, x: int, y: int, cursor: bool = False) -> str:
        """Render a complete cell where content is always 2 cells wide"""
        cell = self.board[y][x]
        char = cell.char
        
        # THE SIMPLE FIX: Make everything 2 cells wide
        # If char looks like an emoji (starts with high Unicode), don't pad
        # Otherwise, add a space
        if char and ord(char[0]) > 1000:  # Probably an emoji
            content = char  # Keep as is (2 cells)
        else:
            content = char + " "  # Add space (makes 2 cells)
        
        # Color the content
        colored = f"{cell.color}{content}{Color.RESET}"
        
        # Add brackets with optional cursor highlight
        if cursor and not self.game_over:
            return f"{Color.CURSOR_HIGHLIGHT}[{colored}]{Color.RESET}"
        return f"[{colored}]"
    
    def render_header(self) -> List[str]:
        """Render game header"""
        width = max(50, self.width * 3 + 10)
        header = []
        
        # Title
        title = f"💣 GridLock 💣"
        header.append(f"{Color.BRIGHT_CYAN}{title:^{width}}{Color.RESET}")
        header.append(f"{Color.BRIGHT_WHITE}{'='*width}{Color.RESET}")
        header.append("")  # Empty line
        
        # Stats
        time_color = Color.BRIGHT_GREEN if not self.game_over else Color.BRIGHT_RED
        stats = (f"{time_color}Time: {self.elapsed_time:03d}s{Color.RESET} | "
                f"{Color.BRIGHT_RED}Mines: {self.flags_remaining:02d}/{self.mine_count:02d}{Color.RESET} | "
                f"{Color.BRIGHT_GREEN}Moves: {self.moves:03d}{Color.RESET} | "
                f"Face: {self.face}")
        header.append(stats)
        header.append("")  # Empty line
        
        # Column numbers
        col_nums = "   " + " ".join(f"{i:2}" for i in range(self.width))
        header.append(Color.BRIGHT_BLACK + col_nums + Color.RESET)
        
        return header
    
    def render_board(self) -> List[str]:
        """Render game board"""
        board_lines = []
        
        for y in range(self.height):
            # Row number
            line = f"{Color.BRIGHT_BLACK}{y:2} {Color.RESET}"
            
            for x in range(self.width):
                cursor = (x == self.cursor_x and y == self.cursor_y)
                cell_str = self.render_cell(x, y, cursor)
                line += cell_str
            
            board_lines.append(line)
        
        return board_lines
    
    def render_footer(self) -> List[str]:
        """Render game footer with controls"""
        width = max(50, self.width * 3 + 10)
        footer = []
        
        footer.append("")  # Empty line
        footer.append(f"{Color.BRIGHT_WHITE}{'='*width}{Color.RESET}")
        footer.append("")  # Empty line
        
        if self.game_over:
            if self.victory:
                message = f"{Color.BRIGHT_GREEN}🎉 VICTORY! You won in {self.elapsed_time}s! 🎉{Color.RESET}"
                footer.append(message.center(width))
            else:
                message = f"{Color.BRIGHT_RED}💀 GAME OVER! Better luck next time!{Color.RESET}"
                footer.append(message.center(width))
            
            footer.append("")  # Empty line
            footer.append(f"{Color.BRIGHT_YELLOW}Press:{Color.RESET}")
            footer.append(f"  {Color.BRIGHT_GREEN}[SPACE]{Color.RESET} - Play again (same difficulty)")
            footer.append(f"  {Color.BRIGHT_GREEN}[M]{Color.RESET}     - Main menu")
            footer.append(f"  {Color.BRIGHT_GREEN}[Q]{Color.RESET}     - Quit game")
        else:
            controls = [
                f"{Color.BRIGHT_CYAN}Controls:{Color.RESET}",
                "Arrows/WASD: Move",
                "Space/Enter: Reveal",
                "F: Flag",
                "Q: Question mark",
                "C: Chord",
                "R: Restart",
                "M: Menu",
                "ESC: Quit"
            ]
            
            # Split controls into lines that fit the width
            current_line = ""
            for control in controls:
                if len(current_line) + len(control) + 3 > width:
                    footer.append(current_line)
                    current_line = control
                else:
                    if current_line:
                        current_line += " | " + control
                    else:
                        current_line = control
            
            if current_line:
                footer.append(current_line)
        
        return footer
    
    def render(self) -> List[str]:
        """Render complete game screen"""
        screen = []
        screen.extend(self.render_header())
        screen.extend(self.render_board())
        screen.extend(self.render_footer())
        return screen

# ======================
# Screen Manager
# ======================

class ScreenManager:
    """Manages terminal screen updates efficiently"""
    
    def __init__(self):
        self.last_screen = []
        self.screen_height = 0
        self.input_handler = InputHandler()
        self.setup_terminal()
    
    def setup_terminal(self):
        """Setup terminal for the game"""
        # Update terminal title
        Terminal.set_terminal_title(f"💣 {title} - CLI Minesweeper")
        
        # Switch to alternate screen buffer
        Terminal.use_alternate_screen()
        Terminal.clear_screen()
        
        # Hide cursor initially
        Terminal.hide_cursor()
        
        # Enable mouse
        Terminal.enable_mouse()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.cleanup()
        print(f"\n{Color.BRIGHT_YELLOW}Game interrupted. Thanks for playing! 👋{Color.RESET}")
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup terminal settings"""
        # Reset terminal title
        Terminal.set_terminal_title("Terminal")
        
        Terminal.show_cursor()
        Terminal.disable_mouse()
        Terminal.use_main_screen()
        self.input_handler.restore_terminal()
        sys.stdout.write(Color.RESET)
        sys.stdout.flush()
    
    def update_screen(self, screen_lines: List[str]):
        """Update screen efficiently"""
        # Always start at top-left
        Terminal.move_cursor(1, 1)
        
        # Calculate needed height
        needed_height = len(screen_lines)
        
        # If screen size changed or first render, draw everything
        if needed_height != self.screen_height or not self.last_screen:
            for i, line in enumerate(screen_lines):
                if i > 0:
                    sys.stdout.write("\n")
                sys.stdout.write(line)
                sys.stdout.flush()
            
            # Clear any remaining lines from previous render
            if self.screen_height > needed_height:
                for i in range(needed_height, self.screen_height):
                    sys.stdout.write("\n")
                    Terminal.clear_line()
            
            self.screen_height = needed_height
            self.last_screen = screen_lines.copy()
            return
        
        # Update only changed lines
        for i, (new_line, old_line) in enumerate(zip(screen_lines, self.last_screen)):
            if new_line != old_line:
                Terminal.move_cursor(1, i + 1)
                Terminal.clear_line()
                sys.stdout.write(new_line)
                sys.stdout.flush()
        
        # Clear any extra lines from previous render
        if len(self.last_screen) > len(screen_lines):
            for i in range(len(screen_lines), len(self.last_screen)):
                Terminal.move_cursor(1, i + 1)
                Terminal.clear_line()
                sys.stdout.flush()
        
        # Update last screen
        self.last_screen = screen_lines.copy()
        
        # Ensure cursor is at bottom
        Terminal.move_cursor(1, needed_height + 1)
    
    def get_input(self):
        """Get input from user"""
        return self.input_handler.get_input()

# ======================
# Menu System
# ======================

class Menu:
    """Menu system for the game"""
    
    @staticmethod
    def show_main(screen_manager: ScreenManager) -> Difficulty:
        """Show main menu"""
        while True:
            screen = Menu._render_main_menu()
            screen_manager.update_screen(screen)
            
            action, value = screen_manager.get_input()
            
            if action == 'key':
                if value == 'escape' or value == 'ctrl+c':
                    raise KeyboardInterrupt
                
                for diff in Difficulty:
                    if value == diff.value[0][0]:
                        return diff
    
    @staticmethod
    def _render_main_menu() -> List[str]:
        """Render main menu"""
        lines = []
        
        lines.append("")
        title = "💣 GridLock 💣"
        lines.append(f"{Color.BRIGHT_CYAN}{title:^50}{Color.RESET}")
        lines.append(f"{Color.BRIGHT_WHITE}{'='*50}{Color.RESET}")
        lines.append("")
        lines.append(f"{Color.BRIGHT_YELLOW}Select Difficulty:{Color.RESET}")
        lines.append("")
        
        for diff in Difficulty:
            lines.append(f"  {Color.BRIGHT_GREEN}[{diff.value[0][0]}]{Color.RESET} "
                        f"{diff.icon} {Color.BRIGHT_WHITE}{diff.mode.title():8}{Color.RESET} "
                        f"{diff.width}x{diff.height} with {diff.mines} mines")
        
        lines.append("")
        lines.append(f"{Color.BRIGHT_WHITE}{'='*50}{Color.RESET}")
        lines.append(f"{Color.BRIGHT_CYAN}Controls:{Color.RESET}")
        lines.append("  Arrow keys / WASD: Move cursor")
        lines.append("  Space / Enter:     Reveal cell")
        lines.append("  F:                 Toggle flag")
        lines.append("  Q:                 Question mark")
        lines.append("  C:                 Chord")
        lines.append("  ESC:               Quit game")
        lines.append("  Mouse:             Click to interact")
        
        return lines

# ======================
# Main Game
# ======================

def main():
    """Main game loop"""
    screen_manager = None
    
    try:
        screen_manager = ScreenManager()
        
        while True:
            # Show menu and get difficulty
            difficulty = Menu.show_main(screen_manager)
            
            # Game session
            while True:
                game = Minesweeper(difficulty)
                game_over_action = None
                
                # Game loop
                while not game.game_over:
                    # Render game
                    screen = game.render()
                    screen_manager.update_screen(screen)
                    
                    # Handle input
                    action, value = screen_manager.get_input()
                    
                    if action == 'mouse':
                        x, y, button, event_type = value
                        
                        # Convert to board coordinates
                        # Each cell is 3 chars wide: [X], header is 6 lines
                        board_x = x // 3
                        board_y = y - 6  # Adjust for header
                        
                        if 0 <= board_x < game.width and 0 <= board_y < game.height:
                            # Move cursor to clicked cell
                            game.cursor_x = board_x
                            game.cursor_y = board_y
                            
                            if event_type == 'M':  # Mouse down
                                if button == 0:  # Left click
                                    game.reveal(board_x, board_y)
                                elif button == 2:  # Right click
                                    game.toggle_flag(board_x, board_y)
                    
                    elif action == 'key':
                        if value == 'escape':
                            screen_manager.cleanup()
                            print(f"\n{Color.BRIGHT_YELLOW}Thanks for playing! 👋{Color.RESET}")
                            return
                        elif value == 'ctrl+c':
                            raise KeyboardInterrupt
                        elif value == 'r':
                            break  # Restart game
                        elif value == 'm':
                            game_over_action = 'menu'
                            break
                        
                        # Movement
                        if value in ('left', 'a', 'h'):
                            game.cursor_x = max(0, game.cursor_x - 1)
                        elif value in ('right', 'd', 'l'):
                            game.cursor_x = min(game.width - 1, game.cursor_x + 1)
                        elif value in ('up', 'w', 'k'):
                            game.cursor_y = max(0, game.cursor_y - 1)
                        elif value in ('down', 's', 'j'):
                            game.cursor_y = min(game.height - 1, game.cursor_y + 1)
                        
                        # Actions
                        elif value in (' ', 'enter'):
                            game.reveal(game.cursor_x, game.cursor_y)
                        elif value == 'f':
                            game.toggle_flag(game.cursor_x, game.cursor_y)
                        elif value == 'q':
                            game.toggle_flag(game.cursor_x, game.cursor_y)  # Cycle flag/question
                        elif value == 'c':
                            game.chord(game.cursor_x, game.cursor_y)
                
                # Game over - show final state
                screen = game.render()
                screen_manager.update_screen(screen)
                
                # Wait for input in game over state
                while game.game_over and game_over_action is None:
                    action, value = screen_manager.get_input()
                    
                    if action == 'key':
                        if value == ' ':
                            game_over_action = 'restart'
                        elif value == 'm':
                            game_over_action = 'menu'
                        elif value == 'q' or value == 'escape':
                            game_over_action = 'quit'
                        elif value == 'ctrl+c':
                            raise KeyboardInterrupt
                
                if game_over_action == 'restart':
                    continue
                elif game_over_action == 'menu':
                    break
                elif game_over_action == 'quit':
                    screen_manager.cleanup()
                    print(f"\n{Color.BRIGHT_YELLOW}Thanks for playing! 👋{Color.RESET}")
                    return
    
    except KeyboardInterrupt:
        print(f"\n{Color.BRIGHT_YELLOW}Thanks for playing! 👋{Color.RESET}")
    
    except Exception as e:
        if screen_manager:
            screen_manager.cleanup()
        print(f"\n{Color.BRIGHT_RED}Error: {e}{Color.RESET}")
        import traceback
        traceback.print_exc()
    
    finally:
        if screen_manager:
            screen_manager.cleanup()

if __name__ == "__main__":
    main()
