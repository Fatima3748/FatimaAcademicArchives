import tkinter as tk
from PIL import Image, ImageTk
import random
import time

class CardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Puzzle Game")
        
        # Load the images
        self.card_back_image = Image.open("./images/inverted_card.jpeg")
        self.card_back_image = ImageTk.PhotoImage(self.card_back_image)
        self.blank_image = Image.open("./images/blankCard.gif")
        self.blank_image = ImageTk.PhotoImage(self.blank_image)
        
        self.card_images = [ImageTk.PhotoImage(Image.open(f"./images/carte-{i}.gif")) for i in range(1, 9)]

        # Initialize game variables
        self.buttons = []
        self.images = self.card_images * 2
        self.exposed_buttons = []
        self.exposed_values = []
        self.score = 0
        self.wrong_matches = 0
        self.timer_started = False
        self.start_time = 0
        self.can_click = True
        
        # Timer label
        self.timer_label = tk.Label(self.root, text="Time: 0s", font=("Helvetica", 16))
        self.timer_label.grid(row=4, column=0, columnspan=4)

        # Score label
        self.score_label = tk.Label(self.root, text="Score: 0", font=("Helvetica", 16, "bold"), fg="red")
        self.score_label.grid(row=5, column=0, columnspan=2)

        # Wrong matches label
        self.wrong_matches_label = tk.Label(self.root, text="Wrong Matches: 0", font=("Helvetica", 16, "bold"), fg="blue")
        self.wrong_matches_label.grid(row=5, column=2, columnspan=2)

        # Initialize the game
        self.init_game()

    def init_game(self):
        self.shuffle_cards()
        self.draw_cards()

    def shuffle_cards(self):
        random.shuffle(self.images)

    def draw_cards(self):
        for row in range(4):
            button_row = []
            for col in range(4):
                button = tk.Button(self.root, image=self.card_back_image,
                                   command=lambda r=row, c=col: self.handleOnClick(r, c))
                button.grid(row=row, column=col, padx=5, pady=5)
                button_row.append(button)
            self.buttons.append(button_row)
    
    def handleOnClick(self, row, col):
        if not self.can_click or self.buttons[row][col]['state'] == 'disabled':
            return
        
        if not self.timer_started:
            self.start_timer()

        button = self.buttons[row][col]
        image = self.images[row * 4 + col]
        
        # Reveal the image on the button
        button.config(image=image)
        
        self.exposed_buttons.append((row, col))
        self.exposed_values.append(image)
        
        # Check if two cards are exposed
        if len(self.exposed_buttons) == 2:
            self.can_click = False
            self.root.after(1000, self.check_match)
    
    def check_match(self):
        if self.exposed_buttons[0] != self.exposed_buttons[1] and self.exposed_values[0] == self.exposed_values[1]:
            # Match found
            self.score += 1
            self.update_score()
            for row, col in self.exposed_buttons:
                button = self.buttons[row][col]
                button.config(image=self.blank_image, state='disabled')
        else:
            # No match, hide the images
            self.wrong_matches += 1
            self.update_wrong_matches()
            for row, col in self.exposed_buttons:
                button = self.buttons[row][col]
                button.config(image=self.card_back_image)
        
        # Reset exposed buttons and values
        self.exposed_buttons = []
        self.exposed_values = []
        self.can_click = True  # Allow clicking again

        # Check if all cards are matched
        if self.score == len(self.images) // 2:
            self.end_game()

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def update_wrong_matches(self):
        self.wrong_matches_label.config(text=f"Wrong Matches: {self.wrong_matches}")

    def start_timer(self):
        self.timer_started = True
        self.start_time = time.time()
        self.update_timer()
    
    def update_timer(self):
        if self.timer_started:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed_time}s")
            self.root.after(1000, self.update_timer)

    def end_game(self):
        self.timer_started = False
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')
        
        summary_label = tk.Label(self.root, text=f"Total Score: {self.score}\nTotal Wrong Matches: {self.wrong_matches}", font=("Helvetica", 20, "bold"))
        summary_label.grid(row=6, column=0, columnspan=4, pady=20)
        
        restart_button = tk.Button(self.root, text="Restart Game", command=self.restart_game)
        restart_button.grid(row=7, column=0, columnspan=4, pady=10)

    def restart_game(self):
        # Destroy the current root window and create a new one
        self.root.destroy()
        root = tk.Tk()
        game = CardGame(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    game = CardGame(root)
    root.mainloop()
