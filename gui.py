import tkinter as tk

import client as client

class LoginScreen(tk.Frame):
    def __init__(self, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller  # Store a reference to the controller

        # Create a label and entry for the host
        tk.Label(self, text="Host").grid(row=0, column=0)
        self.host_entry = tk.Entry(self)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1)

        # Create a label and entry for the username
        tk.Label(self, text="Username").grid(row=1, column=0)
        self.username_entry = tk.Entry(self)
        self.username_entry.insert(0, "Anonymous")
        self.username_entry.grid(row=1, column=1)

        # Create a login button
        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, sticky="e")

    # This method is called when the login button is pressed
    def login(self):
        try:
            host = self.host_entry.get()
            username = self.username_entry.get()
        except Exception as e:
            print(e)
        self.controller.show_chat_screen(host, 1234, username)

class ChatScreen(tk.Frame):
    def __init__(self, controller):
        tk.Frame.__init__(self, controller)
        self.controller = controller  # Store a reference to the controller
        self.grid()
        controller.title("Chat App")
        controller.geometry("400x500")
        controller.configure(bg="white")

        # Make the window resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create a frame for the chat window
        self.chat_frame = tk.Frame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self.chat_frame.rowconfigure(0, weight=1)
        self.chat_frame.columnconfigure(0, weight=1)

        # Create a text widget for the chat
        self.chat = tk.Text(self.chat_frame, state="disabled", bg="lightgrey")
        self.chat.grid(row=0, column=0, sticky="nsew")

        # Create a scrollbar for the chat
        self.scrollbar = tk.Scrollbar(self.chat_frame)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Attach the scrollbar to the chat
        self.chat.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.chat.yview)

        # Create a frame for the message window
        self.message_frame = tk.Frame(self)
        self.message_frame.grid(row=1, column=0, sticky="ew")
        self.message_frame.rowconfigure(0, weight=1)
        self.message_frame.columnconfigure(0, weight=1)

        # Create an input field with limited size
        self.input_field = tk.Text(self.message_frame, height=4, width=40)
        self.input_field.grid(row=0, column=0, sticky="ew")

        # Create a send button
        self.send_button = tk.Button(self.message_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, sticky="ew")

    def send_message(self):
        message = self.input_field.get("1.0", "end-1c")
        self.input_field.delete("1.0", "end-1c")
        self.controller.client.send_to_server(message)

class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.show_login_screen()

        self.client = None
        self.chat_screen = None

        # Make the window resizable
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

#       self.bind('<Configure>', self.on_resize)
    def on_resize(self, event):
        width = self.winfo_width()
        height = self.winfo_height()
        print(f"Width: {width}, Height: {height}")

    def show_login_screen(self):
        new_frame = LoginScreen(self)
        self._switch_frame(new_frame)

    def show_chat_screen(self, IP, PORT, USERNAME):
        self.chat_screen = ChatScreen(self)
        self._switch_frame(self.chat_screen)
        self.client = client.Client(IP, PORT, USERNAME, self.chat_screen)  # Pass chat_screen as the gui_controller

    def _switch_frame(self, new_frame):
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
