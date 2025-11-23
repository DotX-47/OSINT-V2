import os
import sys
import time
import socket
import asyncio
import httpx
import subprocess
import signal

from bs4 import BeautifulSoup
from tabulate import tabulate
from tqdm import tqdm
import pyfiglet
from colorama import Fore, init

init(autoreset=True)

COLORS = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
GREEN = Fore.GREEN
RED = Fore.RED
RESET = Fore.RESET


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def rainbow_line(line, shift):
    return "".join(COLORS[(i + shift) % len(COLORS)] + ch for i, ch in enumerate(line)) + RESET


def banner():
    text = "OSINT Toolkit"
    art = pyfiglet.figlet_format(text)
    lines = art.splitlines()

    for i in range(20):
        clear()
        for line in lines:
            print(rainbow_line(line, i))
        print("\n" + rainbow_line("Made by DotX-47", i))
        time.sleep(0.04)

    clear()
    for line in lines:
        print(rainbow_line(line, 10))
    print("\n" + rainbow_line("Made by DotX-47", 10) + "\n")


banner()

HEADERS = {"User-Agent": "Mozilla/5.0"}
client = httpx.AsyncClient(timeout=8, headers=HEADERS, follow_redirects=True)

def signal_handler(sig, frame):
    print(f"\n{RED}[!] Exiting safely...{RESET}")
    asyncio.get_event_loop().run_until_complete(client.aclose())
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

#  Google Dork Search

async def google_dork(query):
    print(f"\n[+] Searching Google for: {query}\n")
    url = f"https://www.google.com/search?q={query}"

    try:
        r = await client.get(url)
    except:
        print(f"{RED}[!] Google blocked request or network problem.{RESET}")
        return

    soup = BeautifulSoup(r.text, "html.parser")
    links = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if href and "url?q=" in href:
            links.append(href)

    if links:
        print(tabulate([[l] for l in links], ["Results"], tablefmt="grid"))
    else:
        print(f"{RED}[!] No results found.{RESET}")


#  PLATFORMS

