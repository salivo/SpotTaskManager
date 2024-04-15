import configparser
import json
class Config:
    def __init__(self):
        truestr = ("yes", "true", "t", "1", "yep", "aha", "ano", "jo")
        parser = configparser.ConfigParser()
        parser.read("config.conf")
        # robot
        self.hostname = parser.get("robot", "hostname")
        self.verbose = parser.get("robot", "verbose").lower() in truestr
        self.user = parser.get("robot", "user")
        self.password = parser.get("robot", "password")
        self.timeout = int(parser.get("robot", "timeout"))
        # autowalk
        self.graphnavs_dir = parser.get("graph_nav", "graphnavs_dir")
        self.graphnav_name = parser.get("graph_nav", "graphnav_name")
