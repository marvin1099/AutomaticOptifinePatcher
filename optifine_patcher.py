#!/usr/bin/env python3

import urllib.request
import re
import json
import argparse
import subprocess
import time
import signal
import shutil
import tempfile
import platform
import os

# URLs and paths
HTTP = "http://"
HTTPS = "https://"
OPTIFINE_BASE_URL = "optifine.net"
OPTIFINE_DOWNLOAD_URL = HTTPS + OPTIFINE_BASE_URL + "/downloads"

# Regex for jar links (both preview and non-preview)
OPTIFINE_BASE_JAR_REGEX = re.compile(
    rf'href="({re.escape(HTTP + OPTIFINE_BASE_URL)}/adloadx\?f=[^"]+\.jar)"'
)

# Regex to parse the optifine link for version, release and prerelease
OPTIFINE_PARSE_JAR_REGEX = re.compile(
    r"(?:preview_)?OptiFine_(?P<version>[\d\.]+)_HD_U_(?P<release>[A-Z]\d+)(?:_pre(?P<pre>\d+))?\.jar"
)

MINECRAFT_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
USER_AGENS_URL = "https://raw.githubusercontent.com/microlinkhq/top-user-agents/refs/heads/master/src/index.json"
HEADERS = None # this will be populated with the user agent later
CACHE_FILE = os.path.join(tempfile.gettempdir(), "optifine_patcher_cache.json")
CACHE_TTL = 3600  # 1 hour

# Load cache
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            CACHE = json.load(f)
    except Exception:
        CACHE = {"redirects": {}, "pages": {}}
else:
    CACHE = {"redirects": {}, "pages": {}}

def cleanup_cache():
    """Remove expired entries from cache (both redirects and pages)."""
    now = int(time.time())
    for section in ("redirects", "pages"):
        expired_keys = [
            url for url, entry in CACHE.get(section, {}).items()
            if now - entry.get("fetched", 0) >= CACHE_TTL
        ]
        for key in expired_keys:
            del CACHE[section][key]

def save_cache():
    """Save cache to disk after cleanup."""
    cleanup_cache()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(CACHE, f)
    except Exception as e:
        print("Warning: failed to save cache:", e)

def fetch_html(url, ret_json=False):
    """Fetch HTML with caching."""
    now = int(time.time())
    cleanup_cache()

    if url in CACHE["pages"]:
        raw = CACHE["pages"][url].get("data")
        if raw:
            return json.loads(raw) if ret_json else raw

    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        raw = response.read().decode("utf-8")

    CACHE["pages"][url] = {"fetched": now, "data": raw}
    save_cache()
    return json.loads(raw) if ret_json else raw


HEADERS = { 'User-Agent': fetch_html(USER_AGENS_URL, True)[0] }

def follow_redirect(url):
    """Follow redirect and cache final URL."""
    now = int(time.time())
    cleanup_cache()

    if url in CACHE["redirects"]:
        final_url = CACHE["redirects"][url].get("final_url")
        if final_url:
            return final_url

    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        final_url = response.geturl()

    CACHE["redirects"][url] = {"fetched": now, "final_url": final_url}
    save_cache()
    return final_url

def download_file(url, output_path, remove = False):
    if os.path.isfile(output_path) and not remove:
        print("Requested file already exists, skipping...")
        return
    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        # Read the response data
        data = response.read()
        print("Done reading file, saving now...")

        # Write the data to the output file
        with open(output_path, 'wb') as file:
            file.write(data)

def get_optifine_links():
    """Fetch OptiFine download page and extract .jar links"""
    html = fetch_html(OPTIFINE_DOWNLOAD_URL)
    # Regex for both preview and non-preview jars
    pattern = OPTIFINE_BASE_JAR_REGEX
    links = pattern.findall(html)
    # Convert http → https
    links = [link.replace(HTTP, HTTPS, 1) for link in links]
    return links


def clean_version(version_string, as_list=False, allow_none=False, zero_ok=False):
    # Keep only digits and dots
    filtered = re.sub(r"[^0-9.]", "", version_string)

    # Split into parts and remove leading zeros (but keep "0" if alone)
    parts = [str(int(p)) if p.isdigit() else "" for p in filtered.split(".")]

    # Remove empty parts
    parts = [p for p in parts if p]

    if not zero_ok:
        # Trim trailing zeros
        while parts and parts[-1] == "0":
            parts.pop()

    if as_list:
        return parts if parts else [] if allow_none else ["0"]
    else:
        return ".".join(parts) if parts else "" if allow_none else "0"

