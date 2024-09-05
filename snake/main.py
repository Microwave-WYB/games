import asyncio
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import pygame


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class SnakeGameState:
    board_size: tuple[int, int] = (20, 20)
    gameover: bool = False
    snake: list[tuple[int, int]] = field(default_factory=lambda: [(10, 10), (10, 11), (10, 12)])
    food: tuple[int, int] = field(
        default_factory=lambda: (random.randint(0, 19), random.randint(0, 19))
    )
    score: int = 0
    direction: Direction = Direction.RIGHT


class SnakeGameModel:
    def __init__(self, state: Optional[SnakeGameState] = None):
        self.state = state or SnakeGameState()

    def __iter__(self):
        while not self.state.gameover:
            yield self.state
            self.state = self.get_next_state(self.state)
        yield self.state  # Yield the final (game over) state

    def get_next_state(self, state: SnakeGameState) -> SnakeGameState:
        new_state = SnakeGameState(**state.__dict__)  # Create a copy of the current state

        # Calculate new head position
        head_x, head_y = new_state.snake[0]
        dx, dy = new_state.direction.value
        new_head = (
            (head_x + dx) % new_state.board_size[0],
            (head_y + dy) % new_state.board_size[1],
        )

        # Check for collision with self
        if new_head in new_state.snake[1:]:
            new_state.gameover = True
            return new_state

        # Move snake
        new_state.snake.insert(0, new_head)

        # Check for food
        if new_head == new_state.food:
            new_state.score += 1
            # Generate new food
            while True:
                new_food = (
                    random.randint(0, new_state.board_size[0] - 1),
                    random.randint(0, new_state.board_size[1] - 1),
                )
                if new_food not in new_state.snake:
                    new_state.food = new_food
                    break
        else:
            new_state.snake.pop()  # Remove tail if no food eaten

        return new_state

    def change_direction(self, new_direction: Direction):
        if (
            new_direction.value[0] + self.state.direction.value[0] != 0
            or new_direction.value[1] + self.state.direction.value[1] != 0
        ):
            self.state.direction = new_direction


class SnakeGameView:
    def __init__(self, state: SnakeGameState, cell_size: int = 20):
        self.cell_size = cell_size
        pygame.init()
        self.screen = pygame.display.set_mode(
            (state.board_size[0] * cell_size, state.board_size[1] * cell_size)
        )
        pygame.display.set_caption("Snake Game")

    def draw(self, state: SnakeGameState):
        self.screen.fill((0, 0, 0))  # Fill screen with black

        # Draw snake
        for segment in state.snake:
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),
                (
                    segment[0] * self.cell_size,
                    segment[1] * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                ),
            )

        # Draw food
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (
                state.food[0] * self.cell_size,
                state.food[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
        )

        pygame.display.flip()


class SnakeGameController:
    def __init__(self, model: SnakeGameModel, view: SnakeGameView):
        self.model = model
        self.view = view
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.model.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.model.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.model.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.model.change_direction(Direction.RIGHT)

    async def run_game(self):
        clock = pygame.time.Clock()
        state = SnakeGameState()
        for state in self.model:
            self.handle_events()
            if not self.running:
                break
            self.view.draw(state)
            clock.tick(10)  # Control game speed
            await asyncio.sleep(0)  # very important for pygbag to work
        print(f"Game Over. Final Score: {state.score}")


async def main():
    model = SnakeGameModel()
    view = SnakeGameView(model.state)
    controller = SnakeGameController(model, view)
    await controller.run_game()


asyncio.run(main())
