#!/usr/bin/env python3

import urllib.request
import re
import json
import argparse
import subprocess
import time
import shutil
import os

# URLs and paths
OPTIFINE_BASE_URL = "https://optifine.net/downloads"
MINECRAFT_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
USER_AGENS_URL = "https://raw.githubusercontent.com/microlinkhq/top-user-agents/refs/heads/master/src/index.json"
HEADERS = None # this will be populated with the user agent later

def fetch_html(url,ret_json=False):
    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    if ret_json:
        return json.loads(html)
    else:
        return html

HEADERS = { 'User-Agent':fetch_html(USER_AGENS_URL,True)[0] }

def follow_redirect(url):
    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        # Get the final URL after redirections
        final_url = response.geturl()

    return final_url

def patern_search(pattern, data):
    versions = re.findall(pattern, data)
    versions.sort(reverse=True)
    versions = [v[6:-1].replace("http://","https://") for v in versions]
    return versions


def fetch_optifine_versions(mc_version, html=None, nr=0):
    if not html:
        html = fetch_html(OPTIFINE_BASE_URL)
    Svers = patern_search(rf'href="http://optifine\.net/adloadx\?f=OptiFine_{re.escape(mc_version + ".0")}(?!\d)[^"]*jar"', html)
    Sprev_vers = patern_search(rf'href="http://optifine\.net/adloadx\?f=preview_OptiFine_{re.escape(mc_version  + ".0")}(?!\d)[^"]*jar"', html)
    Nvers = patern_search(rf'href="http://optifine\.net/adloadx\?f=OptiFine_{re.escape(mc_version)}(?!\d)[^"]*jar"', html)
    Nprev_vers = patern_search(rf'href="http://optifine\.net/adloadx\?f=preview_OptiFine_{re.escape(mc_version)}(?!\d)[^"]*jar"', html)

    Fvers = Svers + [item for item in Nvers if item not in Svers]
    Fprev_vers = Sprev_vers + [item for item in Nprev_vers if item not in Sprev_vers]

    if not Fvers and not Fprev_vers and nr<=0:
        if mc_version.removesuffix(".0") != mc_version:
            Fvers, Fprev_vers = fetch_optifine_versions(mc_version.removesuffix(".0")+"_", html, nr+1)
        elif mc_version.find(".0_") > -1:
            Fvers, Fprev_vers = fetch_optifine_versions(mc_version.replace(".0_","_",1) , html, nr+1)

    return Fvers, Fprev_vers

def download_file(url, output_path):
    if HEADERS:
        req = urllib.request.Request(url, headers=HEADERS)
    else:
        req = urllib.request.Request(url)

    with urllib.request.urlopen(req) as response:
        # Read the response data
        data = response.read()
        print("Done reading jar file")

        # Write the data to the output file
        with open(output_path, 'wb') as file:
            file.write(data)

def fetch_minecraft_client(version):
    manifest = fetch_html(MINECRAFT_MANIFEST_URL,True)

    version_info = next((v for v in manifest['versions'] if v['id'] == version), None)
    if not version_info:
        return None

    version_data = fetch_html(version_info['url'],True)

    client_url = version_data['downloads']['client']['url']
    return client_url

def patch_optifine(java,optifine_jar, mc_jar, output_jar):
    patch_command = [
        java, "-cp", optifine_jar, "optifine.Patcher", mc_jar, optifine_jar, output_jar
    ]
    subprocess.run(patch_command, check=True)

def list_versions(mc_version):
    versions, pre_versions = fetch_optifine_versions(mc_version)
    if not versions and not pre_versions:
        print(f"No OptiFine versions found for Minecraft {mc_version}.")
    else:
        print(f"Available OptiFine versions for Minecraft {mc_version}:")
        all_versions = versions + pre_versions
        all_versions.reverse()
        for link_nr in range(len(all_versions)):
            main_link, jar_version = all_versions[link_nr].split("_",1)
            version = jar_version[:-4]
            print("- " + version)


def extract_download_link(html):
    # Regex pattern to find the download link
    pattern = r'href=\'downloadx\?f=OptiFine_[^\'"]+&x=[a-f0-9]{32}\''
    match = re.search(pattern, html)

    if match:
        # Extract the relative URL part from the match
        relative_url = match.group(0)
        # Construct the full URL
        full_url = f'https://optifine.net/{relative_url[6:-1]}'
        return full_url
    else:
        print("Download link not found.")
        return None

