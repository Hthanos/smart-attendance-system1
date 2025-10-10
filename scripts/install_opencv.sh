#!/bin/bash
# OpenCV Installation Script for Raspberry Pi
# For use with Raspberry Pi OS (Debian-based)

set -e  # Exit on error

echo "=========================================="
echo "OpenCV Installation for Raspberry Pi"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "[2/6] Installing dependencies..."
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    python3-pyqt5 \
    python3-dev

# Install pip
echo "[3/6] Installing pip..."
sudo apt-get install -y python3-pip
python3 -m pip install --upgrade pip

# Install NumPy
echo "[4/6] Installing NumPy..."
pip3 install numpy

# Install OpenCV
echo "[5/6] Installing OpenCV..."
# Method 1: Try pre-built package first (faster)
echo "Attempting to install pre-built OpenCV..."
pip3 install opencv-contrib-python

# Verify installation
echo "[6/6] Verifying installation..."
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" && \
    echo "✅ OpenCV installed successfully!" || \
    echo "❌ OpenCV installation failed!"

# Install picamera (for Pi Camera)
echo ""
echo "Installing picamera support..."
pip3 install "picamera[array]"

# Enable camera interface
echo ""
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Test camera: python3 -c 'from picamera import PiCamera; print(\"Camera OK!\")'"
echo "3. Run the attendance system"
echo ""
