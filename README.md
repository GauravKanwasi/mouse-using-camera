# AirMouse - Camera-Based Mouse Control (Work in Progress)

A Python application that enables mouse control using hand gestures via webcam. Currently in active development but fully functional with core features implemented.

## Features ✨
- **Cursor Movement**: Control mouse pointer with index finger
- **Left/Right Click**: Pinch thumb-index or thumb-middle fingers
- **Drag & Drop**: Sustain thumb-index pinch while moving
- **Vertical Scroll**: Move open hand up/down
- **Double Click**: Quick consecutive thumb-index pinches
- **Configurable Settings**: Adjust sensitivity via `config.ini`

## Installation 🛠️

### Requirements
- Python 3.8+
- Webcam
- Windows/macOS/Linux

### Setup
```bash
# Clone repository
git clone https://github.com/GauravKanwasi/mouse-using-camera.git
cd mouse-using-camera

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
