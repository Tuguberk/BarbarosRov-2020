import pygame
print("Joystick başladı")
kumanda_data = []

def kumanda():
    global kumanda_data
    pygame.init()

    done = False

    clock = pygame.time.Clock()


    pygame.joystick.init()


    while not done:
        kumanda_data = []
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop.

        # For each joystick:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        # Get the name from the OS for the controller/joystick.
        name = joystick.get_name()

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()

        for i in range(axes):
            axis = joystick.get_axis(i)
            kumanda_data.append(round(axis,2))

        buttons = joystick.get_numbuttons()

        for i in range(buttons):
            button = joystick.get_button(i)
            kumanda_data.append(button)

        #print(kumanda_data)
        clock.tick(30)
        

    pygame.quit()



if __name__ == "__main__":
    kumanda()
    
