"""
The program implements a snake game.
* Module:
	- turtle: a module for drawing the elements of the game.
	- random: a module for generating random numbers to place food and monster,
			  as well as to determine the speed of the monster.
	- time: a module for calculating the time of the game.
	- functools: a module for using partial function to combine functions.
* Structure:
	- Modules
	- Settings:
		- color: a dictionary for storing the colors of the elements.
		- dir: a dictionary for storing the directions of the snake.
		- font: a dictionary for storing the fonts of the hints.
	- Global variables
	- Functions Groups:
		- Game statistics
		- Game setups
		- Game controlloings
		- Game ending
	- Main function
* User Interface:
	- The game board is a 500x500 square, divided into 25x25 grids.
	- The snake is a blue line with a red head.
	- The monster is a pink square.
	- The food is numbers representing the extra length of the snake.
	- The game starts when the user clicks anywhere on the game board.
	- The user can control the snake by pressing the arrow keys.
	- The game ends when the snake hits the monster or eat all the food.
* Program Information:
	- CSC1002 Assignment 3
	- Author: frankchenfu
	- Last Modified: 2023-04-15
	- Language: Python 3.6.8
    - Standard: PEP 8
"""

# Modules
import turtle
import random
from time import time
from functools import partial

# Settings
color = {
    "head": ("#ff0000", "#ff0000"),
    "dead": ("#ffa500", "#ffa500"),
    "body": ("#0000ff", "#00008b"),
    "monster": ("#ff00ff", "#ff00ff"),
    "g_status": "#000000"
}
dir = {
    "Up": (90, 0, 1),
    "Down": (270, 0, -1),
    "Left": (180, -1, 0),
    "Right": (0, 1, 0)
}
font = {
    "Status": ("Arial", 16, "bold"),
    "Intro": ("Arial", 16, "normal"),
    "Food": ("Arial", 14, "bold")
}

# Global variables (Game statistics)
g_contact = 0
g_initime = 0
g_direction = None
g_paused = False
g_game_over = False
g_snake_pos = None
g_monster_pos = None
g_snake = []
g_len = 5
g_food = []
g_food_map = [[-1 for i in range(25)] for j in range(25)]

# Global variables (Game setups)
g_head = turtle.Turtle()
g_monster = turtle.Turtle()
g_status = turtle.Turtle()
g_screen = turtle.Screen()

# The following 9 functions are for game statistic basics.
"""
Return the status of the game.
@return:
	a string of the status of the game.
"""
def get_status() -> str:
    if g_direction is None:
        return "Contact: %d    Time: %d    Motion: %s" % \
            (g_contact, time() - g_initime, "Wait for start")
    return "Contact: %d    Time: %d    Motion: %s" % \
        (g_contact, time() - g_initime, "Paused" if g_paused else g_direction)

"""
Return the real coordinate of the snake.
@param row:
	the row of the snake on the grid.
@param col:
	the column of the snake on the grid.
@return:
	a tuple of the real coordinate of the snake.
"""
def get_snake(row, col) -> tuple:
    return row * 20 - 240, col * 20 - 280

"""
Return the real coordinate of the monster.
@param row:
	the row of the monster on the grid.
@param col:
	the column of the monster on the grid.
@return:
	a tuple of the real coordinate of the monster.
"""
def get_monster(row, col) -> tuple:
    return row * 20 - 230, col * 20 - 270

"""
Return the real coordinate of the food.
@param row:
	the row of the food on the grid.
@param col:
	the column of the food on the grid.
@return:
	a tuple of the real coordinate of the food.
"""
def get_food(row, col) -> tuple:
    return row * 20 - 240, col * 20 - 292

"""
Check whether the snake hits the wall or itself.
@param row:
	the row of the snake on the grid.
@param col:
	the column of the snake on the grid.
@return:
	<False> for the snake hits the wall or itself.
	<True> for the snake is safe.
"""
def check_snake(row, col) -> bool:
    return 0 <= row <= 24 and 0 <= col <= 24 and (row, col) not in g_snake

