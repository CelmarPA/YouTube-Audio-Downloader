# main.py

from ui.app_window import AppWindow


if __name__ == '__main__':
    """
    Application entry point.

    Initializes the main application window and starts
    the Tkinter main event loop.
    """

    app: AppWindow = AppWindow()

    app.mainloop()
