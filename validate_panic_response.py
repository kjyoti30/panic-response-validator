import argparse
import sys
import os
import subprocess
import validators
from urllib import parse
import ftputil

content_id = 1540023362
server_name="failovernovi.ftp.upload.akamai.com"
user="novi_alb"
password = ""
watch_path = "/822471/panic-response/hotstar-x/page-compositor/prod/in/watch/weighted/ultimate"
v5_path = "/822471/panic-response/hotstar-x/pcdds-v5/prod/in"
proto_platform_list = ["android", "androidtv", "ios", "appletv", "firetv"]
json_platform_list = ["web", "mweb", "webos", "tizentv", "chromecast"]
v5_platform_list = ["android", "androidtv", "ios", "appletv", "firetv", "web", "mweb", "webos", "tizentv", "chromecast"]
cmd = """ protoc --decode_raw < {} | grep 'ads' | grep 'http' | grep -E '.mpd\?|.m3u8\?' | head -1 """
cmd2 = """jq '.success.page.spaces.player.widget_wrappers[0].widget.data.player_config.media_asset_v2.primary.content_url' -r {}"""
cmd3 = """jq '.success.page.spaces.player.widget_wrappers[0].widget.data.player_config.media_asset_v2.primary.playback_tags' -r {}"""
cmd4 = """jq '.data.playback_sets[0].playback_url' -r {}"""
cmd5 = """jq '.data.playback_sets[0].tags_combination' -r {}"""

def validate_path(path):
    return os.path.exists(path)

def validate_url(url, cdn):
    res = parse.urlsplit(url)
    hostname = res.hostname
    path = res.path
    query = parse.parse_qs(res.query)
    queryparams = dict(query)
    valid = True
    hdnea = queryparams["hdnea"]
    if len(hdnea) > 0:
        hdnea_list = hdnea[0].split("~")
        hdneadict = dict()
        for item in hdnea_list:
            keyval = item.split("=")
            hdneadict[keyval[0]] = keyval[1]
    else:
        valid = False
    if cdn == "akamai":
        if "live12p" not in hostname:
            valid = False
        if "apmf" not in path:
            valid = False
        if "acl" not in hdneadict:
            valid = False
    elif cdn == "airtel":
        if "airtel" not in hostname:
            valid = False
        if "apmf" not in path:
            valid = False
        if "acl" not in hdneadict or "apmf" not in hdneadict["acl"]:
            valid = False
        if "type" not in hdneadict or hdneadict["type"] != "free":
            valid = False
        if "ttl" not in hdneadict or hdneadict["ttl"] != "86400":
            valid = False
    elif cdn == "cloudfront":
        if "cf" not in hostname:
            valid = False
        if "apmf" not in path:
            valid = False
        if "acl" not in hdneadict or "apmf" not in hdneadict["acl"]:
            valid = False
        if "type" not in hdneadict or hdneadict["type"] != "free":
            valid = False
        if "ttl" not in hdneadict or hdneadict["ttl"] != "86400":
            valid = False
    elif cdn == "gme":
        if "gme" not in hostname:
            valid = False
        if "apmf" not in path:
            valid = False
        if "acl" not in hdneadict or "apmf" not in hdneadict["acl"]:
            valid = False
    return valid
        
def validate_tag_combination(tag_combination):
    valid = True
    tag_combination_list = tag_combination.split(";")
    tag_combination_dict = dict()
    for tag in tag_combination_list:
        keyval = tag.split(":")
        tag_combination_dict[keyval[0]] = keyval[1]
    if "ads" not in tag_combination_dict or tag_combination_dict["ads"] != "non_ssai":
        valid = False
    if "language" not in tag_combination_dict or tag_combination_dict["language"] != "hin":
        valid = False
    if "resolution" not in tag_combination_dict or tag_combination_dict["resolution"] != "sd":
        valid = False
    return valid

def validate_response_proto(path, cdn):
    exist = validate_path(path)
    if not exist:
        print("Error: Invalid path", path)
    else:
        c = cmd.format(path)
        out = subprocess.getoutput(c)
        out_arr = out.strip().split(" ")
        spilt_by_ads = out_arr[1].split("ads")
        tag_combination = "ads" + spilt_by_ads[1].rstrip('"')
        playback_url = "http" + spilt_by_ads[0].split("http")[1].split("\\")[0]
        valid_url = validators.url(playback_url)
        if valid_url:
            valid = validate_url(playback_url, cdn)
            if not valid:
                print("{} : '\u2715' - invalid url ".format(cdn))
            valid = validate_tag_combination(tag_combination)
            if not valid:
                print("{} : '\u2715' - invalid tag_combination ".format(cdn))
            if valid:
                print("{} : '\u2713' ".format(cdn))


