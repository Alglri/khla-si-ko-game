from __future__ import annotations

import math
from array import array
from pathlib import Path

try:
    import pygame
except ImportError: 
    pygame = None


_SOUND_NOTES = {
    "countdown": ((660,), 0.12),
    "gesture": ((880, 1175), 0.12),
    "win": ((523, 659, 784), 0.45),
    "lose": ((392, 330, 262), 0.5),
    "draw": ((440, 440), 0.42),
}

_SOUND_ASSETS = {
    "game_win": Path(__file__).resolve().parent.parent / "assets" / "game​​ win.ogg",
    "tiger_eat_cow": Path(__file__).resolve().parent.parent / "assets" / "tiger ate cow.ogg",
}


def _sound_samples(notes: tuple[int, ...], duration: float, sample_rate: int = 22050) -> bytes:
    samples = array("h")
    note_duration = duration / len(notes)
    note_samples = int(sample_rate * note_duration)
    fade_samples = max(1, int(sample_rate * 0.015))

    for frequency in notes:
        for index in range(note_samples):
            fade_in = min(1.0, index / fade_samples)
            fade_out = min(1.0, (note_samples - index - 1) / fade_samples)
            envelope = min(fade_in, fade_out)
            value = int(5000 * math.sin(2 * math.pi * frequency * index / sample_rate) * envelope)
            samples.append(value)

    return samples.tobytes()


class AudioManager:
    def __init__(self) -> None:
        self.available = False
        self.enabled = False
        self.countdown_enabled = True
        self.gesture_enabled = True
        self._sounds = {}
        if pygame is None:
            return

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error as exc:
            print(f"Audio unavailable: {exc}")
            return

        self.available = True
        self.enabled = True

    def play(self, sound_name: str) -> None:
        if sound_name not in _SOUND_NOTES and sound_name not in _SOUND_ASSETS:
            raise ValueError(f"Unknown sound: {sound_name}")
        if not self.available or not self.enabled or pygame is None:
            return
        if sound_name == "countdown" and not self.countdown_enabled:
            return
        if sound_name == "gesture" and not self.gesture_enabled:
            return

        sound = self._sounds.get(sound_name)
        if sound is None:
            if sound_name in _SOUND_ASSETS:
                asset_path = _SOUND_ASSETS[sound_name]
                if sound_name == "game_win" and not asset_path.is_file():
                    matching_assets = tuple(asset_path.parent.glob("game*win.ogg"))
                    if len(matching_assets) == 1:
                        asset_path = matching_assets[0]
                sound = pygame.mixer.Sound(str(asset_path))
            else:
                notes, duration = _SOUND_NOTES[sound_name]
                sound = pygame.mixer.Sound(buffer=_sound_samples(notes, duration))
            self._sounds[sound_name] = sound
        sound.play()
