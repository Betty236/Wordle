# Wordle – Pygame Edition

A desktop recreation of **Wordle** written in pure Python with **pygame**.

* Auto‑downloads the original 2,315‑word answer list on first launch (or falls back to an embedded mini‑dictionary if you’re offline).
* Smooth flip‑tile animations, modern rounded‑card UI & subtle shadows.
* End‑of‑game prompt lets you play again or exit without restarting the program.

---

## Preview

```
┌──────────────────────────────────────────────┐
│  WORDLE                                      │
│                                              │
│  □ □ □ □ □                                   │
│  ▧ ▧ ▧ ▧ ▧   ← live flip animation           │
│  ■ ■ ■ ■ ■                                   │
│                                              │
└──────────────────────────────────────────────┘
```

*(green = correct spot, yellow = wrong spot, gray = absent)*

---

## Features

| Feature                 | Details                                                                    |
|-------------------------|----------------------------------------------------------------------------|
| **Auto word list**      | Downloads & caches the full official list to `wordlist.txt`                |
| **Flip animation**      | Each tile flips with a staggered reveal just like the original             |
| **Polished graphics**   | Gradient banner, drop shadows, rounded tiles, current‑row highlight        |
| **Replay loop**         | After a win/loss press **Y** to start a fresh word or **N / Esc** to quit   |
| **Offline‑safe**        | Bundled 450‑word fallback means it always runs                             |

---

## Requirements

| Software | Version |
|----------|---------|
| Python   | 3.9 +   |
| pygame   | ≥ 2.0 &nbsp;`pip install pygame` |

---

## Installation

```bash
git clone https://github.com/your‑alias/fancy‑wordle.git
cd wordle
pip install pygame          # if you don’t already have it
```

(or simply drop `wordle.py` anywhere, then run `pip install pygame` in the same environment)

---

## Running

```bash
python wordle.py
```

The first launch fetches the word list; subsequent runs start instantly.

---

## Controls

| Key / Action    | Effect                                  |
|-----------------|-----------------------------------------|
| **A–Z**         | Type letters into current row           |
| **Backspace**   | Delete last letter                      |
| **Enter**       | Submit guess                            |
| **Y** (endgame) | Play another round                      |
| **N / Esc**     | Exit game                               |

---

## File structure

```
wordle.py         # main game script
wordlist.txt      # full word list (auto‑created on first run)
README.md         # this file
```

---

## Customising

* **Colours / sizes** – edit the constant blocks at the top of `wordle.py`.
* **Debug word** – comment out the `print("debug target …")` line if you don’t want answers revealed in the console.
* **Word length / tries** – change `WORD_LEN` & `MAX_TRIES` (provide a matching word list!).

