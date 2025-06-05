import pygame as pg 


def save_screen(screen: pg.surface.Surface, path: str) -> None:
    """Сохраняет экран приложения как изображение

    Args:
        screen (pg.surface.Surface): Экран приложения.
        path (str): Путь для сохранения снимка экрана.
    """
    pg.image.save(screen, path)    
