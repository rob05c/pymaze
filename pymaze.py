#from sys import argv
#from enum import Enum
#from random import seed
#from random import randint
import sys
import enum
import random
import time

class SpaceType(enum.Enum):
    Open = 0
    Wall = 1


MAZE_PERCENT_FILL = 10
    
def gen_maze(height, width, rand_seed, fill_percent):
    """ generate a new maze.

    Takes the length, width, and a random seed.

    """

    random.seed(rand_seed)
    
    # TODO add flag whether to include borders or not
    #      (is it a closed dungeon, or a maze with exits?)

    # TODO write a deterministic easy-to-understand random generator
    # (e.g. just using sha512 on the seed, and incrementing every call)
    # To make the generation portable. So it's sane to rewrite in a different language to generate the same mazes
    
    # we start with a maze of all walls
    
    maze = [ ]
    for x in range(width):
        maze.append([ ])
        for y in range(height):
            maze[x].append(SpaceType.Wall)

    pos_x = random.randint(0, width-1)
    pos_y = random.randint(0, height-1)

    # create an open space to start in

    #print(f"DEBUG height {height} width {width} start pos_x {pos_x} start pos_y {pos_y}")

    
    maze[pos_x][pos_y] = SpaceType.Open

    # cache (memoize) the fill percent, because it's expensive to compute every time. As in, seconds.
    maze_fill = 1 # we just made 1 open space

    # and then generate paths though the maze

    direction = PathDir(random.randint(0, len(PathDir)-1))

    #print(f"DEBUG start direction: {direction}")

    maze_size = width * height
    
    total_perc_time = 0
    while True:
        (maze, pos_x, pos_y, direction, maze_fill) = gen_path(maze, pos_x, pos_y, direction, maze_fill)

        start = time.process_time()
        total_perc_time += time.process_time() - start

        percent_full = float(maze_fill) / float(maze_size) * 100
        
        #print(f"DEBUG maze percent full: {percent_full}")
        if percent_full >= fill_percent:
            print(f"get_maze_percent_full time: {total_perc_time}")
            return maze

        
class PathAction(enum.Enum):
    """ actions the generator can take """
    Stop = 0
    Fork = 1
    Continue = 2
    ChangeDir = 3
    MakeRoom = 4
    
class PathDir(enum.Enum):
    """ the vector of an ongoing path being generated """
    Left = 0
    Right = 1
    Up = 2
    Down = 3

def get_action_odds():
    """ returns the odds of different actions when a path is being generated 
    
    The odds are relative to each-other. That is, if Stop is 1, Fork is 5, Continue is 2,
    then there's a 1/8 chance of stopping.

    """
    
    return {
        PathAction.Stop: 0,
        PathAction.Fork: 0,
        PathAction.Continue: 15,
        PathAction.ChangeDir: 5,
        PathAction.MakeRoom: 0,
    }


def get_next_action():
    """ gets the next action to perform, based on get_action_odds """
    
    action_odds = get_action_odds()
    #print(f"DEBUG action_odds {action_odds}")

    # get the sum of all the action odds values
    total = 0
    for action in action_odds:
        #print(f"DEBUG get_next_action total {total} adding action {action} odds {action_odds[action]}")
        total += action_odds[action]
        #print(f"DEBUG get_next_action total now {total}")

    # get a random number from 1..sum
    val = random.randint(1,total)

    #print(f"DEBUG get_next_action val {val} is 1..{total}")
    
    # now, check if the value is <= the first action.
    # If so, use that. If not, reduce the sum by that number, and check the next action.
    for action in action_odds:
        odds = action_odds[action]
        if val <= odds:
            return action
        val -= odds

    raise Exception("random action was greater than sum of odds, this shouldn't be possible")
    
def get_maze_percent_full(maze):
    """ returns the percentage of the maze that's open space, versus walls.

    This is incredibly inefficient. It could easily be made more efficient by
    storing a variable every time an open space is added, if necessary.

    """

    if len(maze) == 0:
        return 0 # TODO throw? This isn't normal, and probably needs an error or warning

    width = len(maze)
    height = len(maze[0])

    totalSpace = width*height
    emptySpace = 0

    for x in range(len(maze)):
        for y in range(len(maze[0])):
            if maze[x][y] == SpaceType.Open:
                emptySpace += 1
    return float(emptySpace) / float(totalSpace) * 100


