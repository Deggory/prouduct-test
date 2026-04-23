# STEP 1: Setup environment
sudo apt install openjdk-11-jdk git wget

# STEP 2: Install Android Studio OR download SDK separately
# https://developer.android.com/studio

# STEP 3: Clone repo
git clone https://github.com/Deggory/flowpilotandroid.git
cd flowpilotandroid

# STEP 4: Initialize submodules
git submodule update --init --recursive

# STEP 5: Setup Python (for flowy if needed)
python3 -m venv ~/.venv
source ~/.venv/bin/activate

# STEP 6: Build APK (choose one)
# Quick build (Gradle only):
./gradlew assembleRelease

# OR Full build (includes Python components):
source ~/.venv/bin/activate
./build.sh full

# STEP 7: Find your APK
ls -lh android/build/outputs/apk/release/



VS Code Setup
Step 1: Download and Install VS Code

    Go to https://code.visualstudio.com/
    Download for your operating system
    Install and launch VS Code

Step 2: Install Required Extensions

Open VS Code and press Ctrl+Shift+X (Extensions panel).

Install these extensions (in order):
#	Extension Name	Publisher	Purpose
1	Extension Pack for Java	Microsoft	Java development support
2	Gradle for Java	Microsoft	Gradle build automation
3	Python	Microsoft	Python support (optional but recommended)
4	Android	Google	Android development tools
5	Better Comments	Aaron Bond	Color-coded comments
6	GitLens	GitKraken	Git integration
7	Code Runner	Jun Han	Quick code execution
8	Terminal	Microsoft	Enhanced terminal support

Installation Instructions:

    In Extensions panel, search for extension name
    Click "Install" button
    Wait for installation to complete
    Reload VS Code when prompted

Quick Install (Paste in VS Code Terminal):
bash

code --install-extension vscjava.extension-pack-for-java
code --install-extension vscjava.vscode-gradle
code --install-extension ms-python.python
code --install-extension Google.android-ndk-manager
code --install-extension Aaron Bond.better-comments
code --install-extension eamodio.gitlens
code --install-extension formulahendry.code-runner





