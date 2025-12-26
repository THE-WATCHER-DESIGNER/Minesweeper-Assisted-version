import random

# --- 3. GREEDY AI SOLVER ---
# --- 3. RULE-ACCURATE AI SOLVER ---
class AI_Solver:
    def __init__(self):
        self.logs = ["Game Started. AI Ready."]

    def log(self, message):
        self.logs.append(message)
        if len(self.logs) > 8: self.logs.pop(0)

    def get_move(self, board, is_hint=False):
        frontier = board.get_revealed_numbered_nodes()
        
        # We separate moves into "Must Flag" and "Must Reveal"
        # The rules say: "Once you think you know the location of all the mines... 
        # you can use this function (left click) to avoid having to click one by one."
        
        moves_reveal = []
        moves_flag = []
        
        for cell in frontier:
            hidden = board.get_hidden_neighbors(cell)
            flagged = board.get_flagged_neighbors(cell)
            
            if not hidden: continue

            # RULE 1: SATISFACTION (Chording / Clear Around)
            # "If the square has exactly as many flags surrounding it as it should have mines..."
            if len(flagged) == cell.number:
                # "...then all the covered squares next to it which are not flagged will be uncovered."
                for h in hidden:
                    if h not in moves_reveal:
                        moves_reveal.append(h)

            # RULE 2: DEDUCTION (Mine Finding)
            # If the number of hidden squares + existing flags EXACTLY equals the number...
            # Then ALL hidden squares MUST be mines.
            elif (cell.number - len(flagged)) == len(hidden):
                for h in hidden:
                    if h not in moves_flag:
                        moves_flag.append(h)

        # --- EXECUTION ORDER (Crucial for "Official" Feel) ---
        
        # 1. DO WE HAVE SAFE SPOTS? (The "Clear Around" move)
        # The AI should immediately open safe areas to expand the map.
        if moves_reveal:
            target = moves_reveal[0]
            if not is_hint: 
                self.log(f"AI: Safe 'Clear Around' at ({target.r},{target.c})")
            return (target.r, target.c, 'reveal')

        # 2. DO WE HAVE OBVIOUS MINES?
        # Only flag if we can't safely expand the map yet.
        if moves_flag:
            target = moves_flag[0]
            if not is_hint: 
                self.log(f"AI: Flagging deduced mine at ({target.r},{target.c})")
            return (target.r, target.c, 'flag')

        # 3. GUESS (Only if stuck)
        if not is_hint:
            valid_moves = []
            for r in range(board.rows):
                for c in range(board.cols):
                    cell = board.grid[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        valid_moves.append((r, c))
            
            if valid_moves:
                move = random.choice(valid_moves)
                self.log(f"AI: Guessing ({move[0]},{move[1]})")
                return (move[0], move[1], 'reveal')
        
        return None
