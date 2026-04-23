# 1. Install Java
sudo apt install openjdk-11-jdk

# 2. Install Android Studio or Android SDK/NDK
# https://developer.android.com/studio

# 3. Setup Python environment
python3 -m venv ~/.venv
source ~/.venv/bin/activate

# 4. Install buildozer and dependencies
pip install --upgrade pip
pip install buildozer cython
pip install casadi numpy pyzmq smbus2 tqdm crcmod cffi pyyaml atomicwrites
pip install git+https://github.com/vpelletier/python-libusb1.git@c18c9fa7cdcaa8e29088af527e5fbe481a53423f

# 5. Clone and prepare repo
git clone https://github.com/Deggory/flowpilotandroid.git
cd flowpilotandroid
git submodule update --init --recursive

# 6. Build everything
source ~/.venv/bin/activate
./build.sh full

# 7. APK will be in: android/build/outputs/apk/release/