"""
Check whether the monster is in the game board.
@param row:
	the row of the monster on the grid.
@param col:
	the column of the monster on the grid.
@return:
	<False> for the monster is out of the game board.
	<True> for the monster is in the game board.
"""
def check_monster(row, col) -> bool:
    return 0 <= row <= 23 and 0 <= col <= 23

"""
Check whether the snake can eat the food.
@param row:
	the row of the food on the grid.
@param col:
	the column of the food on the grid.
@return:
	None
"""
def check_food(row, col) -> None:
    global g_food_map, g_food, g_len
    if g_food_map[row][col] != -1:
        g_len += g_food_map[row][col] + 1
        g_food[g_food_map[row][col]]["Eaten"] = True
        g_food[g_food_map[row][col]]["Visible"] = False
        g_food[g_food_map[row][col]]["Object"].clear()
        g_food_map[row][col] = -1

"""
Check whether the monster contacts the snake's body.
If so, add <g_contact> by 1.
@return:
	None
"""
def check_contact() -> None:
    global g_contact
    checklist = []
    checklist.append((g_monster_pos[0] + 1, g_monster_pos[1] + 1))
    checklist.append((g_monster_pos[0] + 1, g_monster_pos[1]))
    checklist.append((g_monster_pos[0], g_monster_pos[1] + 1))
    checklist.append((g_monster_pos[0], g_monster_pos[1]))
    for pos in g_snake:
        if pos in checklist:
            g_contact += 1
            return

"""
Check whether the snake is dead.
If so, call <game_over> to end the game.
@return:
	None
"""
def check_dead() -> None:
    global g_contact
    checklist = []
    checklist.append((g_monster_pos[0] + 1, g_monster_pos[1] + 1))
    checklist.append((g_monster_pos[0] + 1, g_monster_pos[1]))
    checklist.append((g_monster_pos[0], g_monster_pos[1] + 1))
    checklist.append((g_monster_pos[0], g_monster_pos[1]))
    if g_snake_pos in checklist:
        game_over(False)


# The following 6 functions are for game setups.
"""
Setup the whole game.
The basic elements (board, snake, monster, food) are set up separately.
@return:
	None
"""
def setup() -> None:
    g_screen.setup(580, 660)  # (500+40*2, 500+80+40*2)
    g_screen.title("Snake")  # Set the title of the game
    g_screen.tracer(0)  # Disable the animation
    setup_gameboard()
    setup_elements()
    g_status.penup()
    g_status.hideturtle()
    g_status.goto(-220, 250)  # Set the initial status board
    g_status.write("Contact: 0    Time: 0    Motion: Wait for start",
                   font=font["Status"], align="left")
    g_status.goto(0, 180 if g_monster_pos[1] < 12 else -180)
    g_status.write("Welcome to the Snake Game!",
                   font=font["Intro"], align="center")
    g_status.goto(0, 160 if g_monster_pos[1] < 12 else -160)
    g_status.write("Click anywhere to start the game...",
                   font=font["Intro"], align="center")
    g_status.goto(-220, 250)
    g_screen.update()
    g_screen.onclick(setup_game)

"""
Setup the snake and monster.
@return:
	None
"""
def setup_elements() -> None:
    global g_snake_pos, g_monster_pos
    g_head.shape("square")
    g_head.color(*color["head"])
    g_head.penup()
    g_snake_pos = (12, 12)  # The initial position of the snake
    g_head.goto(get_snake(12, 12))
    g_monster.shape("square")
    g_monster.color(*color["monster"])
    g_monster.penup()
    posx = random.randint(0, 23)  # The initial position of the monster
    posy = random.randint(0, 23)
    while abs(posx - 12) + abs(posy - 12) < 12:  # Far enough from the snake
        posx = random.randint(0, 23)
        posy = random.randint(0, 23)
    g_monster_pos = (posx, posy)
    g_monster.goto(get_monster(posx, posy))

