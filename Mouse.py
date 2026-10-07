"""Mouse Jiggler application entry point."""

from ui.app import MouseJigglerApp


def main() -> None:
    app = MouseJigglerApp()
    app.run()


if __name__ == "__main__":
    main()
