# Application Icons

This directory contains icons and images used in the application UI.

## Required Icons

### Application Icons
- `app_icon.png` (256x256) - Main application icon
- `app_icon_32.png` (32x32) - Taskbar icon
- `app_icon_16.png` (16x16) - Small icon

### UI Icons
- `user_placeholder.png` (200x200) - Default student photo placeholder
- `camera_icon.png` (64x64) - Camera/capture icon
- `success_icon.png` (48x48) - Success/checkmark icon
- `error_icon.png` (48x48) - Error/warning icon
- `settings_icon.png` (48x48) - Settings gear icon

### Feature Icons
- `register_icon.png` (64x64) - Student registration
- `attendance_icon.png` (64x64) - Take attendance
- `report_icon.png` (64x64) - View reports
- `export_icon.png` (48x48) - Export data

## Icon Format Guidelines

- **Format**: PNG with transparency
- **Style**: Flat design, consistent color scheme
- **Colors**: Primary: #2C3E50, Accent: #3498DB
- **Background**: Transparent or white

## Creating Icons

### Using Free Resources:
- **Flaticon**: https://www.flaticon.com/
- **Icons8**: https://icons8.com/
- **Font Awesome**: https://fontawesome.com/

### Using Python (PIL):
```python
from PIL import Image, ImageDraw

# Create simple placeholder
img = Image.new('RGBA', (256, 256), (44, 62, 80, 255))
draw = ImageDraw.Draw(img)
draw.ellipse([64, 64, 192, 192], fill=(255, 255, 255, 255))
img.save('app_icon.png')
```

## Placeholder Script

Run this to create basic placeholders:

```bash
cd resources/icons
python3 create_placeholders.py
```

## Usage in Code

```python
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk

# Load icon
icon_path = Path('resources/icons/app_icon.png')
if icon_path.exists():
    photo = ImageTk.PhotoImage(Image.open(icon_path))
    label = tk.Label(image=photo)
```

## Attribution

If using third-party icons, maintain attribution here:
- Icon name: Source / License