def download_version(mc_version, pre, java):
    versions, pre_versions = fetch_optifine_versions(mc_version)
    #versions, pre_versions = ["https://optifine.net/adloadx?f=OptiFine_1.8.9_HD_U_M5.jar"], []
    if (pre and pre_versions) or (not versions and pre_versions):
        versions = pre_versions

    if versions:
        op_version_link = versions[0]
    else:
        print(f"No version found for {mc_version}")
        exit()
    nr_vers = op_version_link.find(mc_version)
    if nr_vers < 0:
        print(f"No version found for {mc_version}")
        exit()
    else:
        optifine_jar = op_version_link[nr_vers:]
        if optifine_jar.endswith(".jar"):
            optifine_version = optifine_jar.removesuffix(".jar")
        else:
            print(f"There was a problem with the download link {op_version_link} from the optifine webpage, is not a jar file")
            exit()
        split_op = optifine_version.split("_",1)
        if len(split_op) > 1:
            mc_version = split_op[0]
            op_ending = "_" + split_op[1]
        elif len(split_op) == 1:
            mc_version = split_op[0]
            op_ending = ""
        else:
            print(f"There was a problem detecting minecraft version {mc_version} from the optifine webpage for the link {op_version_link}")
            exit()

    time.sleep(2)
    download_page = fetch_html(op_version_link)
    download_link = extract_download_link(download_page)
    #download_link = "https://optifine.net/downloadx?f=OptiFine_1.8.9_HD_U_M5.jar&x=82306fe5063280fee220e41be4cce1d6"

    if not download_link:
        print(f"No download found for {mc_version} on download page {op_version_link}")
        exit()

    print(f"Downloading OptiFine {optifine_version}...")
    time.sleep(2)
    final_url = follow_redirect(download_link)

    os.makedirs(mc_version,exist_ok=True)

    full_optifine_jar = "optifine-" + mc_version + op_ending + ".jar"
    path_optifine_jar = os.path.join(mc_version,full_optifine_jar)

    time.sleep(2)
    download_file(final_url, path_optifine_jar)

    print(f"OptiFine {optifine_version} downloaded as {full_optifine_jar} in the subfolder {mc_version}.")

    print(f"Fetching Minecraft client jar for {mc_version}...")
    client_url = fetch_minecraft_client(mc_version)
    nmc_version = None
    if client_url == None:
        client_url = fetch_minecraft_client(mc_version.removesuffix(".0"))
        if client_url == None:
            print(f"Found no minecraft client for version {mc_version}")
            exit()
        else:
            nmc_version = mc_version.removesuffix(".0")

    if nmc_version:
        os.makedirs(nmc_version,exist_ok=True)

        nfull_optifine_jar = "optifine-" + nmc_version + op_ending + ".jar"
        npath_optifine_jar = os.path.join(nmc_version, nfull_optifine_jar)
        shutil.move(path_optifine_jar, npath_optifine_jar)

        try:
            os.rmdir(mc_version)
        except Exception as e:
            pass

        full_optifine_jar = nfull_optifine_jar
        path_optifine_jar = npath_optifine_jar
        mc_version = nmc_version


    mc_jar = f"minecraft-{mc_version}-client.jar"
    path_mc_jar = os.path.join(mc_version, mc_jar)
    download_file(client_url, path_mc_jar)
    print(f"Minecraft {mc_version} client jar downloaded as {mc_jar} in the subfolder {mc_version}.")

    output_jar = f"optifine-{mc_version}{op_ending}-MOD.jar"
    path_output_jar = os.path.join(mc_version,output_jar)
    print(f"Patching OptiFine into {output_jar} in subfolder {mc_version}...")
    patch_optifine(java, path_optifine_jar, path_mc_jar, path_output_jar)
    print(f"Patched OptiFine jar saved as {output_jar} in subfolder {mc_version}.")

def main():
    parser = argparse.ArgumentParser(description="OptiFine Downloader and Patcher")
    parser.add_argument("-l", "--list", help="List OptiFine versions for a specific Minecraft version (e.g., 1.16)")
    parser.add_argument("-d", "--download", help="Download and patch a specific OptiFine version (e.g., 1.16.5 or 1.16.5_HD_U_G8)")
    parser.add_argument("-j", "--java", default="java", help="Provide a custom java path")
    parser.add_argument("-w", "--workdir", help="Provide a custom working directory (the path will be relative to the script if not absolute)")
    parser.add_argument("-p", "--pre", action='store_true', help="Prioritize optifine preview versions instead on the normal ones")
    args = parser.parse_args()

    if args.list:
        list_versions(args.list)
    elif args.download:
        if args.workdir:
            if os.path.isabs(args.workdir):
                os.chdir(args.workdir)
            else:
                os.chdir(os.join(os.path.dirname(os.path.realpath(__file__)), args.workdir))
        download_version(args.download, args.pre, args.java)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
