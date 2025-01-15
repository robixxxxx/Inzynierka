import pygame
import cv2

class VideoView:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.draw_functions = []
        self.telemetry_data = {}

    def render(self, frame):
        try:
            if frame is not None:
                width, height = self.screen.get_size()
                frame = cv2.resize(frame, (width, height))
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.screen.blit(frame_surface, (0, 0))

            for draw_function, args, kwargs in self.draw_functions:
                draw_function(self.screen, *args, **kwargs)

            # self._draw_telemetry_data()
            pygame.display.flip()
        except Exception as e:
            print(f"Error rendering frame: {e}")

    def stop(self):
        return