PLATFORM_CATEGORIES = {
    "Social Media": {
        "YouTube": {"url": "https://www.youtube.com/@{}", "exists": ["channel", "watch?v="], "not_exists": ["This channel does not exist"]},
        "TikTok": {"url": "https://www.tiktok.com/@{}", "exists": ["video-feed", "profile"], "not_exists": ["Page not found"]},
        "Instagram": {"url": "https://www.instagram.com/{}/", "exists": ["posts", "followers"], "not_exists": ["Sorry, this page isn't available."]},
        "Facebook": {"url": "https://www.facebook.com/{}/", "exists": ["timeline", "profile"], "not_exists": ["Sorry, this content isn't available right now"]},
        "X": {"url": "https://x.com/{}", "exists": ["tweets", "following"], "not_exists": ["Sorry, that page doesn’t exist"]},
        "Reddit": {"url": "https://www.reddit.com/user/{}", "exists": ["karma", "posts"], "not_exists": ["Sorry, nobody on Reddit goes by that name"]},
        "Tumblr": {"url": "https://www.tumblr.com/{}", "exists": ["posts", "followers"], "not_exists": ["Not Found"]},
        "Pinterest": {"url": "https://www.pinterest.com/{}/", "exists": ["boards", "followers"], "not_exists": ["Page not found"]},
        "Twitch": {"url": "https://www.twitch.tv/{}", "exists": ["followers", "views"], "not_exists": ["Sorry. Unless you’ve got a time machine"]},
        "Quora": {"url": "https://www.quora.com/profile/{}", "exists": ["answers", "followers"], "not_exists": ["No user found"]},
        "LinkedIn": {"url": "https://www.linkedin.com/in/{}", "exists": ["profile", "connections"], "not_exists": ["This page isn’t available"]},
        "VK": {"url": "https://vk.com/{}", "exists": ["friends", "posts"], "not_exists": ["This page does not exist"]},
        "OK.ru": {"url": "https://ok.ru/{}", "exists": ["friends", "posts"], "not_exists": ["Page not found"]},
        "Telegram": {"url": "https://t.me/{}", "exists": ["members"], "not_exists": ["Invalid username"]},
        "Matrix": {"url": "https://matrix.to/#/@{}:matrix.org", "exists": ["messages", "rooms"], "not_exists": ["User not found"]},
        "Snapchat": {"url": "https://www.snapchat.com/add/{}", "exists": ["Add Friend"], "not_exists": ["Sorry, this username doesn't exist"]},

        "Flickr": {"url": "https://www.flickr.com/people/{}", "exists": ["Photostream"], "not_exists": ["Page Not Found"]},
        "Mastodon": {"url": "https://mastodon.social/@{}", "exists": ["@{}"], "not_exists": ["Page not found"]},
        "Mix": {"url": "https://mix.com/{}", "exists": ["content"], "not_exists": ["Sorry, this page doesn’t exist"]},
        "Clubhouse": {"url": "https://www.joinclubhouse.com/@{}", "exists": ["Follow"], "not_exists": ["Profile Not Found"]},
        "Meetup": {"url": "https://www.meetup.com/members/{}", "exists": ["Groups"], "not_exists": ["Member not found"]},
        "Diaspora": {"url": "https://diaspora.example.com/u/{}", "exists": ["posts"], "not_exists": ["User not found"]},
        "Minds": {"url": "https://www.minds.com/{}", "exists": ["posts"], "not_exists": ["No user found"]},
        "Gab": {"url": "https://gab.com/{}", "exists": ["posts"], "not_exists": ["No account found"]},
        "Ello": {"url": "https://ello.co/{}", "exists": ["posts"], "not_exists": ["User not found"]},
        "Rumble": {"url": "https://rumble.com/{}", "exists": ["videos"], "not_exists": ["Channel not found"]},
        "Discord": {"url": "https://discord.com/users/{}", "exists": ["username"], "not_exists": ["User not found"]},
        "Badoo": {"url": "https://badoo.com/en/{}", "exists": ["profile"], "not_exists": ["not found"]},
        "Myspace": {"url": "https://myspace.com/{}", "exists": ["posts"], "not_exists": ["Profile not found"]},
        "Signal": {"url": "https://signal.org/{}", "exists": ["profile"], "not_exists": ["not found"]},
        "Vero": {"url": "https://vero.co/{}", "exists": ["posts"], "not_exists": ["not found"]},
    },

    "Developer": {
        "GitHub": {"url": "https://github.com/{}", "exists": ["repositories", "followers"], "not_exists": ["Not Found"]},
        "GitLab": {"url": "https://gitlab.com/{}", "exists": ["projects", "followers"], "not_exists": ["404"]},
        "Bitbucket": {"url": "https://bitbucket.org/{}/", "exists": ["repositories", "followers"], "not_exists": ["This account does not exist"]},
        "Gitea": {"url": "https://gitea.com/{}", "exists": ["repositories", "followers"], "not_exists": ["User not found"]},
        "SourceForge": {"url": "https://sourceforge.net/u/{}/profile/", "exists": ["projects"], "not_exists": ["Page not found"]},
        "StackOverflow": {"url": "https://stackoverflow.com/users/{}", "exists": ["answers", "reputation"], "not_exists": ["User not found"]},
        "DockerHub": {"url": "https://hub.docker.com/u/{}", "exists": ["repositories", "followers"], "not_exists": ["No user found"]},
        "PyPI": {"url": "https://pypi.org/user/{}/", "exists": ["projects", "followers"], "not_exists": ["Not Found"]},
        "Kaggle": {"url": "https://www.kaggle.com/{}", "exists": ["competitions", "datasets"], "not_exists": ["User not found"]},
        "CodePen": {"url": "https://codepen.io/{}", "exists": ["pens", "projects"], "not_exists": ["Profile Not Found"]},
        "JSFiddle": {"url": "https://jsfiddle.net/user/{}", "exists": ["fiddles"], "not_exists": ["Not Found"]},
        "Replit": {"url": "https://replit.com/@{}", "exists": ["projects"], "not_exists": ["User not found"]},
        "Glitch": {"url": "https://glitch.com/@{}", "exists": ["projects"], "not_exists": ["Page Not Found"]},
        "HackerRank": {"url": "https://www.hackerrank.com/{}", "exists": ["Badges", "Skills"], "not_exists": ["Profile Not Found"]},
        "LeetCode": {"url": "https://leetcode.com/{}", "exists": ["Submissions", "Problems solved"], "not_exists": ["User Not Found"]},
        "Dev.to": {"url": "https://dev.to/{}", "exists": ["articles", "followers"], "not_exists": ["Page Not Found"]},
        "Hashnode": {"url": "https://hashnode.com/@{}", "exists": ["posts", "followers"], "not_exists": ["Not Found"]},
        "CodinGame": {"url": "https://www.codingame.com/profile/{}", "exists": ["games", "skilled"], "not_exists": ["User not found"]},
        "Exercism": {"url": "https://exercism.org/profiles/{}", "exists": ["exercises"], "not_exists": ["Not Found"]},
        "Codewars": {"url": "https://www.codewars.com/users/{}", "exists": ["kata", "honor"], "not_exists": ["Not Found"]},
        "CodeChef": {"url": "https://www.codechef.com/users/{}", "exists": ["rating", "problems"], "not_exists": ["User not found"]},
        "Sphere Engine": {"url": "https://sphere-engine.com/user/{}", "exists": ["solutions"], "not_exists": ["Not Found"]},
    },

    "Gaming": {
        "Steam": {"url": "https://steamcommunity.com/id/{}", "exists": ["games", "friends"], "not_exists": ["This profile could not be found"]},
        "Speedrun": {"url": "https://www.speedrun.com/user/{}", "exists": ["runs", "profile"], "not_exists": ["User not found"]},
        "OSU": {"url": "https://osu.ppy.sh/users/{}", "exists": ["scores", "playcount"], "not_exists": ["not found"]},
        "FortniteTracker": {"url": "https://fortnitetracker.com/profile/all/{}", "exists": ["stats", "matches"], "not_exists": ["Player Not Found"]},
        "FFXIV": {"url": "https://na.finalfantasyxiv.com/lodestone/character/?q={}", "exists": ["Character", "Profile"], "not_exists": ["No character found"]},
        "Chess.com": {"url": "https://www.chess.com/member/{}", "exists": ["games", "followers"], "not_exists": ["Member not found"]},
        "ChessGames": {"url": "https://www.chessgames.com/perl/chessplayer?username={}", "exists": ["games", "profile"], "not_exists": ["Player not found"]},
        "Roblox": {"url": "https://roblox.com/user.aspx?username={}", "exists": ["profile", "friends"], "not_exists": ["User not found"]},
        "Scratch": {"url": "https://scratch.mit.edu/users/{}/", "exists": ["projects", "followers"], "not_exists": ["User not found"]},
        "EpicGames": {"url": "https://www.epicgames.com/id/{}", "exists": ["profile"], "not_exists": ["User not found"]},
        "Xbox": {"url": "https://account.xbox.com/en-us/Profile?gamerTag={}", "exists": ["Gamertag"], "not_exists": ["not found"]},
        "PlayStation": {"url": "https://my.playstation.com/{}", "exists": ["Trophies"], "not_exists": ["Profile Not Found"]},
        "GOG": {"url": "https://www.gog.com/u/{}", "exists": ["games", "reviews"], "not_exists": ["User not found"]},
        "Itch.io": {"url": "https://{}.itch.io/", "exists": ["games", "followers"], "not_exists": ["Page Not Found"]},
        "HumbleBundle": {"url": "https://www.humblebundle.com/user/{}", "exists": ["library", "purchases"], "not_exists": ["Not Found"]},
        "GameJolt": {"url": "https://gamejolt.com/@{}", "exists": ["games", "followers"], "not_exists": ["User not found"]},
        "Kongregate": {"url": "https://www.kongregate.com/accounts/{}", "exists": ["games", "badges"], "not_exists": ["User not found"]},
        "EpicRPG": {"url": "https://epicrpg.com/user/{}", "exists": ["level", "quests"], "not_exists": ["Not Found"]},
        "Miniclip": {"url": "https://www.miniclip.com/users/{}/", "exists": ["games", "scores"], "not_exists": ["User not found"]},
    },

    "Music / Creators": {
        "SoundCloud": {"url": "https://soundcloud.com/{}", "exists": ["tracks", "followers"], "not_exists": ["SoundCloud | Explore music"]},
        "Bandcamp": {"url": "https://www.bandcamp.com/{}", "exists": ["discography", "albums"], "not_exists": ["Page not found"]},
        "About.me": {"url": "https://about.me/{}", "exists": ["bio", "profile"], "not_exists": ["Page Not Found"]},
        "Linktree": {"url": "https://linktr.ee/{}", "exists": ["links", "profile"], "not_exists": ["Sorry, we couldn't find this page"]},
        "VSCO": {"url": "https://vsco.co/{}/gallery", "exists": ["gallery", "photos"], "not_exists": ["Profile not found"]},
        "Patreon": {"url": "https://www.patreon.com/{}", "exists": ["pledges", "posts"], "not_exists": ["This creator has no page"]},
        "SubscribeStar": {"url": "https://www.subscribestar.com/{}", "exists": ["posts", "supporters"], "not_exists": ["This page does not exist"]},
        "Last.fm": {"url": "https://www.last.fm/user/{}", "exists": ["scrobbles", "friends"], "not_exists": ["User not found"]},
        "MyAnimeList": {"url": "https://myanimelist.net/profile/{}", "exists": ["anime_list", "manga_list"], "not_exists": ["User not found"]},
        "Trakt.tv": {"url": "https://trakt.tv/users/{}", "exists": ["watched", "ratings"], "not_exists": ["User not found"]},
        "Mixcloud": {"url": "https://www.mixcloud.com/{}", "exists": ["cloudcasts", "followers"], "not_exists": ["Page not found"]},
        "Audiomack": {"url": "https://audiomack.com/{}", "exists": ["songs", "followers"], "not_exists": ["User not found"]},
        "ReverbNation": {"url": "https://www.reverbnation.com/{}", "exists": ["songs", "fans"], "not_exists": ["User not found"]},
        "Jamendo": {"url": "https://www.jamendo.com/artist/{}", "exists": ["tracks", "albums"], "not_exists": ["Artist not found"]},
        "Vimeo": {"url": "https://vimeo.com/{}", "exists": ["videos", "followers"], "not_exists": ["Page not found"]},
        "Ko-fi": {"url": "https://ko-fi.com/{}", "exists": ["supporters", "posts"], "not_exists": ["Page not found"]},
    },

    "Forums / Misc": {
        "DeviantArt": {"url": "https://www.deviantart.com/{}", "exists": ["gallery", "followers"], "not_exists": ["Page Not Found"]},
        "Dribbble": {"url": "https://dribbble.com/{}", "exists": ["shots", "followers"], "not_exists": ["Not Found"]},
        "Behance": {"url": "https://www.behance.net/{}", "exists": ["projects", "followers"], "not_exists": ["Page Not Found"]},
        "Pastebin": {"url": "https://pastebin.com/u/{}", "exists": ["paste", "created"], "not_exists": ["This user does not exist"]},
        "Gist": {"url": "https://gist.github.com/{}", "exists": ["gists", "followers"], "not_exists": ["Not Found"]},
        "Rentry": {"url": "https://rentry.co/{}", "exists": ["content"], "not_exists": ["Not Found"]},
        "Product Hunt": {"url": "https://www.producthunt.com/@{}", "exists": ["posts", "followers"], "not_exists": ["User not found"]},
        "Goodreads": {"url": "https://www.goodreads.com/{}", "exists": ["books", "reviews"], "not_exists": ["User not found"]},
        "Letterboxd": {"url": "https://letterboxd.com/{}/", "exists": ["films", "reviews"], "not_exists": ["Page Not Found"]},
        "Geocaching": {"url": "https://www.geocaching.com/p/default.aspx?u={}", "exists": ["caches", "found"], "not_exists": ["Profile not found"]},
        "Medium": {"url": "https://medium.com/@{}", "exists": ["articles", "followers"], "not_exists": ["Page Not Found"]},
        "StackExchange": {"url": "https://stackexchange.com/users/{}", "exists": ["reputation", "answers"], "not_exists": ["User not found"]},
        "Disqus": {"url": "https://disqus.com/{}.disqus.com", "exists": ["posts", "comments"], "not_exists": ["User not found"]},
        "Instructables": {"url": "https://www.instructables.com/member/{}", "exists": ["projects"], "not_exists": ["User not found"]},
        "BlogSpot": {"url": "https://{}.blogspot.com", "exists": ["blog"], "not_exists": ["Not Found"]},
        "WordPress": {"url": "https://{}.wordpress.com", "exists": ["posts"], "not_exists": ["No posts found"]},
        "Imgur": {"url": "https://imgur.com/user/{}", "exists": ["images"], "not_exists": ["User not found"]},
        "Hackaday": {"url": "https://hackaday.io/{}", "exists": ["projects"], "not_exists": ["User not found"]},
    }
    }

