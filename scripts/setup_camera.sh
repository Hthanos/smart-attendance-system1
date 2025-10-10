#!/bin/bash
# Camera Setup and Testing Script

set -e

echo "=========================================="
echo "Camera Setup and Configuration"
echo "=========================================="
echo ""

# Detect platform
if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
    PLATFORM="raspberry_pi"
    echo "Platform: Raspberry Pi"
else
    PLATFORM="generic"
    echo "Platform: Generic Linux/Unix"
fi

echo ""
echo "Available cameras:"
echo ""

# List USB cameras
if [ "$PLATFORM" == "raspberry_pi" ]; then
    # Check for Pi Camera
    if vcgencmd get_camera | grep -q "detected=1"; then
        echo "✅ Raspberry Pi Camera Module detected"
        PI_CAMERA=true
    else
        echo "❌ No Raspberry Pi Camera Module detected"
        PI_CAMERA=false
    fi
    echo ""
fi

# List USB video devices
if ls /dev/video* >/dev/null 2>&1; then
    echo "USB Cameras found:"
    for device in /dev/video*; do
        if [ -c "$device" ]; then
            echo "  - $device"
            v4l2-ctl --device=$device --all 2>/dev/null | grep "Card type" || true
        fi
    done
else
    echo "❌ No USB cameras found at /dev/video*"
fi

echo ""
echo "=========================================="
echo "Camera Configuration"
echo "=========================================="
echo ""

# Ask user which camera to use
if [ "$PLATFORM" == "raspberry_pi" ] && [ "$PI_CAMERA" == true ]; then
    echo "Which camera would you like to configure?"
    echo "1) Raspberry Pi Camera Module"
    echo "2) USB Webcam"
    read -p "Enter choice (1 or 2): " camera_choice
    
    if [ "$camera_choice" == "1" ]; then
        CAMERA_TYPE="picamera"
        CAMERA_INDEX="0"
    else
        CAMERA_TYPE="usb"
        read -p "Enter USB camera index (0, 1, 2...): " CAMERA_INDEX
    fi
else
    CAMERA_TYPE="usb"
    read -p "Enter USB camera index (0, 1, 2...): " CAMERA_INDEX
fi

echo ""
echo "Testing camera: $CAMERA_TYPE (index: $CAMERA_INDEX)"
echo ""

# Test camera with Python
python3 << EOF
import sys
import cv2

camera_type = "$CAMERA_TYPE"
camera_index = int("$CAMERA_INDEX")

print("Attempting to open camera...")

try:
    if camera_type == "picamera":
        # Test Pi Camera
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        import time
        
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 30
        raw_capture = PiRGBArray(camera, size=(640, 480))
        
        time.sleep(0.1)
        camera.capture(raw_capture, format="bgr")
        frame = raw_capture.array
        
        print("✅ Pi Camera working!")
        print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
        
        camera.close()
        
    else:
        # Test USB Camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("❌ Failed to open USB camera")
            sys.exit(1)
        
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to read from camera")
            sys.exit(1)
        
        height, width = frame.shape[:2]
        print("✅ USB Camera working!")
        print(f"   Resolution: {width}x{height}")
        
        cap.release()
    
    print("\n✅ Camera test successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Install required packages: pip install opencv-python picamera")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Camera test failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Updating Configuration"
    echo "=========================================="
    echo ""
    
    # Update .env file
    ENV_FILE=".env"
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "Created .env from .env.example"
        else
            touch .env
            echo "Created new .env file"
        fi
    fi
    
    # Update camera settings
    if grep -q "CAMERA_TYPE=" .env; then
        sed -i "s/CAMERA_TYPE=.*/CAMERA_TYPE=$CAMERA_TYPE/" .env
    else
        echo "CAMERA_TYPE=$CAMERA_TYPE" >> .env
    fi
    
    if grep -q "CAMERA_INDEX=" .env; then
        sed -i "s/CAMERA_INDEX=.*/CAMERA_INDEX=$CAMERA_INDEX/" .env
    else
        echo "CAMERA_INDEX=$CAMERA_INDEX" >> .env
    fi
    
    echo "✅ Configuration updated in .env"
    echo "   CAMERA_TYPE=$CAMERA_TYPE"
    echo "   CAMERA_INDEX=$CAMERA_INDEX"
    
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Camera is ready to use with the attendance system."
    echo "Run: python3 app.py"
    
else
    echo ""
    echo "❌ Camera setup failed. Please check:"
    echo "   - Camera is properly connected"
    echo "   - Required drivers are installed"
    echo "   - Camera permissions are correct"
    echo "   - No other application is using the camera"
fi