"""
Setup the game board.
@return:
	None
"""
def setup_gameboard() -> None:
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.color(color["g_status"])
    pen.pensize(3)
    pen.penup()
    pen.goto(-251, 211)
    pen.pendown()
    pen.setheading(dir["Up"][0])  # Draw the status board
    pen.forward(80)
    pen.setheading(dir["Right"][0])
    pen.forward(503)
    pen.setheading(dir["Down"][0])
    pen.forward(80)
    pen.setheading(dir["Left"][0])
    pen.forward(503)
    pen.setheading(dir["Down"][0])  # Draw the game board
    pen.forward(503)
    pen.setheading(dir["Right"][0])
    pen.forward(503)
    pen.setheading(dir["Up"][0])
    pen.forward(503)
    pen.penup()

"""
Setup the food with distinct positions.
@return:
	None
"""
def setup_food() -> None:
    global g_food_map, g_food
    pos = []
    while len(pos) < 5:
        posx = random.randint(0, 24)
        posy = random.randint(0, 24)
        if (posx, posy) not in pos + [g_snake_pos, g_monster_pos]:
            pos.append((posx, posy))  # Distinct positions
        g_food_map[posx][posy] = len(pos) - 1
        g_food.append({  # The food information
            "Object": turtle.Turtle(),
            "Position": (posx, posy),
            "Eaten": False,
            "Visible": True
        })
    for i in range(5):  # Draw the food
        g_food[i]["Object"].hideturtle()
        g_food[i]["Object"].penup()
        g_food[i]["Object"].goto(get_food(*g_food[i]["Position"]))
        g_food[i]["Object"].write(i + 1, font=font["Food"], align="center")

"""
Start the game.
@param x, y:
	None
@return:
	None
"""
def setup_game(x, y) -> None:
    setup_food()
    global g_initime
    g_initime = time()  # Start the timer
    g_status.clear()
    g_screen.onclick(None)  # Disable the click event
    g_screen.onkey(partial(set_direction, "Up"), "Up")  # Set the key operation
    g_screen.onkey(partial(set_direction, "Down"), "Down")
    g_screen.onkey(partial(set_direction, "Left"), "Left")
    g_screen.onkey(partial(set_direction, "Right"), "Right")
    g_screen.onkey(partial(set_direction, "Paused"), "space")
    g_screen.ontimer(move_snake, 200)
    g_screen.ontimer(move_monster, random.randint(250, 350))
    g_screen.ontimer(hide_food, 5000)
    setup_timer()  # Refresh the timer every second

"""
Refresh the timer every second.
@return:
	None
"""
def setup_timer() -> None:
    if g_game_over:
        return
    g_status.clear()
    g_status.write(get_status(), font=font["Status"], align="left")
    g_screen.ontimer(setup_timer, 1000)


# The following 4 functions are used to operate the snake and monster
"""
Set the direction of the snake.
@param direction:
	The direction of the snake in string.
@return:
	None
"""
def set_direction(direction) -> None:
    global g_direction, g_paused
    if direction != "Paused":
        g_direction = direction
        g_paused = False  # Unpause if any key is pressed
    else:
        g_paused = not g_paused
    g_status.clear()
    g_status.write(get_status(), font=font["Status"], align="left")

"""
Move the snake.
Every time it try to move towards, but before it actually moves,
it will check if the snake is going to hit itself or the wall.
If so, it will do nothing and wait for the next move.
@return:
	None
"""
def move_snake() -> None:
    if g_game_over:
        return
    if g_paused or g_direction is None:
        g_screen.ontimer(move_snake, 200)
        return
    global g_snake_pos, g_len
    attempt = (g_snake_pos[0] + dir[g_direction][1],
               g_snake_pos[1] + dir[g_direction][2])
    if not check_snake(*attempt):
        g_screen.ontimer(move_snake, 200)
        return
    g_snake_pos = attempt
    g_snake.append(g_snake_pos)
    g_head.color(*color["body"])
    g_head.stamp()  # Duplicate the snake head
    g_head.color(*color["head"])
    g_head.setheading(dir[g_direction][0])
    g_head.forward(20)  # Move the snake head
    check_dead()  # Check if the snake is dead
    if len(g_snake) > g_len:
        g_snake.pop(0)
        g_head.clearstamps(1)
        g_screen.update()
        g_screen.ontimer(move_snake, 200)
    else:  # If the snake is not fully extended
        g_screen.update()
        if len(g_snake) == 20:  # If the snake reaches it maximum length
            game_over(True)
            return
        g_screen.ontimer(move_snake, 300)  # The snake will move slower
    check_food(g_snake_pos[0], g_snake_pos[1])  # Check if the snake eats food

