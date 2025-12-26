import pygame
import sys
from constants import *
from board import Board
from ai_solver import AI_Solver
from button import Button

# --- 5. MENU & APP MANAGEMENT ---
class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen_w = 800
        self.screen_h = 600
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Minesweeper Graph AI")
        self.clock = pygame.time.Clock()
        
        # --- FONTS ---
        self.font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 40, bold=True)
        # NEW: Extra Large font for the main title
        self.font_xl = pygame.font.SysFont("Segoe UI", 80, bold=True) 

        # ... (rest of your init code remains the same) ...
        self.grid_size = 16
        self.difficulty = "Medium" 
        self.mode = "Menu" 
        self.vs_cpu = False
        self.cell_size = CELL_SIZE 
        
        # ... (Background loading code remains the same) ...
        self.bg_image = None
        bg_path = r"Images\Startup-Page-BG-Image.jpg"
        try:
            loaded_img = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.smoothscale(loaded_img, (self.screen_w, self.screen_h))
        except Exception as e:
            print(f"Could not load background: {e}")
            self.bg_image = None

    def run(self):
        while True:
            if self.mode == "Menu":
                self.menu_loop()
            elif self.mode == "Settings":
                self.settings_loop()
            elif self.mode == "Game":
                self.game_loop()

    def calc_mines(self):
        total = self.grid_size * self.grid_size
        ratio = 0.12 if self.difficulty == "Easy" else 0.17 if self.difficulty == "Medium" else 0.22
        return int(total * ratio)

    # --- HELPER: FAST BLUR TRICK ---
    def get_blurred_background(self):
        if not self.bg_image: return None
        
        # 1. Scale down significantly (this loses detail)
        # 40% blur feel = scaling down to about 10% of original size
        small_w = self.screen_w // 10
        small_h = self.screen_h // 10
        small_surf = pygame.transform.smoothscale(self.bg_image, (small_w, small_h))
        
        # 2. Scale back up (this creates the blur)
        blurred_surf = pygame.transform.smoothscale(small_surf, (self.screen_w, self.screen_h))
        
        # 3. Add a dark overlay so white text is readable
        dark_overlay = pygame.Surface((self.screen_w, self.screen_h))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(100) # Semi-transparent black
        blurred_surf.blit(dark_overlay, (0,0))
        
        return blurred_surf

    # --- HELPER: SMOOTH FADE TRANSITION ---
    def fade_transition(self):
        fade_surf = pygame.Surface((self.screen_w, self.screen_h))
        fade_surf.fill((0, 0, 0))
        
        # Fade Out Loop (Transparent -> Black)
        for alpha in range(0, 255, 15): # Speed of fade (increase 15 to make faster)
            fade_surf.set_alpha(alpha)
            # Redraw current screen content behind the fade
            # (We skip complex redrawing here for simplicity, just drawing over)
            self.screen.blit(fade_surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10) # Smoothness delay

    def menu_loop(self):
        # Buttons positioned lower on the "floor" of the grid image
        btn_single = Button(300, 400, 200, 50, "SOLO SWEEPER") 
        btn_cpu = Button(290, 470, 220, 50, "MIND VS MACHINE")

        while self.mode == "Menu":
            if self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill(C_BG)

            # --- TITLE ADJUSTMENT ---
            # Using font_xl (Size 80)
            # MOVED DOWN: Y coordinate changed from 230 to 320
            
            # 1. Draw Drop Shadow (Black) for depth
            shadow = self.font_xl.render("MINESWEEPER AI", True, (0, 0, 0))
            # Center Y is now 320 (+4 offset for shadow)
            shadow_rect = shadow.get_rect(center=(self.screen_w // 2 + 4, 290 + 4))
            self.screen.blit(shadow, shadow_rect)

            # 2. Draw Main Title (Cyan Accent to match the grid)
            title = self.font_xl.render("MINESWEEPER AI", True, C_ACCENT)
            # Center Y is now 320
            title_rect = title.get_rect(center=(self.screen_w // 2, 290))
            self.screen.blit(title, title_rect)

            btn_single.draw(self.screen, self.font)
            btn_cpu.draw(self.screen, self.font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if btn_single.is_clicked(event):
                    self.fade_transition()
                    self.vs_cpu = False
                    self.mode = "Settings"
                    return 

                if btn_cpu.is_clicked(event):
                    self.fade_transition()
                    self.vs_cpu = True
                    self.mode = "Settings"
                    return

            pygame.display.flip()
            self.clock.tick(60)

    def settings_loop(self):
        # --- PREPARE BLURRED BACKGROUND ---
        # We generate this once before the loop starts to save CPU
        bg_blur = self.get_blurred_background()

        btns_size = []
        sizes = [8, 12, 16, 20]
        for i, s in enumerate(sizes):
            col = C_ACCENT if self.grid_size == s else C_PANEL
            btns_size.append(Button(200 + i*70, 200, 60, 40, str(s), color=col))

        btns_diff = []
        diffs = ["Easy", "Medium", "Hard"]
        for i, d in enumerate(diffs):
            col = C_ACCENT if self.difficulty == d else C_PANEL
            btns_diff.append(Button(200 + i*120, 300, 100, 40, d, color=col))

        btn_start = Button(300, 450, 200, 60, "START GAME", color=C_FLAG)

        # Fade In (Optional: Black -> Transparent)
        # Just a quick flash to show we arrived
        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.time.delay(100)

        while self.mode == "Settings":
            # Draw Blurred Background
            if bg_blur:
                self.screen.blit(bg_blur, (0, 0))
            else:
                self.screen.fill(C_BG)

            title = self.font_lg.render("GAME SETUP", True, C_ACCENT)
            self.screen.blit(title, (280, 100))

            lbl_size = self.font.render("GRID SIZE:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_size, (80, 210))
            for b in btns_size: b.draw(self.screen, self.font)

            lbl_diff = self.font.render("DIFFICULTY:", True, C_TEXT_MAIN)
            self.screen.blit(lbl_diff, (60, 310))
            for b in btns_diff: b.draw(self.screen, self.font)

            btn_start.draw(self.screen, self.font)
            
            info = f"Mines: {self.calc_mines()}"
            info_surf = self.font.render(info, True, (200, 200, 200)) # Brighter text for blurred bg
            self.screen.blit(info_surf, (350, 400))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                for i, b in enumerate(btns_size):
                    if b.is_clicked(event): 
                        self.grid_size = sizes[i]
                        for k, bx in enumerate(btns_size): bx.color = C_ACCENT if k == i else C_PANEL
                
                for i, b in enumerate(btns_diff):
                    if b.is_clicked(event): 
                        self.difficulty = diffs[i]
                        for k, bx in enumerate(btns_diff): bx.color = C_ACCENT if k == i else C_PANEL
                
                if btn_start.is_clicked(event):
                    self.fade_transition()
                    self.mode = "Game"
                    return

            pygame.display.flip()
            self.clock.tick(60)

    def game_loop(self):
        # --- HELPER: Resizes the actual window (Call this only when necessary) ---
        def update_window_size():
            # Calculate required width/height based on grid
            grid_px = self.grid_size * int(self.cell_size) # Use int() to stabilize
            req_w = MARGIN * 2 + grid_px + SIDEBAR_WIDTH
            req_h = MARGIN * 2 + grid_px
            
            # Minimum limits
            if req_h < 600: req_h = 600
            if req_w < 800: req_w = 800
            
            # Only resize if the window size actually needs to change
            current_w, current_h = self.screen.get_size()
            if int(req_w) != current_w or int(req_h) != current_h:
                self.screen = pygame.display.set_mode((int(req_w), int(req_h)))
            return int(req_w), int(req_h)

        # Initial Setup
        game_w, game_h = update_window_size()

        def init_game():
            return Board(self.grid_size, self.grid_size, self.calc_mines())

        board = init_game()
        ai = AI_Solver()
        turn = "Human"
        scores = {"Human": {'RS':0, 'CF':0, 'WF':0}, "AI": {'RS':0, 'CF':0, 'WF':0}}
        ai_timer = 0
        hint = None 
        
        # --- TIMER LOGIC VARIABLES ---
        game_started = False
        start_ticks = 0
        elapsed_time = 0
        
        # Resize Variables
        is_resizing = False
        font_log = pygame.font.SysFont("Consolas", 14)
        
        running = True
        while running:
            self.screen.fill(C_BG)
            mouse_pos = pygame.mouse.get_pos()
            
            # Calculate layout based on CURRENT cell_size
            grid_px = self.grid_size * int(self.cell_size)
            sidebar_x = MARGIN + grid_px + 40
            
            # --- FIX: DEFINE BUTTONS HERE (OUTSIDE THE EVENT LOOP) ---
            # Re-create buttons every frame to match dynamic window width
            btn_back = Button(game_w - 120, game_h - 50, 100, 30, "MENU", color=C_PANEL)
            btn_reset = Button(game_w - 120, game_h - 90, 100, 30, "RESET", color=C_PANEL)
            btn_undo = Button(game_w - 230, game_h - 50, 100, 30, "UNDO", color=C_PANEL)
            btn_hint = Button(game_w - 230, game_h - 90, 100, 30, "HINT", color=(100, 100, 120))

            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # --- 1. RESIZE LOGIC (SMOOTH & LOW SENSITIVITY) ---
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle is at the bottom-right of the grid
                    handle_rect = pygame.Rect(MARGIN + grid_px, MARGIN + grid_px, 25, 25)
                    if handle_rect.collidepoint(event.pos):
                        is_resizing = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if is_resizing:
                        is_resizing = False
                        # ONLY Resize the actual window when you LET GO
                        game_w, game_h = update_window_size()

                if event.type == pygame.MOUSEMOTION and is_resizing:
                    dx = event.rel[0]
                    dy = event.rel[1]
                    # Sensitivity Fix: We divide by 10 to slow it down
                    change = (dx + dy) / 20 
                    self.cell_size += change
                    
                    # Clamp size limits
                    if self.cell_size < 15: self.cell_size = 15
                    if self.cell_size > 50: self.cell_size = 50
                    # Note: We do NOT call update_window_size() here. This stops the flickering.

                # --- BUTTONS & GAMEPLAY ---
                if btn_back.is_clicked(event):
                    self.mode = "Menu"
                    self.screen = pygame.display.set_mode((800, 600)) 
                    return

                if btn_reset.is_clicked(event):
                    board = init_game()
                    scores = {"Human": {'RS':0, 'CF':0, 'WF':0}, "AI": {'RS':0, 'CF':0, 'WF':0}}
                    turn = "Human"
                    hint = None
                    ai.log("Game Reset.")
                    # Reset Timer
                    game_started = False
                    start_ticks = 0
                    elapsed_time = 0

                if btn_undo.is_clicked(event):
                    if turn == "Human" and board.undo():
                         ai.log("Undo successful.")
                         hint = None

                if btn_hint.is_clicked(event):
                      move = ai.get_move(board, is_hint=True)
                      if move:
                          hint = move 
                          ai.log("Hint: Logic found.")
                      else:
                          ai.log("Hint: No strict logic found.")

                # Click on Grid
                if event.type == pygame.MOUSEBUTTONDOWN and not board.game_over and not is_resizing:
                    mx, my = event.pos
                    # Check if click is inside grid bounds
                    if MARGIN <= mx < MARGIN + grid_px and \
                       MARGIN <= my < MARGIN + grid_px:
                        
                        c = int((mx - MARGIN) // self.cell_size)
                        r = int((my - MARGIN) // self.cell_size)
                        
                        if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                            if turn == "Human":
                                # --- TIMER START LOGIC ---
                                if not game_started:
                                    game_started = True
                                    start_ticks = pygame.time.get_ticks()

                                action_taken = False
                                points = 0
                                
                                if event.button == 1: # Left Click
                                    cell = board.grid[r][c]
                                    if not cell.is_revealed:
                                        res = board.reveal(r, c)
                                        if res == -999:
                                            ai.log("Human Hit Mine! Game Over.")
                                            board.winner = "AI"
                                        else:
                                            points = res
                                            action_taken = True
                                    elif cell.is_revealed: # Chording
                                        res = board.chord(r, c)
                                        if res == -999:
                                            ai.log("Human Chording Hit Mine!")
                                            board.winner = "AI"
                                        elif res > 0:
                                            points = res
                                            action_taken = True
                                    
                                elif event.button == 3: # Right Click
                                    if board.toggle_flag(r, c):
                                        action_taken = True
                                        if board.grid[r][c].is_mine: scores['Human']['CF'] += 1
                                        else: scores['Human']['WF'] += 1

                                if action_taken:
                                    hint = None 
                                    scores['Human']['RS'] += points
                                    if not board.game_over and self.vs_cpu:
                                        turn = "AI"
                                        ai_timer = 45 

            # --- AI LOGIC ---
            if self.vs_cpu and turn == "AI" and not board.game_over:
                ai_timer -= 1
                if ai_timer <= 0:
                    move = ai.get_move(board)
                    if move:
                        r, c, act = move
                        if act == 'reveal':
                            res = board.reveal(r, c)
                            if res == -999:
                                ai.log("AI Hit Mine! Game Over.")
                                board.winner = "Human"
                            else:
                                scores['AI']['RS'] += res
                        elif act == 'flag':
                            board.toggle_flag(r, c)
                            if board.grid[r][c].is_mine: scores['AI']['CF'] += 1
                            else: scores['AI']['WF'] += 1
                    turn = "Human"

            # --- UPDATE TIMER CALCULATION ---
            if game_started and not board.game_over:
                elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

            # --- DRAWING ---
            
            # 1. DRAW GRID
            # Use int(self.cell_size) to keep grid sharp
            draw_cell_size = int(self.cell_size)
            
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    x = MARGIN + c * draw_cell_size
                    y = MARGIN + r * draw_cell_size
                    cell = board.grid[r][c]
                    rect = pygame.Rect(x, y, draw_cell_size-1, draw_cell_size-1) # -1 for grid lines
                    
                    if cell.is_revealed:
                        pygame.draw.rect(self.screen, C_CELL_REVEALED, rect, border_radius=4)
                        if cell.is_mine:
                            pygame.draw.circle(self.screen, C_MINE, rect.center, draw_cell_size//4)
                        elif cell.number > 0:
                            dyn_font = pygame.font.SysFont("Segoe UI", int(draw_cell_size * 0.7), bold=True)
                            txt = dyn_font.render(str(cell.number), True, C_NUMS[cell.number])
                            self.screen.blit(txt, txt.get_rect(center=rect.center))
                    else:
                        is_hover = rect.collidepoint(mouse_pos)
                        col = C_CELL_HOVER if (is_hover and not board.game_over) else C_CELL_HIDDEN
                        pygame.draw.rect(self.screen, col, rect, border_radius=4)
                        if cell.is_flagged:
                            off = 5 * (draw_cell_size / 35) 
                            pts = [(rect.centerx-off, rect.centery+off), 
                                   (rect.centerx-off, rect.centery-off), 
                                   (rect.centerx+off, rect.centery)]
                            pygame.draw.polygon(self.screen, C_FLAG, pts)
                    
                    if hint and hint[0] == r and hint[1] == c:
                        h_col = C_HINT_SAFE if hint[2] == 'reveal' else C_HINT_MINE
                        pygame.draw.rect(self.screen, h_col, rect, 3, border_radius=4)

            # 2. DRAW RESIZE HANDLE (Visual Only)
            h_x = MARGIN + grid_px
            h_y = MARGIN + grid_px
            # Draw a little triangle corner
            pygame.draw.line(self.screen, (150, 150, 150), (h_x, h_y), (h_x + 15, h_y + 15), 3)
            pygame.draw.line(self.screen, (150, 150, 150), (h_x + 6, h_y + 15), (h_x + 15, h_y + 6), 2)
            
            # 3. SIDEBAR BACKGROUND
            # We draw this large enough to cover previous frames if resizing
            pygame.draw.rect(self.screen, C_PANEL, (sidebar_x, MARGIN, SIDEBAR_WIDTH, game_h - MARGIN*2), border_radius=10)
            pygame.draw.rect(self.screen, C_ACCENT, (sidebar_x, MARGIN, SIDEBAR_WIDTH, game_h - MARGIN*2), 2, border_radius=10)

            # 4. DRAW TIMER (High Visibility)
            mins = elapsed_time // 60
            secs = elapsed_time % 60
            time_str = f"{mins:02}:{secs:02}"
            
            # Change color if active so you know it's working
            timer_color = C_ACCENT if game_started else (100, 100, 100)
            
            time_lbl = self.font.render("TIME", True, (150,150,150))
            self.screen.blit(time_lbl, (sidebar_x + 20, MARGIN + 20))
            
            time_surf = self.font_lg.render(time_str, True, timer_color)
            self.screen.blit(time_surf, (sidebar_x + 20, MARGIN + 45))

            # 5. REST OF UI
            status = f"TURN: {turn}"
            if board.game_over: status = f"WINNER: {board.winner}"
            lbl_stat = self.font.render(status, True, C_ACCENT if not board.game_over else C_MINE)
            self.screen.blit(lbl_stat, (sidebar_x + 20, MARGIN + 100))

            def draw_score(lbl, s, y):
                val = s['RS'] + 2*s['CF'] - s['WF']
                txt = self.font.render(f"{lbl}: {val}", True, C_TEXT_MAIN)
                self.screen.blit(txt, (sidebar_x + 20, y))
            
            draw_score("HUMAN", scores['Human'], MARGIN + 140)
            if self.vs_cpu:
                draw_score("AI CPU", scores['AI'], MARGIN + 170)

            # Logs
            log_y_start = MARGIN + 220
            pygame.draw.line(self.screen, (60,60,70), (sidebar_x+10, log_y_start), (sidebar_x+SIDEBAR_WIDTH-10, log_y_start))
            for i, l in enumerate(reversed(ai.logs)):
                txt = font_log.render(f"> {l}", True, (180,180,180))
                self.screen.blit(txt, (sidebar_x + 20, log_y_start + 10 + i*20))

            btn_back.draw(self.screen, self.font)
            btn_reset.draw(self.screen, self.font)
            btn_undo.draw(self.screen, self.font)
            btn_hint.draw(self.screen, self.font)

            pygame.display.flip()
            self.clock.tick(60)
