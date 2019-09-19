#! /bin/env python
"""
Refactor torrents in qbittorrents from a folder to another folder
based on certain criteria using qbittorrent set location
"""
import argparse
import os
import logging.config
from client import Client
from textwrap import dedent

IP = "http://192.168.1.105:9001"
AUDIO_EXTENSION = ["mp3", "ogg", "wav", "m4b", "m4a"]
qbit_logger = logging.getLogger(__name__)


class Config:
    log_file = None
    login_cred = [os.environ.get("QBIT_USER", "admin"), os.environ.get("QBIT_PASS", "adminadmin")]
    source_dir = "/media/Books"
    dest_dir = "/media/AudioBooks"
    tracker = "myanonamouse"
    extensions = AUDIO_EXTENSION
    exclude_extensions = []
    url = IP
    no_move = False
    verbose = False


def _matched_ext(file_name: str, extensions: list):
    ext = ""
    for s in reversed(file_name):
        if s == ".":
            break
        ext = s + ext
    return ext in extensions


def _files_matched(t_files, config: Config):
    result = False
    for t in t_files:
        if _matched_ext(t["name"], config.extensions):
            result = True
        if _matched_ext(t["name"], config.exclude_extensions):
            return False
    return result


def refactor_torrents(qb: Client, config: Config):
    qb.login(*config.login_cred)
    if not qb._is_authenticated:
        qbit_logger.error("Invalid login username/password.")
        return
    n = 1
    hashes_to_change = []
    qbit_logger.info(f"Moving audiobooks from {config.source_dir} to {config.dest_dir}")
    for this_torrent in qb.torrents():
        hash = this_torrent["hash"]
        t_properties = qb.get_torrent(hash)
        t_files = qb.get_torrent_files(hash)
        if _files_matched(t_files, config) \
                and config.tracker in this_torrent["tracker"] \
                and os.path.samefile(t_properties["save_path"], config.source_dir) :
            qbit_logger.info(f"{n}: {this_torrent['name']}, path {t_properties['save_path']}")
            hashes_to_change.append(hash)
            n += 1
    qbit_logger.info(f"changing {len(hashes_to_change)} torrents to {config.dest_dir}")
    if not config.no_move:
        qbit_logger.info(f"performing set_location on qittorrent on these hashes: {hashes_to_change}")
        qb.set_location(hashes_to_change, config.dest_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=dedent("""\
        Refactor torrents in qbittorrents from a folder to another folder \
        based on certain criteria using qbittorrent set location
        """))
    parser.add_argument("-u", "--url", dest="url", default=IP, help="the url for qbittorrent web.")
    parser.add_argument("-l", "--login", dest="login_cred", nargs=2, metavar="<ID> <PW>",
                        help=dedent("""\
        Enter your qbittorrent login credential.
            -l <USERNAME> <PASSWORD>
        or use environment variable:
            QBIT_USER, QBIT_PASS
        Default:
            username = admin
            password = adminadmin
                        """))
    parser.add_argument("-s", "--source", dest="source_dir", type=str, default="/media/Books",
                        help="specify the source dir to look scan for torrents.")
    parser.add_argument("-d", "--dest", dest="dest_dir", type=str, default="/media/AudioBooks",
                        help="specify the destination directory for moving.")
    parser.add_argument("-t", "--tracker", dest="tracker", type=str, default="myanonamouse",
                        help="filter the tracker.")
    parser.add_argument("-e", "--extension", dest="extensions", nargs="+",
                        help="filter the file extension")
    parser.add_argument("-x", "--exclude", dest="exclude_extensions", nargs="+", metavar="<EXT>",
                        help="exclude moving of the files if matches specified extensions")
    parser.add_argument("--no-move", dest="no_move", help="Does not perform set location.", action="store_true")
    parser.add_argument("--log-file", dest="log_file", metavar="<LOG_FILE>", type=argparse.FileType('wb', 0),
                        help="specify the log file.")
    config = Config()
    parser.parse_args(namespace=config)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if config.log_file:
        fh = logging.FileHandler(config.log_file.name, 'a')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        qbit_logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    qbit_logger.addHandler(sh)
    qbit_logger.setLevel(logging.INFO)
    qb = Client(IP)
    refactor_torrents(qb, config)
