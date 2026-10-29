import os
import random
import subprocess
import sys
import urllib.request
import json
from datetime import datetime, timezone, timedelta
from PIL import Image

import gifos

IST = timezone(timedelta(hours=5, minutes=30))

# Set ffmpeg path on Windows if present
win_ffmpeg = r"C:\Users\ansha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if os.path.exists(win_ffmpeg) and win_ffmpeg not in os.environ.get("PATH", ""):
    os.environ["PATH"] = win_ffmpeg + os.pathsep + os.environ.get("PATH", "")

FONT_FILE_LOGO = "./fonts/vtks-blocketo.regular.ttf"
FONT_FILE_BITMAP = "./fonts/gohufont-uni-14.pil"
FONT_FILE_TRUETYPE = "./fonts/IosevkaTermNerdFont-Bold.ttf"
FONT_FILE_MONA = "./fonts/Inversionz.otf"

def safe_gen_gif(terminal, output_file="output.gif"):
    """Cross-platform GIF generator using ffmpeg subprocess."""
    fps = getattr(terminal, "_Terminal__fps", 15)
    frame_folder = "frames"
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-r",
        str(fps),
        "-i",
        os.path.join(frame_folder, "frame_%d.png"),
        "-filter_complex",
        "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse",
        "-loop",
        "-1",
        output_file,
    ]
    subprocess.run(cmd, check=True)
    frame_count = getattr(terminal, "_Terminal__frame_count", 0)
    print(f"INFO: Generated {output_file} ({round(frame_count / fps, 2)}s, {fps} fps)")

def fetch_stats():
    """Fetch GitHub stats with fallback."""
    user = "anshdev44"
    user_rank = "A+"
    total_stars = 2
    total_commits = 210
    total_prs = 12
    total_contribs = 280
    top_langs = ["TypeScript", "JavaScript", "Python", "Java"]

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            stats = gifos.utils.fetch_github_stats(user)
            user_rank = stats.user_rank.level
            total_stars = stats.total_stargazers
            total_commits = stats.total_commits_last_year
            total_prs = stats.total_pull_requests_made
            total_contribs = stats.total_repo_contributions
            top_langs = [lang[0] for lang in stats.languages_sorted][:4]
            return user_rank, total_stars, total_commits, total_prs, total_contribs, top_langs
        except Exception as e:
            print(f"Warning: gifos.utils.fetch_github_stats failed: {e}")

    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{user}/repos?per_page=100",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        repos = json.loads(urllib.request.urlopen(req, timeout=5).read())
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        lang_counts = {}
        for r in repos:
            l = r.get("language")
            if l:
                lang_counts[l] = lang_counts.get(l, 0) + 1
        sorted_l = [k for k, _ in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)]
        if sorted_l:
            top_langs = sorted_l[:4]
    except Exception as e:
        print(f"Warning: public github api fallback: {e}")

    return user_rank, total_stars, total_commits, total_prs, total_contribs, top_langs