def validate_response_json(path, cdn):
    exist = validate_path(path)
    if not exist:
        print("Error: Invalid path", path)
    else:
        c = cmd2.format(path)
        playback_url = subprocess.getoutput(c)
        c = cmd3.format(path)
        tag_combination = subprocess.getoutput(c)
        valid_url = validators.url(playback_url)
        if valid_url:
            valid = validate_url(playback_url, cdn)
            if not valid:
                print("{} : '\u2715' - invalid url ".format(cdn))
            valid = validate_tag_combination(tag_combination)
            if not valid:
                print("{} : '\u2715' - invalid tag_combination ".format(cdn))
            if valid:
                print("{} : '\u2713' ".format(cdn))

def validate_response_json_v5(path, cdn):
    exist = validate_path(path)
    if not exist:
        print("Error: Invalid path", path)
    else:
        c = cmd4.format(path)
        playback_url = subprocess.getoutput(c)
        c = cmd5.format(path)
        tag_combination = subprocess.getoutput(c)
        valid_url = validators.url(playback_url)
        if valid_url:
            valid = validate_url(playback_url, cdn)
            if not valid:
                print("{} : '\u2715' - invalid url ".format(cdn))
                return
            valid = validate_tag_combination(tag_combination)
            if not valid:
                print("{} : '\u2715' - invalid tag_combination ".format(cdn))
            if valid:
                print("{} : '\u2713' ".format(cdn))


def traverse_directory(ftp_host, watch_path):
    ftp_host.chdir(watch_path)
    directories = ftp_host.listdir(ftp_host.curdir)
    # print(directories)
    # validating response for platforms with response in proto format
    for platform in proto_platform_list:
        files = ftp_host.listdir(ftp_host.curdir + '/' + platform + '-cdn')
        print("----------- {} -----------".format(platform))
        for file in files:
            file_path = watch_path + '/' + platform + '-cdn' + '/' + file
            if ftp_host.path.isfile(file_path):
                ftp_host.download(file_path, "/tmp/" + file)
                validate_response_proto("/tmp/" + file, file)
    # validating response for platforms with response in json format
    for platform in json_platform_list:
        files = ftp_host.listdir(ftp_host.curdir + '/' + platform + '-cdn')
        print("----------- {} -----------".format(platform))
        for file in files:
            file_path = watch_path + '/' + platform + '-cdn' + '/' + file
            if ftp_host.path.isfile(file_path):
                ftp_host.download(file_path, "/tmp/" + file)
                validate_response_json("/tmp/" + file, file)

def traverse_directory_v5(ftp_host, v5_path):
    ftp_host.chdir(v5_path)
    directories = ftp_host.listdir(ftp_host.curdir)
    # validating response for platforms
    for platform in v5_platform_list:
        files = ftp_host.listdir(ftp_host.curdir + '/' + platform + '-cdn')
        print("----------- {} -----------".format(platform))
        for file in files:
            file_path = v5_path + '/' + platform + '-cdn' + '/' + file
            if ftp_host.path.isfile(file_path):
                ftp_host.download(file_path, "/tmp/" + file)
                validate_response_json_v5("/tmp/" + file, file)

    
def validate_watch_panic_response():
    try:
        # establishing connection with ftp server
        with ftputil.FTPHost(server_name, user, password) as ftp_host:
            names = ftp_host.listdir(ftp_host.curdir)
            watch_path_dir = watch_path + '/' + content_id 
            traverse_directory(ftp_host, watch_path_dir)
    except Exception as e:
        print("Error: Not able to connect to filezilla", e)

def validate_v5_panic_response():
    try:
        # establishing connection with ftp server
        with ftputil.FTPHost(server_name, user, password) as ftp_host:
            names = ftp_host.listdir(ftp_host.curdir)
            v5_path_dir = v5_path + '/' + content_id 
            traverse_directory_v5(ftp_host, v5_path_dir)
    except Exception as e:
        print("Error: Not able to connect to filezilla", e)
        
if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-c", "--content_id", help="content-id", required=True)
    argParser.add_argument("-p", "--password", help="filezilla password", required=True)
    args = argParser.parse_args()
    content_id = args.content_id
    password = args.password
    print("----------- Content-id: {} -----------".format(content_id))
    print("\n----------- Validating Watch panic response -----------")
    validate_watch_panic_response()
    print("\n----------- Validating V5 panic response -----------")
    validate_v5_panic_response()