"""
Move the monster.
It will always move towards the snake head, and count the number of contracts.
The speed will
"""
def move_monster():
    if g_game_over:
        return
    global g_monster_pos
    attempt: tuple[int, int]
    s_posx, s_posy = get_snake(*g_snake_pos)
    m_posx, m_posy = get_monster(*g_monster_pos)
    # Check whether it should move horizontally or vertically
    if abs(s_posx - m_posx) > abs(s_posy - m_posy):
        if m_posx > s_posx:
            attempt = (g_monster_pos[0] - 1, g_monster_pos[1])
        else:
            attempt = (g_monster_pos[0] + 1, g_monster_pos[1])
    else:
        if m_posy > s_posy:
            attempt = (g_monster_pos[0], g_monster_pos[1] - 1)
        else:
            attempt = (g_monster_pos[0], g_monster_pos[1] + 1)
    if not check_monster(*attempt):
        g_screen.ontimer(move_monster, random.randint(250, 350))
        return
    g_monster_pos = attempt
    g_monster.goto(get_monster(*attempt))
    check_contact()
    check_dead()  # Check if the snake is dead
    if g_game_over:
        return
    g_status.clear()
    g_status.write(get_status(), font=font["Status"], align="left")
    g_screen.update()
    g_screen.ontimer(move_monster, random.randint(280, 380))

"""
Hide or unhide the food every a few seconds.
Randomly choose a food that is not eaten and hide or unhide it.
@return:
	None
"""
def hide_food() -> None:
    if g_game_over:
        return
    u = [i for i in range(5) if not g_food[i]["Eaten"]]
    if len(u) == 0:
        return
    u = random.choice(u)
    if g_food[u]["Visible"]:
        g_food[u]["Visible"] = False
        g_food[u]["Object"].clear()
        g_food_map[g_food[u]["Position"][0]][g_food[u]["Position"][1]] = -1
    else:
        g_food[u]["Visible"] = True
        g_food[u]["Object"].write(u + 1, font=font["Food"], align="center")
        g_food_map[g_food[u]["Position"][0]][g_food[u]["Position"][1]] = u
    check_food(g_snake_pos[0], g_snake_pos[1])
    g_screen.update()
    g_screen.ontimer(hide_food, random.randint(5000, 10000))


# The function that will be called when the game is over
"""
End the game and stop all the functions.
@param win:
	<True> for winning the game,
	<False> for losing the game.
@return:
	None
"""
def game_over(win: bool = False) -> None:
    global g_game_over, g_direction
    g_game_over = True
    if not win:
        g_head.color(*color["dead"])
        # For convenience, adjust the position of the text
        if g_monster_pos[0] > 12:
            g_monster.write("Game Over!    ", font=font["Food"], align="right")
        else:
            g_monster.write("    Game Over!", font=font["Food"], align="left")
    else:
        # For convenience, adjust the position of the text
        if g_snake_pos[0] > 12:
            g_head.write("Winner!    ", font=font["Food"], align="right")
        else:
            g_head.write("    Winner!", font=font["Food"], align="left")
    g_screen.onkey(None, "Up")  # Disable all the keys
    g_screen.onkey(None, "Down")
    g_screen.onkey(None, "Left")
    g_screen.onkey(None, "Right")
    g_screen.onkey(None, "space")
    g_status.goto(-220, 220)
    g_status.write(
        "You %s Click anywhere to quit." % ("win!" if win else "lose."),
        font=font["Status"], align="left")
    g_screen.update()

    # Quit the game when the user clicks the screen
    g_screen.onclick(lambda x, y: g_screen.bye())


# The main function
if __name__ == "__main__":
    setup()
    g_screen.listen()
    g_screen.mainloop()