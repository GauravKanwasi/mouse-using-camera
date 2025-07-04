# AirMouse - Camera-Based Mouse Control (Work in Progress)

A Python application that enables mouse control using hand gestures via webcam. Currently in active development but fully functional with core features implemented.

## Features ✨
- **Cursor Movement**: Control mouse pointer with index finger [[1]]
- **Left/Right Click**: Pinch thumb-index or thumb-middle fingers [[6]]
- **Drag & Drop**: Sustain thumb-index pinch while moving [[9]]
- **Vertical Scroll**: Move open hand up/down [[3]]
- **Double Click**: Quick consecutive thumb-index pinches [[8]]
- **Configurable Settings**: Adjust sensitivity via `config.ini` or environment variables [[5]]

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



---

### **Key Improvements Summary**
1. **Multi-Threading**: Separated frame processing and gesture handling to reduce latency [[4]][[8]]
2. **Dynamic Smoothing**: Adaptive cursor speed based on hand movement velocity [[1]][[8]]
3. **Calibration Mode**: Automatic threshold adjustment for varying lighting conditions [[1]][[8]]
4. **Environment Variables**: Override settings without editing `config.ini` [[5]]
5. **Scroll Buffer**: Reduce jitter with averaged scroll values [[6]]
6. **Enhanced Error Handling**: Robust camera permission checks and resource cleanup [[1]][[7]]

All files are compatible and work together in a single directory. Let me know if you need further refinements!
