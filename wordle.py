#!/usr/bin/env python3
"""
Fancy Wordle (pygame edition) – with auto-wordlist, flip animations,
and a “play again?” prompt when the round ends.
"""

# ─────────────────────────────  STANDARD LIB  ────────────────────────────
import random, sys, urllib.request, urllib.error, math
from pathlib import Path

# ──────────────────────────────  3RD-PARTY  ──────────────────────────────
import pygame as pg      # pip install pygame

# ─────────────────────────────  WORD LIST  ───────────────────────────────
WORD_LEN       = 5
WORDLIST_FILE  = "wordlist.txt"
WORDLIST_URL   = (
    "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"
)  # 2 315-word original answer set

FALLBACK_WORDS = """
cigar blush focal evade naval serve heath dwarf model karma
stink grade quiet bench feign major death fresh crust stool
colon marry react batty pride floss helix croak staff paper
unfed whelp trawl adobe crazy sower repay digit crate cluck
spike mimic pound maxim linen unmet flesh booby forth first
stand belly ivory seedy print yearn drain bribe stout panel
crass flume offal agree error swirl argue bleed delta flick
totem wooer front shrub parry biome lapel start greet goner
golem lusty loopy round audit lying gamma labor islet civic
forge corny moult basic salad agate spicy spray essay fjord
spend kebab guild aback motor alone hatch hyper thumb dowry
vivid spill chant choke broom brine altar rogue lobby plush
""".split()

def ensure_wordlist(path: str = WORDLIST_FILE) -> list[str]:
    """Return a clean 5-letter list – try local → online → fallback."""
    p = Path(path)
    if p.exists():
        words = [w.strip().lower() for w in p.read_text().splitlines()]
        words = [w for w in words if len(w) == WORD_LEN and w.isalpha()]
        if words:  # good file
            return words

    try:                                           # try online
        print("Fetching full word list …")
        with urllib.request.urlopen(WORDLIST_URL, timeout=8) as resp:
            raw = resp.read().decode().splitlines()
        words = [w.strip().lower() for w in raw if len(w) == WORD_LEN and w.isalpha()]
        Path(path).write_text("\n".join(words))
        print(f"✓ saved {len(words)} words to {path}")
    except Exception:
        print("couldn’t download – using fallback list")
        words = FALLBACK_WORDS
        try: Path(path).write_text("\n".join(words))
        except Exception: pass                     # sandbox read-only? ignore
    return sorted(set(words))

WORDS       = ensure_wordlist()
TARGET_WORD = random.choice(WORDS)
LEGAL_SET   = set(WORDS)

# ─────────────────────────────  APPEARANCE  ──────────────────────────────
MAX_TRIES    = 6
TILE         = 80
GAP          = 8
TOP          = 140
WIDTH        = TILE*WORD_LEN + GAP*(WORD_LEN-1) + 2*GAP
HEIGHT       = TOP + MAX_TRIES*TILE + (MAX_TRIES-1)*GAP + 2*GAP
FPS          = 60
FLIP_MS      = 280              # one tile flip duration
STAGGER_MS   = 120              # delay between flips

BG      = (19, 21, 24)
EMPTY   = (58, 58, 60)
LETTER  = (230, 233, 236)
GREEN   = (83, 141, 78)
YELLOW  = (181, 159, 59)
GRAY    = (58, 58, 60)
SHADOW  = (0, 0, 0, 90)

def colour(c): return {"green": GREEN, "yellow": YELLOW, "gray": GRAY}[c]

# ───────────────────────────  FLIP ANIMATION  ────────────────────────────
class TileReveal:
    """Manage a single letter flip (0→1 progress)"""
    def __init__(self, row, col, new_color, start_ms):
        self.row, self.col = row, col
        self.color   = new_color
        self.start   = start_ms

    def progress(self, now):
        return max(0.0, min(1.0, (now - self.start) / FLIP_MS))

