"""
Main simulator class.
This class extends from arcade.Window and manages the updates and rendering of the simulator window.
"""
import argparse
import os
import sys

import arcade
import pyglet
from pymunk import Space

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# ## below not needed if ev3dev2simulator installed on PYTHONPATH
# ## put dir which contains  ev3dev2simulator on PYTHONPATH
# ev3devsimulator_dir = os.path.dirname(script_dir)
# sys.path.insert(0,ev3devsimulator_dir)


from ev3dev2simulator.config.config import load_config, write_scale_config, load_scale_config
from ev3dev2simulator.connection.ServerSocket import ServerSocket
from ev3dev2simulator.obstacle.Border import Border
from ev3dev2simulator.obstacle.Lake import BlueLake, GreenLake, RedLake
from ev3dev2simulator.obstacle.Rock import Rock
from ev3dev2simulator.robot.Robot import Robot
from ev3dev2simulator.state.RobotState import get_robot_state
from ev3dev2simulator.util.Util import apply_scaling



class Simulator(arcade.Window):



    def __init__(self, robot_state, robot_pos, show_fullscreen,show_maximized,use_second_screen_to_show_simulator):

        self.cfg = load_config()
        self.robot_state = robot_state


        # get current_screen_index
        current_screen_index=0
        if use_second_screen_to_show_simulator == True:
            current_screen_index=1
        display = pyglet.canvas.get_display()
        screens= display.get_screens()
        num_screens=len(screens)
        if  num_screens== 1:
            current_screen_index=0
        self.current_screen_index=current_screen_index


        # HACK override default screen function to change it.
        # Note: arcade window class doesn't has the screen parameter which pyglet has, so by overriding
        #       the get_default_screen method we can still change the screen parameter.
        def get_default_screen():
            """Get the default screen as specified by the user's operating system preferences."""
            return screens[self.current_screen_index]
        display.get_default_screen=get_default_screen

        # note:
        #  for macos  get_default_screen() is also used to as the screen to draw the window initially
        #  for windows the current screen is used to to draw the window initially,
        #              however the value set by get_default_screen() is used as the screen
        #              where to display the window fullscreen!

        # note: for Macos the screen of the mac can have higher pixel ratio (self.get_pixel_ratio())
        #       then the second screen connected. If you drag the window from the mac screen to the
        #       second screen then the windows may be the same size, but the simulator is drawn in only
        #       in the lower left quart of the window.
        #        => we need somehow make drawing of the simulator larger
        #       SOLUTION: just when starting up the simulator set it to open on the second screen,
        #                 then it goes well, and you can also open it fullscreen on the second screen
        # see also : https://stackoverflow.com/questions/49302201/highdpi-retina-windows-in-pyglet


        self.scaling_multiplier = load_scale_config()



        self.screen_width = int(apply_scaling(self.cfg['screen_settings']['screen_width']))
        self.screen_height = int(apply_scaling(self.cfg['screen_settings']['screen_height']))
        screen_title = self.cfg['screen_settings']['screen_title']


        super(Simulator, self).__init__(self.screen_width, self.screen_height, screen_title, update_rate=1 / 30,
                                        resizable=True)

        arcade.set_background_color((235, 235, 235))

        if show_fullscreen == True:
            self.toggleFullScreen()

        if show_maximized == True:
            self.maximize()

        self.robot_elements = None
        self.obstacle_elements = None

        self.robot = None
        self.robot_pos = robot_pos

        self.red_lake = None
        self.green_lake = None
        self.blue_lake = None

        self.rock1 = None
        self.rock2 = None

        self.border = None

        self.space = None

        self.center_cs_data = 0
        self.left_ts_data = False
        self.right_ts_data = False
        self.top_us_data = -1

        self.text_x = self.screen_width - apply_scaling(220)




    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """


        # Toggle fullscreen
        if key == arcade.key.T:
            # # User hits T. Switch screen used for fullscreen.
            # switch which screen is used for fullscreen ; Toggle between first and second screen (other screens are ignored)
            self.toggleScreenUsedForFullscreen()

        # Maximize window
        # note: is toggle on macos, but not on windows
        if key == arcade.key.M:
            if (not self.fullscreen): self.maximize()

        #src: http://arcade.academy/examples/full_screen_example.html
        # Fullscreen => keeps viewport coordinates the same   STRETCHED (FULLSCREEN)
        # Instead of a one-to-one mapping to screen size, we use stretch/squash window to match the constants.
        if key == arcade.key.F:
            self.toggleFullScreen()


    #toggle screen for fullscreen => doesn't work  => sizing errors
    def toggleScreenUsedForFullscreen(self):
        display = pyglet.canvas.get_display()
        screens= display.get_screens()
        num_screens=len(screens)
        if  num_screens== 1:
            return
        # toggle only between screen 0 and 1 (other screens are ignored)
        self.current_screen_index=(self.current_screen_index+1)%2

        # override hidden screen parameter in window
        self._screen=screens[self.current_screen_index]

    def toggleFullScreen(self):
            # User hits 'f' Flip between full and not full screen.
            #self.set_fullscreen(not self.fullscreen,self.screen_width*2, self.screen_height*2)
            self.set_fullscreen(not self.fullscreen)

            # Instead of a one-to-one mapping, stretch/squash window to match the
            # constants. This does NOT respect aspect ratio. You'd need to
            # do a bit of math for that.
            self.set_viewport(0, self.screen_width, 0, self.screen_height)

            # HACK for macos: without this hack fullscreen on the second screen is shifted downwards in the y direction
            #                 By also calling the maximize function te position the fullscreen in second screen is corrected!)
            import platform
            if platform.system() == "darwin":
                self.maximize()


    def on_resize(self, width, height):
        """ This method is automatically called when the window is resized. """

        # Call the parent. Failing to do this will mess up the coordinates, and default to 0,0 at the center and the
        # edges being -1 to 1.
        super().on_resize(width, height)

        self.set_viewport(0, self.screen_width, 0, self.screen_height)


    def setup(self):
        """
        Set up all the necessary shapes and sprites which are used in the simulation.
        These elements are added to lists to make buffered rendering possible to improve performance.
        """

        self.robot_elements = arcade.SpriteList()
        self.obstacle_elements = arcade.ShapeElementList()

        self.robot = Robot(self.cfg, self.robot_pos[0], self.robot_pos[1], self.robot_pos[2])

        for s in self.robot.get_sprites():
            self.robot_elements.append(s)

        for s in self.robot.get_sensors():
            self.robot_state.load_sensor(s)

        self.blue_lake = BlueLake(self.cfg)
        self.green_lake = GreenLake(self.cfg)
        self.red_lake = RedLake(self.cfg)

        # self.rock1 = Rock(apply_scaling(175), apply_scaling(700), apply_scaling(150), apply_scaling(60), arcade.color.DARK_GRAY, 0)
        self.rock2 = Rock(apply_scaling(1000), apply_scaling(300), apply_scaling(300), apply_scaling(90), arcade.color.DARK_GRAY, 90)

        self.obstacle_elements.append(self.blue_lake.shape)
        self.obstacle_elements.append(self.green_lake.shape)
        self.obstacle_elements.append(self.red_lake.shape)

        # self.obstacle_elements.append(self.rock1.shape)
        self.obstacle_elements.append(self.rock2.shape)

        self.border = Border(self.cfg, arcade.color.BLACK_OLIVE)

        for s in self.border.shapes:
            self.obstacle_elements.append(s)

        color_obstacles = [self.blue_lake, self.green_lake, self.red_lake, self.border]
        touch_obstacles = [self.rock2]
        # touch_obstacles = [self.rock1, self.rock2]

        self.robot.set_color_obstacles(color_obstacles)
        self.robot.set_touch_obstacles(touch_obstacles)

        self.space = Space()
        # self.space.add(self.rock1.poly)
        self.space.add(self.rock2.poly)


    def on_draw(self):
        """
        Render the simulation. This is done in 30 frames per second.
        """

        arcade.start_render()

        self.obstacle_elements.draw()
        self.robot_elements.draw()

        self._draw_text()



    def _draw_text(self):
        center_cs = 'CS center:  ' + str(self.center_cs_data)
        left_ts = 'TS right:      ' + str(self.right_ts_data)
        right_ts = 'TS left:         ' + str(self.left_ts_data)
        top_us = 'US top:        ' + str(int(round(self.top_us_data / self.scaling_multiplier))) + 'mm'

        message = self.robot_state.next_sound_job()
        sound = message if message else '-'

        arcade.draw_text(center_cs, self.text_x, self.screen_height - apply_scaling(80), arcade.color.BLACK_LEATHER_JACKET, 10)
        arcade.draw_text(left_ts, self.text_x, self.screen_height - apply_scaling(100), arcade.color.BLACK_LEATHER_JACKET, 10)
        arcade.draw_text(right_ts, self.text_x, self.screen_height - apply_scaling(120), arcade.color.BLACK_LEATHER_JACKET, 10)
        arcade.draw_text(top_us, self.text_x, self.screen_height - apply_scaling(140), arcade.color.BLACK_LEATHER_JACKET, 10)
        arcade.draw_text('Sound:', self.text_x, self.screen_height - apply_scaling(160), arcade.color.BLACK_LEATHER_JACKET, 10)
        arcade.draw_text(sound, self.text_x, self.screen_height - apply_scaling(180), arcade.color.BLACK_LEATHER_JACKET, 10, anchor_y='top')


    def update(self, delta_time):
        """
        All the logic to move the robot. Collision detection is also performed.
        """

        if self.robot_state.should_reset:
            self.setup()
            self.robot_state.reset()

        else:
            left_ppf, right_ppf = self.robot_state.next_move_jobs()

            if left_ppf or right_ppf:
                self.robot.execute_movement(left_ppf, right_ppf)

            address_center_cs = self.robot.center_color_sensor.address
            address_left_ts = self.robot.left_touch_sensor.address
            address_right_ts = self.robot.right_touch_sensor.address
            address_us = self.robot.ultrasonic_sensor.address

            self.center_cs_data = self.robot.center_color_sensor.get_sensed_color()
            self.left_ts_data = self.robot.left_touch_sensor.is_touching()
            self.right_ts_data = self.robot.right_touch_sensor.is_touching()
            self.top_us_data = self.robot.ultrasonic_sensor.distance(self.space)

            self.robot_state.values[address_center_cs] = self.center_cs_data
            self.robot_state.values[address_left_ts] = self.left_ts_data
            self.robot_state.values[address_right_ts] = self.right_ts_data
            self.robot_state.values[address_us] = self.top_us_data

        self.robot_state.release_locks()


def main():

    """
    Spawns the user thread and creates and starts the simulation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--window_scaling",
                        default=load_config()['screen_settings']['scaling_multiplier'],
                        help="Scaling of the screen, default is 0.7",
                        required=False,
                        type=check_scale)
    parser.add_argument("-x", "--robot_position_x",
                        default=200,
                        help="Starting position x-coordinate of the robot, default is 200",
                        required=False,
                        type=check_xy)
    parser.add_argument("-y", "--robot_position_y",
                        default=300,
                        help="Starting position y-coordinate of the robot, default is 300",
                        required=False,
                        type=check_xy)
    parser.add_argument("-o", "--robot_orientation",
                        default=0,
                        help="Starting orientation the robot, default is 0",
                        required=False,
                        type=int)

    parser.add_argument("-2", "--show-on-second-monitor",
                        action='store_true',
                        help="Show simulator window on second monitor instead, default is first monitor")
    parser.add_argument("-f", "--fullscreen",
                        action='store_true',
                        help="Show simulator fullscreen")
    parser.add_argument("-m", "--maximized",
                        action='store_true',
                        help="Show simulator maximized")


    args = vars(parser.parse_args())

    s = args['window_scaling']
    write_scale_config(s)

    x = apply_scaling(args['robot_position_x'])
    y = apply_scaling(args['robot_position_y'])
    o = args['robot_orientation']

    use_second_screen_to_show_simulator=args['show_on_second_monitor']
    show_fullscreen=args['fullscreen']
    show_maximized=args['maximized']


    robot_state = get_robot_state()
    robot_pos= (x, y, o)

    server_thread = ServerSocket(robot_state)
    server_thread.setDaemon(True)
    server_thread.start()

    sim = Simulator(robot_state, robot_pos,show_fullscreen,show_maximized,use_second_screen_to_show_simulator)
    sim.setup()
    arcade.run()




def check_scale(value):
    try:
        f = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError('Scaling value must be a floating point number')

    if f < 0.0 or f > 1.0:
        raise argparse.ArgumentTypeError("%s is an invalid scaling value. Should be between 0 and 1" % f)

    return f


def check_xy(value):
    try:
        f = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('Coordinate value must be a integer')

    if f < 0 or f > 1000:
        raise argparse.ArgumentTypeError("%s is an invalid coordinate. Should be between 0 and 1000" % f)

    return f

