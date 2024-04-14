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
        self.path_following_mode = int(parser.get("graph_nav", "path_following_mode"))
        self.graph_directory = parser.get("graph_nav", "graph_directory")
        self.upload_timeout = float(parser.get("graph_nav", "upload_timeout"))
        self.graph_timeout = float(parser.get("graph_nav", "graph_timeout"))
        self.disable_directed_exploration = parser.get("graph_nav", "disable_directed_exploration").lower() in truestr