async def check_username(platform_info, username):
    url = platform_info["url"].format(username)
    try:
        resp = await client.get(url)
        text = resp.text.lower()
        if any(keyword.lower() in text for keyword in platform_info.get("exists", [])):
            return url
        if any(keyword.lower() in text for keyword in platform_info.get("not_exists", [])):
            return None
        if resp.status_code == 200:
            return url
    except:
        return None
    return None


#  Username Lookup

async def username_lookup():
    target = input("\nEnter username: ")

    print("\nSearch Options:")
    print("1. Search by category")
    print("2. Search all platforms")
    choice = input("\nSelect (1/2): ")

    selected_platforms = []

    if choice == "1":
        print("\nAvailable Categories:")
        for i, cat in enumerate(PLATFORM_CATEGORIES.keys(), 1):
            print(f"{i}. {cat}")
        idx = int(input("\nSelect category number: ")) - 1
        category_name = list(PLATFORM_CATEGORIES.keys())[idx]
        selected_platforms = list(PLATFORM_CATEGORIES[category_name].values())
    else:
        for cat in PLATFORM_CATEGORIES.values():
            selected_platforms.extend(cat.values())

    print(f"\n[+] Scanning platforms for '{target}'...\n")
    tasks = [check_username(platform_info, target) for platform_info in selected_platforms]

    results = []
    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), colour="green"):
        res = await f
        if res:
            results.append(res)

    if results:
        print("\nFound Accounts:")
        print(tabulate([[r] for r in results], ["URL"], tablefmt="grid"))
    else:
        print(f"{RED}[!] Username not found on selected platforms.{RESET}")


