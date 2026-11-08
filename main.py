import sys
import pygame

from settings import W, H, SCALE, FPS
from assets import Assets
from game import Game
import ui


def main():
    pygame.init()
    window = pygame.display.set_mode((W * SCALE, H * SCALE))
    pygame.display.set_caption("Potion Brewing")
    canvas = pygame.Surface((W, H))
    clock = pygame.time.Clock()

    art = Assets()
    game = Game(art)

    while True:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                game.key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.click(event.pos[0] // SCALE, event.pos[1] // SCALE)

        game.update(dt)
        ui.draw(canvas, game, art)
        pygame.transform.scale(canvas, window.get_size(), window)
        pygame.display.flip()


if __name__ == "__main__":
    main()
