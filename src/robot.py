import bosdyn.client
import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
import bosdyn.api.mission
from bosdyn.client.exceptions import ResponseError
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand, blocking_sit
from bosdyn.client.robot_state import RobotStateClient
from time import sleep
# for graph nav
from bosdyn.client.math_helpers import Quat, SE3Pose
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.api.graph_nav import graph_nav_pb2, map_pb2, nav_pb2
#for localization by fiducials
from bosdyn.client.frame_helpers import get_odom_tform_body


class Robot():
    def __init__(self, config):
        self.config = config
        # get sdk and some settings
        bosdyn.client.util.setup_logging(self.config.verbose)
        sdk = bosdyn.client.create_standard_sdk('SpotClient') # add [bosdyn.mission.client.MissionClient] for autowalk
        self.robot = sdk.create_robot(self.config.hostname)
        # auth
        self.robot.authenticate(self.config.user, self.config.password)
        self.robot.time_sync.wait_for_sync()
        assert not self.robot.is_estopped(), 'Robot is estopped'
        # Clients:
        self.state_client = self.robot.ensure_client(RobotStateClient.default_service_name)
        self.command_client = self.robot.ensure_client(RobotCommandClient.default_service_name)
        self.lease_client = self.robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        self.graph_nav_client = self.robot.ensure_client(GraphNavClient.default_service_name)
        # States
        self.powerState = False
        # Graph navigation vars
        self._current_graph = None
        self._current_edges = dict()
        self._current_waypoint_snapshots = dict()
        self._current_edge_snapshots = dict()
        self._current_annotation_name_to_wp_id = dict()
        # load snapshots
        self.__upload_graph_and_snapshots()
        self.localizeByFiducial()  
              
    def stand(self):
        if not self.powerState:
            self.controlPower(True)
        blocking_stand(self.command_client, timeout_sec=10)
    def sit(self):
        blocking_sit(self.command_client, timeout_sec=10)
        
    def controlPower(self, powerOn):            
        if powerOn:
            self.robot.power_on(timeout_sec=20)
            assert self.robot.is_powered_on(), 'Robot power on failed.'
            self.robot.logger.info('Robot powered on.')
            self.powerState = True
        else:
            self.sit()
            sleep(1)
            self.robot.power_off(cut_immediately=False, timeout_sec=20)
            assert not self.robot.is_powered_on(), 'Robot power off failed.'
            self.robot.logger.info('Robot safely powered off.')
            self.powerState = False

    def __read_graphfile(self, graphnav_dirpath):
        with open(graphnav_dirpath + '/graph', 'rb') as graph_file:
            graphnav_readed_data = graph_file.read()
            self._current_graph = map_pb2.Graph()
            self._current_graph.ParseFromString(graphnav_readed_data)
            
    def __read_waypoints(self, graphnav_dirpath):
        for waypoint in self._current_graph.waypoints:
            with open(f'{graphnav_dirpath}/waypoint_snapshots/{waypoint.snapshot_id}', 'rb') as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                self._current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot
                        
    def __read_edges(self):
        for edge in self._current_graph.edges:
            if len(edge.snapshot_id) == 0:
                continue
            with open(f'{graphnav_dirpath}/edge_snapshots/{edge.snapshot_id}','rb') as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                self._current_edge_snapshots[edge_snapshot.id] = edge_snapshot
                
    def __load_waypoints(self, upload_graph_interface):
        for snapshot_id in upload_graph_interface.unknown_waypoint_snapshot_ids:
            waypoint_snapshot = self._current_waypoint_snapshots[snapshot_id]
            self.graph_nav_client.upload_waypoint_snapshot(waypoint_snapshot)
            
    def __load_edges(self, upload_graph_interface):
        for snapshot_id in upload_graph_interface.unknown_edge_snapshot_ids:
            edge_snapshot = self._current_edge_snapshots[snapshot_id]
            self.graph_nav_client.upload_edge_snapshot(edge_snapshot)
                    
    def __upload_graph_and_snapshots(self, *args):
        graphnav_dirpath = self.config.graphnavs_dir + "/" + self.config.graphnav_name
        self.__read_graphfile(graphnav_dirpath)
        self.__read_waypoints(graphnav_dirpath)  
        true_if_empty = not len(self._current_graph.anchoring.anchors)
        upload_graph_interface = self.graph_nav_client.upload_graph(
            graph=self._current_graph, generate_new_anchoring=true_if_empty)
        self.__load_waypoints(upload_graph_interface)
        self.__load_edges(upload_graph_interface)

    def localizeByFiducial(self, *args):
        robot_state = self.state_client.get_robot_state()
        current_odom_tform_body = get_odom_tform_body(
            robot_state.kinematic_state.transforms_snapshot).to_proto()
        localization = nav_pb2.Localization()
        self.graph_nav_client.set_localization(initial_guess_localization=localization,
                                                ko_tform_body=current_odom_tform_body)
                                                    
    def _navigate_to_anchor(self, x, y, z=0):        
        seed_T_goal = SE3Pose(float(x), float(y), float(z), Quat())
        self.stand()
        nav_to_cmd_id = None
        is_finished = False
        while not is_finished:
            try:
                nav_to_cmd_id = self.graph_nav_client.navigate_to_anchor(
                    seed_T_goal.to_proto(), 1.0, command_id=nav_to_cmd_id)
            except ResponseError as e:
                print(f'Error while navigating {e}')
                break
            sleep(.5)
            is_finished = self.check_success(nav_to_cmd_id)

    def check_success(self, command_id=-1):
        if command_id == -1:
            return False
        feedback = self.graph_nav_client.navigation_feedback(command_id)
        if feedback.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_REACHED_GOAL:
            return True
        elif feedback.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_LOST:
            print('Robot got lost when navigating the route, the robot will now sit down.')
            return True
        elif feedback.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_STUCK:
            print('Robot got stuck when navigating the route, the robot will now sit down.')
            return True
        elif feedback.status == graph_nav_pb2.NavigationFeedbackResponse.STATUS_ROBOT_IMPAIRED:
            print('Robot is impaired.')
            return True
        else:
            return False