def gen_path(maze, pos_x, pos_y, direction, maze_fill):
    """ generate a path through the maze.

    Generates the next step of a path.
    It's the caller's responsibility to decide when to stop generating steps.

    Returns the new maze, and the current direction

    """

    # TODO should hitting a wall change direction or do another action instead of stopping?

    #print(f"DEBUG gen_path: {pos_x} {pos_y} {direction}")

    # TODO abstract, reduce duplication

    # TODO remove Stop action, since gen_path is no longer recursive
    
    action = get_next_action()
    #print(f"DEBUG gen_path: {action}")
    if action == PathAction.Stop:
        return (maze, pos_x, pos_y, direction, maze_fill)
    elif action == PathAction.Continue:
        #print(f"DEBUG gen_path: continuing direction {direction}")
        # todo put in a function
        if direction == PathDir.Left:
            #print(f"DEBUG gen_path: continue: left")
            if pos_x == 0:
                #print(f"DEBUG gen_path: continue: left: hit a wall")
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction) # hit a wall, try something else
            else:
                #print(f"DEBUG gen_path: continue: left: no wall")
                pos_x -= 1
                if maze[pos_x][pos_y] != SpaceType.Open:
                    maze_fill += 1
                maze[pos_x][pos_y] = SpaceType.Open
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction)
        elif direction == PathDir.Right:
            #print(f"DEBUG gen_path: continue: right")
            if pos_x == len(maze)-1:
                #print(f"DEBUG gen_path: continue: right: hit a wall")
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction) # hit a wall, try something else
            else:
                #print(f"DEBUG gen_path: continue: right: no wall")
                pos_x += 1
                if maze[pos_x][pos_y] != SpaceType.Open:
                    maze_fill += 1                
                maze[pos_x][pos_y] = SpaceType.Open
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction)
        elif direction == PathDir.Up:
            #print(f"DEBUG gen_path: continue: up")
            if pos_y == 0:
                #print(f"DEBUG gen_path: continue: up: wall")
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction) # hit a wall, try something else
            else:
                #print(f"DEBUG gen_path: continue: up: no wall")
                pos_y -= 1
                if maze[pos_x][pos_y] != SpaceType.Open:
                    maze_fill += 1                
                maze[pos_x][pos_y] = SpaceType.Open
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction)
        elif direction == PathDir.Down:
            if pos_y == len(maze[pos_x])-1:
                #print(f"DEBUG gen_path: continue: down: wall")
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction) # hit a wall, try something else
            else:
                #print(f"DEBUG gen_path: continue: down: no wall")
                pos_y += 1
                if maze[pos_x][pos_y] != SpaceType.Open:
                    maze_fill += 1                
                maze[pos_x][pos_y] = SpaceType.Open
                return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, direction)
        else:
            raise Exception(f"unknown direction {direction}")
    elif action == PathAction.Fork:
        return (maze, pos_x, pos_y, direction, maze_fill) # TODO implement
    elif action == PathAction.ChangeDir:
        direction = PathDir(random.randint(0, len(PathDir)-1))
        return (maze, pos_x, pos_y, direction, maze_fill) # gen_path(maze, pos_x, pos_y, new_dir)
    elif action == PathAction.MakeRoom:
        return (maze, pos_x, pos_y, direction, maze_fill) # TODO implement
    raise Exception(f"unknown action {action}")

def maze_str(maze):
    """ returns a visual representation of the maze as a string

    Designed to be printed to the screen

    """

    str = ""
    
    # TODO make a dict/func with characters, so it's easy to change the look
    # TODO these are backwards, change maze to [y][x]
    for x in range(len(maze)):
        for y in range(len(maze[x])):
            if maze[x][y] == SpaceType.Open:
                str += " "
            elif maze[x][y] == SpaceType.Wall:
                str += "#"
            else:
                raise Exception(f"unknown action {action}")
        str += "\n"
        
    return str


def main():
    if len(sys.argv) < 3:
        print ("usage: python3 pymaze.py width height [seed] [fill_percent]")
        return

    width_s = sys.argv[1]
    height_s = sys.argv[2]

    if not width_s.isdigit() or not height_s.isdigit():
        print ("width and height must be integers")

    width = int(width_s)
    height = int(height_s)

    maze_seed = random.randint(0,999999)
    if len(sys.argv) >= 4:
        maze_seed = sys.argv[3]

    fill_perc = MAZE_PERCENT_FILL
    if len(sys.argv) >= 5:
        fill_perc = int(sys.argv[4])


    print(f"""width: {width}
height: {height}
seed: {maze_seed}
fill: {fill_perc}%
""")

    # # debug
    # for i in range(10):
    #     action = get_next_action()
    #     print(f"got action: {action}")

    # todo make argument

    start = time.process_time()
    maze = gen_maze(height, width, maze_seed, fill_perc)
    gen_maze_time = time.process_time() - start
    print(f"gen_maze time: {gen_maze_time}")

    print(maze_str(maze))
    print("printed maze")
        
if __name__ == "__main__":
    main()