def parse_optifine_link(link):
    """
    Parse an OptiFine download link into (version, release, previewnr).
    """
    # Extract just the filename part
    match = re.search(r"f=([^&]+\.jar)", link)
    if not match:
        return None
    filename = match.group(1)  # e.g. preview_OptiFine_1.8.9_HD_U_M6_pre2.jar

    # Regex for preview builds
    preview_pattern = OPTIFINE_PARSE_JAR_REGEX

    m = preview_pattern.match(filename)
    if not m:
        return None

    version = clean_version(m.group("version"))
    release = m.group("release")
    previewnr = int(m.group("pre")) if m.group("pre") else 0

    return {
        "version": version,
        "release": release,
        "previewnr": previewnr,
        "url": link
    }

def categorize_optifine_links(links):
    new_links = []
    for link in links:
        parse_dict = parse_optifine_link(link)
        new_links.append(parse_dict)

    return new_links


def extract_download_link(adloadx_url):
    """
    Given an OptiFine 'adloadx' URL, follow redirect and extract the final 'downloadx' link.
    """
    # Step 1: follow redirect to actual page
    final_url = follow_redirect(adloadx_url)

    # Step 2: fetch that page's HTML
    html = fetch_html(final_url)

    # Step 3: extract relative download link
    match = re.search(r"href=['\"](downloadx\?f=[^'\"\s]+)", html)
    if not match:
        return None

    # Step 4: build absolute link
    download_link = HTTPS + OPTIFINE_BASE_URL + "/" + match.group(1)

    final_download_link = follow_redirect(download_link)
    return final_download_link


def validate_release(release_string):
    """
    Accepts a release string like 'M6', 'B3', 'M12', etc.
    Must be at least 2 characters: first character is a letter, the rest are digits.
    Returns the release string if valid, else None.
    """
    if len(release_string) < 2:
        return None
    if not release_string[0].isalpha():
        return None
    if not all(c.isdigit() for c in release_string[1:]):
        return None
    return release_string.upper()

def filter_versions(filter_version, normal_versions_only=False):
    version_and_release = filter_version.split("_")
    version = clean_version(version_and_release[0], allow_none=True, as_list=True, zero_ok=True)
    release = None
    if len(version_and_release) > 1:
        release = validate_release(version_and_release.pop())
    while len(version_and_release) > 1 and not release:
        release = validate_release(version_and_release.pop())

    # Get all categorized links
    links = get_optifine_links()
    links = categorize_optifine_links(links)

    # Filter by version and optionally by release
    filtered = []
    for entry in links:
        if entry is None:
            continue
        if entry.get("version"):
            if version:
                main_version = clean_version(entry.get("version"), as_list=True)
                while len(main_version) < len(version):
                    main_version.append("0")
                if main_version[:len(version)] != version:
                    continue

            if normal_versions_only and entry.get("previewnr") > 0:
                continue

            if release is None or entry.get("release") == release:
                filtered.append(entry)

    return filtered

def list_versions(filter_version):
    filtered = filter_versions(filter_version)

    # Print results
    if not filtered:
        print(f"No OptiFine versions found for: {filter_version}")
    else:
        print("Matching OptiFine versions:")
        for entry in reversed(filtered):
            pre = f"_pre{entry['previewnr']}" if entry['previewnr'] > 0 else ""
            first = f"{entry['version']}_{entry['release']}{pre}"
            print(f"{first}")
            #print(f"{first.ljust(16)} -> {entry['url']}")

def fetch_minecraft_client(version):
    manifest = fetch_html(MINECRAFT_MANIFEST_URL,True)

    # Convert requested version into a list of ints/strings
    requested = clean_version(version, as_list=True)

    version_info = None
    for entry in manifest["versions"]:
        main_version = clean_version(entry.get("id"), as_list=True)
        if not main_version:
            continue

        # Pad shorter version with zeros
        while len(main_version) < len(requested):
            main_version.append("0")
        while len(requested) < len(main_version):
            requested.append("0")

        # Compare
        if main_version == requested:
            version_info = entry
            break

    if not version_info:
        return None

    version_data = fetch_html(version_info["url"], True)
    return version_data["downloads"]["client"]["url"]


def patch_optifine(java, optifine_jar, mc_jar, output_jar):
    patch_command = [
        java, "-cp", optifine_jar, "optifine.Patcher", mc_jar, optifine_jar, output_jar
    ]

    result = subprocess.run(
        patch_command,
        capture_output=True,
        text=True
    )

    return result


