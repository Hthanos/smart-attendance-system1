# Application Sounds

This directory contains audio files for notifications and feedback.

## Sound Files

### Notification Sounds
- `attendance_beep.wav` - Short beep when attendance marked (success)
- `error_sound.wav` - Alert sound for errors
- `complete_sound.wav` - Session completion notification

### Audio Specifications
- **Format**: WAV (uncompressed) or MP3
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit
- **Channels**: Mono or Stereo
- **Duration**: 0.5-2 seconds (keep short)

## Creating Sounds

### Free Sound Resources:
- **Freesound**: https://freesound.org/
- **Zapsplat**: https://www.zapsplat.com/
- **Mixkit**: https://mixkit.co/free-sound-effects/

### Using Python to Generate:
```python
import numpy as np
import wave

# Generate 440Hz beep (A note)
sample_rate = 44100
duration = 0.5
frequency = 440

t = np.linspace(0, duration, int(sample_rate * duration))
audio = np.sin(2 * np.pi * frequency * t)

# Normalize to 16-bit range
audio = (audio * 32767).astype(np.int16)

# Save as WAV
with wave.open('attendance_beep.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio.tobytes())
```

## Usage in Code

### Using pygame:
```python
import pygame

pygame.mixer.init()
sound = pygame.mixer.Sound('resources/sounds/attendance_beep.wav')
sound.play()
```

### Using simpleaudio:
```python
import simpleaudio as sa

wave_obj = sa.WaveObject.from_wave_file('resources/sounds/attendance_beep.wav')
play_obj = wave_obj.play()
play_obj.wait_done()
```

### Using winsound (Windows only):
```python
import winsound

winsound.PlaySound(
    'resources/sounds/attendance_beep.wav',
    winsound.SND_FILENAME
)
```

## Configuration

Sound settings can be configured in Settings window:
- Enable/disable sounds
- Volume control
- Custom sound files

## License

Ensure all sound files are properly licensed for use in your project.
Attribution (if required):
- Sound name: Source / License / Attribution
