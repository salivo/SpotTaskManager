import configparser
import json
class Config:
    def __init__(self):
        truestr = ("yes", "true", "t", "1", "yep", "aha", "ano", "jo")
        parser = configparser.ConfigParser()
        parser.read("config.conf")
        # robot
        self.hostname = parser.get("config", "hostname")
        self.verbose = parser.get("config", "verbose").lower() in truestr
        self.user = parser.get("config", "user")
        self.password = parser.get("config", "password")
        self.timeout = int(parser.get("config", "timeout"))
        # autowalk
        self.path_following_mode = int(parser.get("autowalk", "path_following_mode"))
        self.walk_directory = parser.get("autowalk", "walk_directory")
        self.upload_timeout = float(parser.get("autowalk", "upload_timeout"))
        self.mission_timeout = float(parser.get("autowalk", "mission_timeout"))
        self.disable_directed_exploration = parser.get("autowalk", "disable_directed_exploration").lower() in truestr
