# env/rendering.py

import pygame
import os


class Renderer:
    def __init__(self, map_data, cell_size=80):
        self.map_data = map_data
        self.cell_size = cell_size

        self.screen = None
        self.images = {}
        self.font = None

        self._loader = _AssetLoader(cell_size)

    def initialize(self):
        if not pygame.get_init():
            pygame.init()

        if not pygame.font.get_init():
            pygame.font.init()

        rows, cols = self.map_data.grid.shape

        self.screen = pygame.display.set_mode(
            (cols * self.cell_size, rows * self.cell_size + 50)
        )

        # safe now
        self.images = self._loader.load_assets()
        self.font = self._loader.load_font()

    def draw(self, state):
        self.screen.fill((0, 0, 0))

        rows, cols = self.map_data.grid.shape

        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    c * self.cell_size,
                    r * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                # pygame.draw.rect(self.screen, (91, 120, 166), rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect)

                if "snow" in self.images:
                    img = self.images["snow"]
                    img = pygame.transform.scale(img, (1.05 * self.cell_size, 1.05 * self.cell_size))
                    x = (c+1.05) * self.cell_size - img.get_width()
                    y = (r+1.05) * self.cell_size - img.get_height()
                    #
                    # self.screen.blit(img, (x, y))
                    # self.screen.blit(self.images["snow"], rect)
                    # img = self.images["snow"]
                    # x = (c) + 2  # Shift right by 2 pixels
                    # y = (r) - 3  # Shift up by 3 pixels
                    self.screen.blit(img, (x, y))

                if (r, c) in self.map_data.crate_positions:
                    self.screen.blit(self.images["crate"], rect)

                if (r, c) in self.map_data.ice_positions:
                    self.screen.blit(self.images["ice"], rect)

                if (
                    self.map_data.weapon_pos
                    and (r, c) == self.map_data.weapon_pos
                    and not state.has_weapon()
                ):
                    self.screen.blit(self.images["weapon"], rect)

                if (r, c) in state.get_targets_positions():
                    self.screen.blit(self.images["target"], rect)

                if (
                    state.is_enemy_alive()
                    and state.get_enemy_position() == (r, c)
                ):
                    self.screen.blit(self.images["enemy"], rect)

                if state.get_agent_position() == (r, c):
                    self.screen.blit(self.images["agent"], rect)

        self._draw_hud(state)
        pygame.display.flip()

    def _draw_hud(self, state):
        rows, cols = self.map_data.grid.shape
        hud_y = rows * self.cell_size

        pygame.draw.rect(
            self.screen,
            (40, 97, 120),
            (0, hud_y, cols * self.cell_size, 50)
        )

        if self.font:
            txt = self.font.render(
                f"Steps: {state.get_step_count()} | Remaining Targets: {len(state.get_targets_positions())}",
                True,
                (255, 255, 255)
            )
            self.screen.blit(txt, (10, hud_y + 10))

    def show_results(self, score, expanded_nodes, step_count, cost):
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pygame.display.flip()
        
        print(f"Final Score: {score}")
        print(f"Cost: {cost}")
        print(f"Expanded Nodes: {expanded_nodes}")
        print(f"Steps Taken: {step_count}")
        print("=" * 40)



class _AssetLoader:
    ICON_PATH = "env/src/icons/"

    SCALE_MULTIPLIERS = {
        "snow": 1.2,
        "crate": 1,
        "ice": 1,
        "target": 1,
        "weapon": 1.0,
        "agent": 1.0,
        "enemy": 1.0
    }

    FILES = {
        "snow": "Sum.png",
        "crate": "crate.png",
        "ice": "ice_box.png",
        "target": "dragon_glass.png",
        "agent": "arya.png",
        "enemy": "night_king.png",
        "weapon": "dagger.png"
    }

    def __init__(self, cell_size):
        self.cell_size = cell_size

    def load_assets(self):
        assets = {}

        for name, file in self.FILES.items():
            path = os.path.join(self.ICON_PATH, file)

            if not os.path.exists(path):
                print(f"Warning: missing {path}")
                continue

            image = pygame.image.load(path)

            scale = self.SCALE_MULTIPLIERS.get(name, 1.0)

            assets[name] = pygame.transform.scale(
                image,
                (self.cell_size, int(self.cell_size * scale))
            )

        return assets

    def load_font(self, size=24):
        if not pygame.font.get_init():
            pygame.font.init()

        return pygame.font.Font(None, size)