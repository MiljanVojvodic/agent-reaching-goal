import os
import sys
import traceback
import pygame
import config
from game import Game


def usage():
    print("Usage:")
    print("  python main.py [map_file] [AgentName]")
    print("Example:")
    print("  python main.py maps/map0.txt Example")


def main():
    try:
        pygame.init()

        map_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(config.MAP_FOLDER, "map0.txt")
        agent_name = sys.argv[2] if len(sys.argv) > 2 else "Example"

        g = Game(map_path=map_path, agent_name=agent_name)
        g.run()

    except Exception:
        traceback.print_exc()
        usage()
        input("Press Enter to exit...")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
