from panda_interface import PandaInterface
from ui import App

def main():
    panda = PandaInterface()
    panda.connect()

    app = App(panda)
    app.run()

if __name__ == "__main__":
    main()