def download_version(filter_version, normal_versions_only, java_path, remove, cleanup, move, folder):
    filtered = filter_versions(filter_version, normal_versions_only)
    if not filtered:
        print(f"No OptiFine versions found for: {filter_version}")
        return

    newest = filtered[0]
    url = newest.get('url')
    link = extract_download_link(url)
    if not link:
        print(f"No download found for {filter_version} on download page {url}")
        return

    equals = link.find("=")
    jar = link.find(".jar")
    if equals > -1 and jar > -1 and jar > equals:
        pass
    else:
        print(f"There was a problem with the download link {link} from the optifine webpage, is not a jar file")
        return

    version = newest.get("version")
    release = newest.get("release")
    previewnr = newest.get("previewnr")
    preview = "(regular release)" if previewnr == 0 else f"(preview {previewnr})"
    print(f"Downloading OptiFine {version} with release {release} {preview}...")

    os.makedirs(version,exist_ok=True)

    full_optifine_jar = link[equals+1:jar] + ".jar"
    file_output_jar = link[equals+1:jar] + "-MOD.jar"
    path_optifine_jar = os.path.join(version, full_optifine_jar)
    path_output_jar = os.path.join(version, file_output_jar)

    download_file(link, path_optifine_jar, remove)

    print(f"Fetching Minecraft client jar for {version}...")
    client_url = fetch_minecraft_client(version)

    client_name = f"Minecraft-{version}-client.jar"
    client_path = os.path.join(version, client_name)

    download_file(client_url, client_path, remove)

    print(f"Patching OptiFine into {path_output_jar} in subfolder {version}...")
    result = patch_optifine(java_path, path_optifine_jar, client_path, path_output_jar)

    if cleanup and result.returncode == 0:
        print("Running cleanup...")
    if move and os.path.isfile(path_output_jar):
        print("Moving File...")
        shutil.move(os.path.abspath(path_output_jar), os.path.abspath(file_output_jar))
        print("Removing empty folder")
        try:
            os.rmdir(version)
        except Exception as e:
            if folder:
                print("Folder probably filled, since -f activated removing anyway")
                shutil.rmtree(version)
            else:
                print(f"Cant remove dir files are still in there {e}")

    # Report completion
    status = "success" if result.returncode == 0 else "failure"
    print(f"Done Patching OptiFine with code {result.returncode} ({status}).")

    # --- Prompt with timeout (Unix only) ---
    def timeout_handler(signum, frame):
        raise TimeoutError

    if platform.system() != "Windows":
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # timeout after 10 seconds

    try:
        show = input("Do you want to show the output (10 secs timeout on unix)? (y/N): ").strip().lower()
    except TimeoutError:
        print("\nNo input received, skipping output.")
        show = "n"
    finally:
        if platform.system() != "Windows":
            signal.alarm(0)  # disable alarm

    if show == "y":
        if result.stdout:
            print("=== STDOUT ===")
            print(result.stdout)
            print("=== === ===\n")
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
            print("=== === ===")


def main():
    parser = argparse.ArgumentParser(description="OptiFine Downloader and Patcher")
    parser.add_argument("-l", "--list", nargs='?', const="", default=None, help="List OptiFine versions (if specific Minecraft version is wanted set after -l)")
    parser.add_argument("-d", "--download", nargs='?', const="", default=None, help="Download and patch a OptiFine version (e.g., 1.16.5_HD_U_G8, newest is chosen if not specfied)")
    parser.add_argument("-j", "--java", default="java", help="Provide a custom java path")
    parser.add_argument("-w", "--workdir", help="Provide a custom working directory (the path will be relative to the script if not absolute)")
    parser.add_argument("-n", "--normal", action='store_true', help="Only Download non preview versions of OptiFine (-l not affected)")
    parser.add_argument("-r", "--remove", action='store_true', help="Override files already downloaded, instead of skipping the download")
    parser.add_argument("-c", "--cleanup", action='store_true', help="Delete the optifine and client jar files")
    parser.add_argument("-m", "--move", action='store_true', help="Move the Mod file to woking dir and delete the download folder (if empty)")
    parser.add_argument("-f", "--folder", action='store_true', help="Also remove the filled folder (only active on successfull -m)")
    args = parser.parse_args()

    if args.list != None:
        list_versions(args.list)
    elif args.download != None:
        if args.workdir:
            if os.path.isabs(args.workdir):
                os.chdir(args.workdir)
            else:
                os.chdir(os.join(os.path.dirname(os.path.realpath(__file__)), args.workdir))
        download_version(args.download, args.normal, args.java, args.remove, args.cleanup, args.move, args.folder)
    else:
        parser.print_help()



if __name__ == "__main__":
    main()

    #new = extract_download_link(link)
    #download_file(new,"file.jar")
    #exit()
