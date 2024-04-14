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



# for graph nav
from bosdyn.client.math_helpers import Quat, SE3Pose

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
        self.graph_nav_client = self._robot.ensure_client(GraphNavClient.default_service_name)
        self.__locked_messages = ['', '', '']

        # graph navigation
        self._current_graph = None
        self._current_edges = dict()  #maps to_waypoint to list(from_waypoint)
        self._current_waypoint_snapshots = dict()  # maps id to waypoint snapshot
        self._current_edge_snapshots = dict()  # maps id to edge snapshot
        self._current_annotation_name_to_wp_id = dict()
        
        self.__upload_graph_and_snapshots() # load graph and snapshots to robot
        self._set_initial_localization_fiducial()# localize robot to finductial
        
    def stand(self):
        blocking_stand(self.command_client, timeout_sec=10)
        
    def sit(self)
        blocking_sit(self.command_client, timeout_sec=10)
        
    def motorsOn(self):
        self.robot.power_on(timeout_sec=20)
        assert self.robot.is_powered_on(), 'Robot power on failed.'
        self.robot.logger.info('Robot powered on.')
        
    def motorsOff(self):
        sleep(1)
        self.robot.power_off(cut_immediately=False, timeout_sec=20)
        assert not self.robot.is_powered_on(), 'Robot power off failed.'
        self.robot.logger.info('Robot safely powered off.')

     def __upload_graph_and_snapshots(self, *args):
        with open(self.config.graph_directory + '/graph', 'rb') as graph_file:
            # Load the graph from disk.
            data = graph_file.read()
            self._current_graph = map_pb2.Graph()
            self._current_graph.ParseFromString(data)
            print(
                f'Loaded graph has {len(self._current_graph.waypoints)} waypoints and {self._current_graph.edges} edges'
            )
        for waypoint in self._current_graph.waypoints:
            # Load the waypoint snapshots from disk.
            with open(f'{self._upload_filepath}/waypoint_snapshots/{waypoint.snapshot_id}',
                      'rb') as snapshot_file:
                waypoint_snapshot = map_pb2.WaypointSnapshot()
                waypoint_snapshot.ParseFromString(snapshot_file.read())
                self._current_waypoint_snapshots[waypoint_snapshot.id] = waypoint_snapshot
        for edge in self._current_graph.edges:
            if len(edge.snapshot_id) == 0:
                continue
            # Load the edge snapshots from disk.
            with open(f'{self._upload_filepath}/edge_snapshots/{edge.snapshot_id}',
                      'rb') as snapshot_file:
                edge_snapshot = map_pb2.EdgeSnapshot()
                edge_snapshot.ParseFromString(snapshot_file.read())
                self._current_edge_snapshots[edge_snapshot.id] = edge_snapshot
        # Upload the graph to the robot.
        print('Uploading the graph and snapshots to the robot...')
        true_if_empty = not len(self._current_graph.anchoring.anchors)
        response = self.graph_nav_client.upload_graph(graph=self._current_graph,
                                                       generate_new_anchoring=true_if_empty)
        # Upload the snapshots to the robot.
        for snapshot_id in response.unknown_waypoint_snapshot_ids:
            waypoint_snapshot = self._current_waypoint_snapshots[snapshot_id]
            self.graph_nav_client.upload_waypoint_snapshot(waypoint_snapshot)
            print(f'Uploaded {waypoint_snapshot.id}')
        for snapshot_id in response.unknown_edge_snapshot_ids:
            edge_snapshot = self._current_edge_snapshots[snapshot_id]
            self.graph_nav_client.upload_edge_snapshot(edge_snapshot)
            print(f'Uploaded {edge_snapshot.id}')

        # The upload is complete! Check that the robot is localized to the graph,
        # and if it is not, prompt the user to localize the robot before attempting
        # any navigation commands.
        localization_state = self.graph_nav_client.get_localization_state()
        if not localization_state.localization.waypoint_id:
            # The robot is not localized to the newly uploaded graph.
            print('\n')
            print(
                'Upload complete! The robot is currently not localized to the map; please localize'
                ' the robot using commands (2) or (3) before attempting a navigation command.')
                
        def _set_initial_localization_fiducial(self, *args):
                robot_state = self.state_client.get_robot_state()
                current_odom_tform_body = get_odom_tform_body(
                    robot_state.kinematic_state.transforms_snapshot).to_proto()
                # Create an empty instance for initial localization since we are asking it to localize
                # based on the nearest fiducial.
                localization = nav_pb2.Localization()
                self.graph_nav_client.set_localization(initial_guess_localization=localization,
                                                        ko_tform_body=current_odom_tform_body)
        def _navigate_to_anchor(self, x, y, z=0):        
                seed_T_goal = SE3Pose(float(x), float(y), float(z), Quat())

                
                # if not self.toggle_power(should_power_on=True):
                #     print('Failed to power on the robot, and cannot complete navigate to request.')
                #     return
        
                nav_to_cmd_id = None
                # Navigate to the destination.
                is_finished = False
                while not is_finished:
                    # Issue the navigation command about twice a second such that it is easy to terminate the
                    # navigation command (with estop or killing the program).
                    try:
                        nav_to_cmd_id = self._graph_nav_client.navigate_to_anchor(
                            seed_T_goal.to_proto(), 1.0, command_id=nav_to_cmd_id)
                    except ResponseError as e:
                        print(f'Error while navigating {e}')
                        break
                    time.sleep(.5)  # Sleep for half a second to allow for command execution.
                    # Poll the robot for feedback to determine if the navigation command is complete. Then sit
                    # the robot down once it is finished.
                    is_finished = self._check_success(nav_to_cmd_id)
        
                # Power off the robot if appropriate.
                if self._powered_on and not self._started_powered_on:
                    # Sit the robot down + power off after the navigation command is complete.
                    self.toggle_power(should_power_on=False)
