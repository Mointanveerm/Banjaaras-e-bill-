name: Build Banjaaras Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install System Dependencies
      run: |
        sudo dpkg --add-architecture i386
        sudo apt-get update
        sudo apt-get install -y \
          git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
          zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev \
          libssl-dev build-essential ccache libltdl-dev \
          libc6:i386 libstdc++6:i386 zlib1g:i386

    - name: Cache Buildozer global directory
      uses: actions/cache@v4
      with:
        path: ~/.buildozer
        key: ${{ runner.os }}-buildozer-${{ hashFiles('app/buildozer.spec') }}
        restore-keys: |
          ${{ runner.os }}-buildozer-

    - name: Build with Buildozer
      working-directory: ./app
      run: |
        buildozer android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: Banjaaras-Catering-APK
        path: app/bin/*.apk
