from enum import Enum


class States(Enum):
    S_FREE = 0
    S_ENTER_AMOUNT = 1
    S_ENTER_COLOR = 2
    S_ENTER_ORIENTATION = 3
    S_SEND_PIC = 4


welcome_msg = ("""Welcome to the bot. It can generate and find images using your prompt. Give it a try describe any picture you want to receive""")
continue_msg = "Send next prompt or configure image search"
enter_number_msg = "Enter number of photos you want to receive"
enter_orientation_msg = "Now enter desired orientation (landscape, portrait)"
enter_color_msg = "Nice, now enter the main color of images"
enter_prompt_after_number_msg = "Yes! Now describe what pictures do you want"
incorrect_number_msg = "Incorrect number, try again"
