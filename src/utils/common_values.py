# TEAM STATISTICS
BLUE_TEAM = 0
ORANGE_TEAM = 1

# ACTION SPACE :
NUM_ACTIONS = 8

# FIELD STATISTICS :
CENTER_X = 0
CENTER_Y = 0
SIDE_WALL_X = 4096  # +/-
BACK_WALL_Y = 5120  # +/-
CEILING_Z = 2044

# BALL STATISTICS :
BALL_RADIUS = 92.75 # Or 94.41?? TODO = Need to double-check
BALL_MAX_SPEED = 6000

# CAR STATISTICS :
CAR_MAX_SPEED = 2300
SUPERSONIC_THRESHOLD = 2200
CAR_MAX_ANG_VEL = 5.5

# OCTANE STATISTICS :
# Octane Hitbox 
OCTANE_LENGTH = 118.01                  # unreal units (uu)
OCTANE_WIDTH = 84.20                    # unreal units (uu)
OCTANE_HEIGHT = 36.16                   # unreal units (uu)
OCTANE_ANGLE = -0.55                    # degrees
OCTANE_HEIGHT_AT_FRONT = 55.13          # unreal units (uu)
OCTANE_BACK = 56.27                     # unreal units (uu)
# Octane Turning
OCTANE_MAX_ANG_VEL = 1.98               # rad/s
OCTANE_RESPONSIVENESS = 0.97
OCTANE_BEST_AVG_TURN = 1.65             # rad/s
OCTANE_RELEASE_RESPONSIVENESS = 1.67
OCTANE_OVERSTEER = 7.71                 # degrees
OCTANE_COUNTERSTEER = 2.50              # degrees
OCTANE_BEST_SWITCH_AVG_TURN = 1.56
# Octane Center of Mass (Root Joint = Rotation Joint = "Center of Mass" = RJ = Pivot Point)
OCTANE_RJ_X_OFFSET = 13.88              # unreal units (uu)
OCTANE_RJ_Z_OFFSET = 20.75              # unreal units (uu)
OCTANE_GROUND_TO_RJ = 17.00             # unreal units (uu)
OCTANE_RJ_TO_FRONT = 72.88              # unreal units (uu)
OCTANE_RJ_TO_TOP = 38.83                # unreal units (uu)
OCTANE_RJ_TO_SIDE = 42.10               # unreal units (uu)
OCTANE_RJ_TO_BACK = 45.13               # unreal units (uu)
# Octane Dribbling (All Forces are Relative)
OCTANE_FORCE_FRONT_EDGE = 0.8820
OCTANE_FORCE_AT_40UU_SIDE = 0.9174
OCTANE_MAX_SIDE_FORCE = 1
OCTANE_FORCE_AT_SIDE_EDGE = 0.9136
OCTANE_MAX_VS_EDGE = 0.3500
OCTANE_FORCE_BACK_EDGE = 0.7711
# Octane Wheels
OCTANE_WHEEL_RADIUS_FRONT = 12.50       # unreal units (uu)
OCTANE_WHEEL_RADIUS_BACK =  15.00       # unreal units (uu)
OCTANE_FRONT_AXLE_X_OFFSET = 51.25      # unreal units (uu)
OCTANE_FRONT_AXLE_Y_OFFSET = 25.90      # unreal units (uu)
OCTANE_FRONT_AXLE_Z_OFFSET = -6.00      # unreal units (uu)
OCTANE_BACK_AXLE_X_OFFSET = -33.75      # unreal units (uu)
OCTANE_BACK_AXLE_Y_OFFSET = 29.50       # unreal units (uu)
OCTANE_BACK_AXLE_Z_OFFSET = -4.3        # unreal units (uu)
# Octane Spawning
OCTANE_MIN_SPAWN_HEIGHT = 17.01         # unreal units (uu)

# GOALS STATISTICS :
GOAL_HEIGHT = 642.775
GOAL_BACK_NET_Y = 6000  # +/-
# Center of goal on goal line
ORANGE_GOAL_CENTER = (0, BACK_WALL_Y, GOAL_HEIGHT / 2)
BLUE_GOAL_CENTER = (0, -BACK_WALL_Y, GOAL_HEIGHT / 2)
# Often more useful than center
ORANGE_GOAL_BACK = (0, GOAL_BACK_NET_Y, GOAL_HEIGHT / 2)
BLUE_GOAL_BACK = (0, -GOAL_BACK_NET_Y, GOAL_HEIGHT / 2)

# BOOSTS STATISTICS :
BOOST_LOCATIONS = (
    (0.0, -4240.0, 70.0),
    (-1792.0, -4184.0, 70.0),
    (1792.0, -4184.0, 70.0),
    (-3072.0, -4096.0, 73.0),
    (3072.0, -4096.0, 73.0),
    (- 940.0, -3308.0, 70.0),
    (940.0, -3308.0, 70.0),
    (0.0, -2816.0, 70.0),
    (-3584.0, -2484.0, 70.0),
    (3584.0, -2484.0, 70.0),
    (-1788.0, -2300.0, 70.0),
    (1788.0, -2300.0, 70.0),
    (-2048.0, -1036.0, 70.0),
    (0.0, -1024.0, 70.0),
    (2048.0, -1036.0, 70.0),
    (-3584.0, 0.0, 73.0),
    (-1024.0, 0.0, 70.0),
    (1024.0, 0.0, 70.0),
    (3584.0, 0.0, 73.0),
    (-2048.0, 1036.0, 70.0),
    (0.0, 1024.0, 70.0),
    (2048.0, 1036.0, 70.0),
    (-1788.0, 2300.0, 70.0),
    (1788.0, 2300.0, 70.0),
    (-3584.0, 2484.0, 70.0),
    (3584.0, 2484.0, 70.0),
    (0.0, 2816.0, 70.0),
    (- 940.0, 3310.0, 70.0),
    (940.0, 3308.0, 70.0),
    (-3072.0, 4096.0, 73.0),
    (3072.0, 4096.0, 73.0),
    (-1792.0, 4184.0, 70.0),
    (1792.0, 4184.0, 70.0),
    (0.0, 4240.0, 70.0),
)
