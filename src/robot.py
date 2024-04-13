import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
from bosdyn.api.autowalk import walks_pb2
from bosdyn.api.graph_nav import map_pb2
import bosdyn.api.mission
import bosdyn.mission.client
from bosdyn.api.mission import mission_pb2
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.robot_state import RobotStateClient
from time import sleep


class Robot():
    def __init__(self, config):
        self.config = config
        # get sdk and some settings
        bosdyn.client.util.setup_logging(self.config.verbose)
        sdk = bosdyn.client.create_standard_sdk('SpotClient', [bosdyn.mission.client.MissionClient]) # [bosdyn.mission.client.MissionClient] for autowalk
        self.robot = sdk.create_robot(self.config.hostname)

        # Turning robot on
        self.robot.authenticate(self.config.user, self.config.password)
        self.robot.time_sync.wait_for_sync()
        assert not self.robot.is_estopped(), 'Robot is estopped'
        
        # clients:
        self.state_client = self.robot.ensure_client(RobotStateClient.default_service_name)
        self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
        self.lease_client = self.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        self.__locked_messages = ['', '', '']
        
    def stand(self):
            self.robot.logger.info('Powering on robot... This may take several seconds.')
            self.robot.power_on(timeout_sec=20)
            assert self.robot.is_powered_on(), 'Robot power on failed.'
            blocking_stand(self.command_client, timeout_sec=10)
            self.robot.logger.info('Robot standing.')
            
    def off(self):
            sleep(1)
            self.robot.power_off(cut_immediately=False, timeout_sec=20)
            assert not self.robot.is_powered_on(), 'Robot power off failed.'
            self.robot.logger.info('Robot safely powered off.')