def main():
    width = 750
    height = 500
    t = gifos.Terminal(width, height, 15, 15, FONT_FILE_BITMAP, 15)

    t.gen_text("", 1, count=15)
    t.toggle_show_cursor(False)
    time_now_dt = datetime.now(IST)
    year_now = time_now_dt.strftime("%Y")

    # 1. BIOS screen
    t.gen_text("GIF_OS Modular BIOS v1.0.11", 1)
    t.gen_text(f"Copyright (C) {year_now}, \x1b[31mAnsh Ahuja\x1b[0m", 2)
    t.gen_text("\x1b[94mGitHub Profile ReadMe Terminal, Rev 1011\x1b[0m", 4)
    t.gen_text("Krypton(tm) GIFCPU - 250Hz", 6)
    t.gen_text(
        "Press \x1b[94mDEL\x1b[0m to enter SETUP, \x1b[94mESC\x1b[0m to cancel Memory Test",
        t.num_rows,
    )
    for i in range(0, 65653, 7168):
        t.delete_row(7)
        if i < 30000:
            t.gen_text(f"Memory Test: {i}", 7, count=2, contin=True)
        else:
            t.gen_text(f"Memory Test: {i}", 7, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 64KB OK", 7, count=8, contin=True)
    t.gen_text("", 11, count=8, contin=True)

    # 2. Boot Splash
    t.clear_frame()
    t.gen_text("Initiating Boot Sequence ", 1, contin=True)
    t.gen_typing_text(".....", 1, contin=True)
    t.gen_text("\x1b[96m", 1, count=0, contin=True)
    t.set_font(FONT_FILE_LOGO, 66)
    os_logo_text = "GIF OS"
    mid_row = (t.num_rows + 1) // 2
    mid_col = (t.num_cols - len(os_logo_text) + 1) // 2
    effect_lines = gifos.effects.text_scramble_effect_lines(
        os_logo_text, 3, include_special=False
    )
    for i in range(len(effect_lines)):
        t.delete_row(mid_row + 1)
        t.gen_text(effect_lines[i], mid_row + 1, mid_col + 1)

    # 3. Login prompt
    t.set_font(FONT_FILE_BITMAP, 15)
    t.clear_frame()
    t.clone_frame(4)
    t.toggle_show_cursor(False)
    t.gen_text("\x1b[93mGIF OS v1.0.11 (tty1)\x1b[0m", 1, count=4)
    t.gen_text("login: ", 3, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text("anshdev44", 3, contin=True)
    t.gen_text("", 4, count=4)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=4)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 4, contin=True)
    t.toggle_show_cursor(False)

    time_now = time_now_dt.strftime("%a %b %d %I:%M:%S %p %Z %Y")
    t.gen_text(f"Last login: {time_now} on tty1", 6)

    t.gen_prompt(7, count=4)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mclea", 7, contin=True)
    t.delete_row(7, prompt_col)
    t.gen_text("\x1b[92mclear\x1b[0m", 7, count=3, contin=True)

    # 4. Fetch Details Screen
    t.clear_frame()
    t.gen_prompt(1)
    prompt_col = t.curr_col
    t.clone_frame(6)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\x1b[91mfetch.s", 1, contin=True)
    t.delete_row(1, prompt_col)
    t.gen_text("\x1b[92mfetch.sh\x1b[0m", 1, contin=True)
    t.gen_typing_text(" -u anshdev44", 1, contin=True)

    # Mona ASCII Silhouette
    t.set_font(FONT_FILE_MONA, 16, 0)
    t.toggle_show_cursor(False)
    mona_lines = r"""
    \x1b[49m     \x1b[90;100m}}\x1b[49m     \x1b[90;100m}}\x1b[0m
    \x1b[49m    \x1b[90;100m}}}}\x1b[49m   \x1b[90;100m}}}}\x1b[0m
    \x1b[49m    \x1b[90;100m}}}}}\x1b[49m \x1b[90;100m}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}}}}}}}}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}}}}}}}}}}}}}\x1b[0m
    \x1b[49m   \x1b[90;100m}}\x1b[37;47m}}}}}}}\x1b[90;100m}}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}}\x1b[37;47m}}}}}}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}}\x1b[37;47m}\x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}\x1b[37;47m}}\x1b[90;100m}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}\x1b[37;47m}}\x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}\x1b[37;47m}}}\x1b[90;100m}}}\x1b[0m
    \x1b[90;100m}}}\x1b[37;47m}}}}\x1b[90;100m}}}\x1b[37;47m}}}}}\x1b[90;100m}}}}\x1b[0m
    \x1b[49m  \x1b[90;100m}\x1b[37;47m}}}}}\x1b[90;100m}}\x1b[37;47m}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[49m \x1b[90;100m}}\x1b[37;47m}}}}}}}}}}}}\x1b[90;100m}}}\x1b[0m
    \x1b[90;100m}\x1b[49m  \x1b[90;100m}}\x1b[37;47m}}}}}}}}\x1b[90;100m}}}\x1b[49m  \x1b[90;100m}\x1b[0m
    \x1b[49m        \x1b[90;100m}}}}}\x1b[0m
    \x1b[49m       \x1b[90;100m}}}}}}}\x1b[0m
    \x1b[49m       \x1b[90;100m}}}}}}}}\x1b[0m
    \x1b[49m      \x1b[90;100m}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}}}}}}}}}}}\x1b[0m
    \x1b[49m     \x1b[90;100m}}\x1b[49m \x1b[90;100m}}}}}}\x1b[49m \x1b[90;100m}}\x1b[0m
    \x1b[49m        \x1b[90;100m}}}}}}}\x1b[0m
    \x1b[49m         \x1b[90;100m}}}\x1b[49m \x1b[90;100m}}\x1b[0m
    """
    t.gen_text(mona_lines, 9)

    user_rank, total_stars, total_commits, total_prs, total_contribs, top_langs = fetch_stats()
    top_langs_str = ", ".join(top_langs)

    user_details_lines = f"""
    \x1b[30;102manshdev44@GitHub\x1b[0m
    -----------------
    \x1b[96mHost:      \x1b[93mIIIT Vadodara (B.Tech CSE '28)\x1b[0m
    \x1b[96mKernel:    \x1b[93mDSA (800+ Solved), OOP, OS, DBMS\x1b[0m
    \x1b[96mLanguages: \x1b[93mJava, JS/TS, Python, C/C++, SQL\x1b[0m
    \x1b[96mAI / LLM:  \x1b[93mRAG, LangChain, LangGraph, Agents\x1b[0m
    \x1b[96mStack:     \x1b[93mReact, Next.js, Node.js, Socket.IO\x1b[0m
    \x1b[96mDBs/Tools: \x1b[93mMongoDB, MySQL, Vector DBs, Redis\x1b[0m
    \x1b[96mCommunity: \x1b[93mIIIT Vadodara Coding Club\x1b[0m

    \x1b[30;104mContact:\x1b[0m
    --------
    \x1b[96mEmail:     \x1b[93manshahuja770@gmail.com\x1b[0m
    \x1b[96mLinkedIn:  \x1b[93mansh-ahuja-3081662b9\x1b[0m
    \x1b[96mGitHub:    \x1b[93mgithub.com/anshdev44\x1b[0m

    \x1b[30;105mGitHub Stats:\x1b[0m
    -------------
    \x1b[96mUser Rating:         \x1b[93m{user_rank}\x1b[0m
    \x1b[96mTotal Stars Earned:  \x1b[93m{total_stars}\x1b[0m
    \x1b[96mTotal Commits ({int(year_now) - 1}): \x1b[93m{total_commits}\x1b[0m
    \x1b[96mTotal PRs:           \x1b[93m{total_prs}\x1b[0m
    \x1b[96mTotal Contributions: \x1b[93m{total_contribs}\x1b[0m
    \x1b[96mTop Languages:       \x1b[93m{top_langs_str}\x1b[0m
    """

    t.set_font(FONT_FILE_BITMAP)
    t.toggle_show_cursor(True)
    t.gen_text(user_details_lines, 2, 33, count=4, contin=True)
    t.gen_prompt(t.curr_row)
    t.gen_typing_text(
        "\x1b[92m# Have a nice day kind stranger :D Thanks for stopping by!",
        t.curr_row,
        contin=True,
    )
    t.gen_text("", t.curr_row, count=225, contin=True)

    # 5. Generate output GIF
    try:
        safe_gen_gif(t, "output.gif")
    except Exception as e:
        print(f"Warning: safe_gen_gif failed, falling back to t.gen_gif: {e}")
        t.gen_gif()

    # 6. Generate README.md
    readme_content = f"""<div align="center">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="Terminal - anshdev44" src="./output.gif">
</picture>

<br><br>

<details>
### 🌐 Connect With Me
<p align="center">
  <a href="mailto:anshahuja770@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
  &nbsp;
  <a href="https://linkedin.com/in/ansh-ahuja-3081662b9"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  &nbsp;
  <a href="https://github.com/anshdev44"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
</p>

</details>

</div>
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("INFO: README.md generated successfully!")

if __name__ == "__main__":
    main()