# ─────────────────────────────-  GAME CLASS  ─────────────────────────────
class Wordle:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Fancy Wordle")
        self.clock  = pg.time.Clock()
        self.big    = pg.font.SysFont("arialblack", 54)
        self.med    = pg.font.SysFont("arialblack", 34)
        self.small  = pg.font.SysFont("arial", 26)

        self.new_round()

    # -------------------------  ROUND SETUP  -----------------------------
    def new_round(self):
        global TARGET_WORD
        TARGET_WORD = random.choice(WORDS)
        print("debug target ➜", TARGET_WORD)        # comment to hide
        self.guesses: list[str]    = []
        self.results: list[list]   = []             # 'green' / 'yellow' / 'gray'
        self.current               = ""
        self.reveals: list[TileReveal] = []
        self.message               = ""
        self.play_again_prompt     = False
        self.game_over             = False

    # --------------------------  INPUT  ----------------------------------
    def handle_key(self, key, uni):
        if self.game_over:
            if key in (pg.K_y, pg.K_RETURN):
                self.new_round()
            elif key in (pg.K_n, pg.K_ESCAPE):
                self.quit()
            return

        if key == pg.K_RETURN:
            self.submit_guess()
        elif key == pg.K_BACKSPACE:
            self.current = self.current[:-1]
        elif pg.K_a <= key <= pg.K_z and len(self.current) < WORD_LEN:
            self.current += uni.lower()

    # ------------------  GUESS VALIDATION & REVEAL SETUP  ----------------
    def submit_guess(self):
        guess = self.current.lower()
        if len(guess) != WORD_LEN:
            self.flash("Not enough letters!")
            return
        if guess not in LEGAL_SET:
            self.flash("Not in word list!")
            return

        styles = self.score(guess, TARGET_WORD)
        row    = len(self.guesses)
        stamp  = pg.time.get_ticks()

        # enqueue flip animations for each tile
        for i, s in enumerate(styles):
            self.reveals.append(TileReveal(row, i, colour(s), stamp + i*STAGGER_MS))

        self.guesses.append(guess)
        self.results.append(styles)
        self.current = ""

        if guess == TARGET_WORD:
            self.end_round("Correct!")
        elif len(self.guesses) == MAX_TRIES:
            self.end_round(f" {TARGET_WORD.upper()}")

    # -------------------------  END-ROUND  ------------------------------
    def end_round(self, msg):
        self.play_again_prompt = True
        self.game_over         = True
        self.flash(msg, keep=True)

    # --------------------------  HELPERS  -------------------------------
    def flash(self, txt, ms=1600, keep=False):
        self.message = txt
        if not keep:
            pg.time.set_timer(pg.USEREVENT, ms, True)

    @staticmethod
    def score(guess, target):
        res = ["gray"]*WORD_LEN
        pool = list(target)
        for i,g in enumerate(guess):
            if g == target[i]:
                res[i] = "green"; pool[i] = None
        for i,g in enumerate(guess):
            if res[i]=="gray" and g in pool:
                res[i] = "yellow"; pool[pool.index(g)] = None
        return res

    # ------------------------  DRAWING  ---------------------------------
    def draw(self):
        self.screen.fill(BG)
        self.draw_banner()
        self.draw_tiles()
        if self.play_again_prompt:
            self.draw_prompt()
        pg.display.flip()

    def draw_banner(self):
        # subtle vertical gradient
        banner = pg.Surface((WIDTH, TOP))
        for y in range(TOP):
            c = int(19 + (24-19)*y/TOP)
            banner.fill((c, c+2, c+5), rect=pg.Rect(0, y, WIDTH, 1))
        self.screen.blit(banner, (0,0))
        title = self.big.render("WORDLE", True, (241,241,242))
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, TOP//2)))

        if self.message and not self.play_again_prompt:
            txt = self.small.render(self.message, True, LETTER)
            self.screen.blit(txt, txt.get_rect(midtop=(WIDTH//2, TOP-34)))

    def draw_tiles(self):
        now = pg.time.get_ticks()

        def rect_at(r,c):
            x = GAP + c*(TILE+GAP)
            y = TOP + GAP + r*(TILE+GAP)
            return pg.Rect(x, y, TILE, TILE)

        # shadow pass
        shadow_surf = pg.Surface((TILE, TILE), pg.SRCALPHA)
        shadow_surf.fill(SHADOW)

        for r in range(MAX_TRIES):
            for c in range(WORD_LEN):
                rect = rect_at(r,c)

                base_col = EMPTY
                letter   = ""
                colorize = False

                if r < len(self.guesses):
                    letter = self.guesses[r][c].upper()
                    # if reveal done, paint final colour
                    if self.reveal_progress(r,c,now) >= 1:
                        base_col = colour(self.results[r][c])
                    colorize = True
                elif r == len(self.guesses) and c < len(self.current):
                    letter = self.current[c].upper()

                # shadow
                shadow_pos = rect.move(3,4)
                self.screen.blit(shadow_surf, shadow_pos)

                # flip animation: scale Y 1→0→1
                prog = self.reveal_progress(r,c,now)
                if 0 < prog < 1:
                    scale = abs(1 - 2*prog)        # down to 0 then up
                    surf  = pg.Surface((TILE, max(1,int(TILE*scale))))
                    surf.fill(base_col if prog>0.5 else EMPTY)
                    center = rect.center
                    top = center[1] - surf.get_height()//2
                    self.screen.blit(surf, (rect.left, top))
                else:
                    pg.draw.rect(self.screen, base_col, rect, border_radius=8)

                # border highlight for current row
                if r == len(self.guesses) and not self.game_over:
                    pg.draw.rect(self.screen, (86,87,89), rect, width=3, border_radius=8)

                # letter
                if letter and prog<0.5:  # hide letter while face is "back"
                    continue
                if letter:
                    txt = self.med.render(letter, True, (255,255,255))
                    self.screen.blit(txt, txt.get_rect(center=rect.center))

    def reveal_progress(self, row, col, now):
        """0→1 progress for given tile if animating, else 1 instantly."""
        for rev in self.reveals:
            if (rev.row,rev.col)==(row,col):
                return rev.progress(now)
        return 1.0

    def draw_prompt(self):
        pad = 30
        box = pg.Rect(pad, pad, WIDTH-2*pad, HEIGHT-2*pad)
        pg.draw.rect(self.screen, (20,20,22,230), box, border_radius=12)
        pg.draw.rect(self.screen, (100,100,105), box, width=4, border_radius=12)

        txt1 = self.med.render(self.message, True, (255,255,255))
        txt2 = self.small.render("Play again?  Y / N", True, LETTER)
        self.screen.blit(txt1, txt1.get_rect(center=(WIDTH//2, HEIGHT//2-20)))
        self.screen.blit(txt2, txt2.get_rect(center=(WIDTH//2, HEIGHT//2+25)))

    # -------------------------  MAIN LOOP  -------------------------------
    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                elif event.type == pg.USEREVENT:          # clear flash
                    self.message = ""
                elif event.type == pg.KEYDOWN:
                    self.handle_key(event.key, event.unicode)

            self.draw()
            self.clock.tick(FPS)

    @staticmethod
    def quit():
        pg.quit(); sys.exit()


# ─────────────────────────────  START  ───────────────────────────────────
if __name__ == "__main__":
    Wordle().run()
