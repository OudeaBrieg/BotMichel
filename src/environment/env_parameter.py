import random
random.seed(420)

def dist_2_ball_easy(GameState):
    print("dist_2_ball: EASY")
    #return between 0 and 1/3
    return random.uniform(0, 0.3)
def dist_2_ball_normal(GameState):
    print("dist_2_ball: NORMAL")
    #return between 1/3 and 2/3
    return random.uniform(0.3, 0.6)
def dist_2_ball_hard(GameState):
    print("dist_2_ball: HARD")
    #return between 2/3 and 1
    return random.uniform(0.6, 1)
def default_b():
    print("[ERROR] dist_2_ball: UNKNOWN DIFFICULTY")
distance_difficulty = {
    0 : dist_2_ball_easy,
    1 : dist_2_ball_normal,
    2 : dist_2_ball_hard
}
def check_if_on_wall(player_dist):
    return True
def dist_2_ball(difficulty, GameState):
    if not check_if_on_wall(player_dist):
        player_dist = distance_difficulty.get(difficulty, default_b)()
        #HERE: Chose random point on a circle of ray player_dist
        #HERE: Compute new GameState with player position modified
    return GameState

def car_yaw(difficulty, GameState):
    #player_rotation = rotation_difficulty.get(difficulty, default_b)()
    #HERE: Compute new GameState with player rotation modified
    return GameState

player_env_params= [(dist_2_ball, 0), (car_yaw, 0)]
def update_training_environment(GameState, player_env_params):
    for param_func, difficulty in player_env_params:
        GameState = param_func.get(difficulty, GameState, default_b)
    return GameState


    
    #if check_if_on_wall(player_dist)=False
        #player_pos_x and player_pos_y on player_dist circle
    #return player_pos

dist_2_ball(0)
    