#  Port Scanner

def port_open(host, port):
    try:
        s = socket.socket()
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0
    except:
        return False


def port_scanner():
    host = input("\nEnter domain/IP: ")
    print(f"\n[+] Scanning ports on {host}\n")

    open_ports = []

    for port in tqdm(range(1, 1025), desc="Scanning", colour="cyan"):
        if port_open(host, port):
            open_ports.append([port])

    print(tabulate(open_ports, ["Open Ports"], tablefmt="grid"))


#  Ping Host

def ping_host():
    host = input("\nEnter host to ping: ")
    cmd = ["ping", "-n", "4", host] if os.name == "nt" else ["ping", "-c", "4", host]
    subprocess.call(cmd)


#  DNS Lookup

def dns_lookup():
    host = input("\nDomain: ")
    try:
        ip = socket.gethostbyname(host)
        print(f"\nIP: {ip}\n")
    except:
        print(f"{RED}[!] Could not resolve domain.{RESET}")


#  URL Analyzer

async def url_analyzer():
    url = input("\nEnter URL: ")
    try:
        r = await client.get(url)
    except:
        print(f"{RED}[!] Error loading URL.{RESET}")
        return

    headers = [[k, v] for k, v in r.headers.items()]
    print("\nHeaders:")
    print(tabulate(headers, ["Header", "Value"], tablefmt="grid"))
    print(f"\nStatus Code: {r.status_code}")


#  Main Menu

async def main():
    while True:
        print("\n[ MENU ]")
        print("1. Google Dork Search")
        print("2. Username Lookup")
        print("3. Port Scanner")
        print("4. Ping Host")
        print("5. DNS Lookup")
        print("6. URL Analyzer")
        print("7. Exit")

        choice = input("\nSelect (1-7): ")

        if choice == "1":
            await google_dork(input("\nEnter dork query: "))
        elif choice == "2":
            await username_lookup()
        elif choice == "3":
            port_scanner()
        elif choice == "4":
            ping_host()
        elif choice == "5":
            dns_lookup()
        elif choice == "6":
            await url_analyzer()
        elif choice == "7":
            print("\nGoodbye.")
            await client.aclose()
            break
        else:
            print(f"{RED}[!] Invalid option.{RESET}")


if __name__ == "__main__":
    asyncio.run(main())
