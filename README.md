**StreakMate** is a lightweight, local-first LeetCode streak companion built with a Chrome extension and a Windows desktop widget. It tracks coding streaks, reminds you to solve a problem before your streak expires, and features a custom mascot with chill, panic, and happy moods.

✨ **Features**
- 🔥 Automatic streak tracking from Accepted LeetCode submissions
- 🥹 23-hour panic mode to encourage daily practice
- 😎 Custom mascot with dynamic mood changes
- 🖥️ Frameless, resizable desktop widget with Floating and Corner modes
- 🔄 Local synchronization between the Chrome extension and desktop companion
- 🔒 Local-first design with no cloud backend
- 🚀 Optional launch on Windows startup

Built to make consistency fun, one problem at a time.
## 🚀 Installation & Setup

Follow these steps to get StreakMate running on your Windows PC.

### 1. Download StreakMate
- Open the repository on GitHub.
- Click **Code → Download ZIP**.
- Extract the downloaded ZIP into a permanent folder on your PC.

### 2. Install Python
StreakMate's desktop companion requires Python 3.

- Download Python from [python.org](https://www.python.org/downloads/).
- During installation, enable **Add Python to PATH**.
- Complete the installation.

### 3. Launch the Desktop Widget
- Open the extracted project folder.
- Double-click `Run-StreakMate.bat`.
- The StreakMate widget should appear on your desktop.

### 4. Install the Chrome Extension
- Open Google Chrome and navigate to `chrome://extensions`.
- Enable **Developer mode**.
- Click **Load unpacked**.
- Select the `streakmate_extension` folder inside the extracted project.
- Pin StreakMate to your Chrome toolbar.

### 5. Use StreakMate
- Click the desktop mascot or streak count to open LeetCode.
- Submit a problem and wait for an **Accepted** result.
- The extension attempts to record your daily streak automatically.
- The mascot changes its expression based on your streak status.
- Use the widget's mode toggle to switch between Floating and Corner modes.
- Resize the widget by dragging its edges or corners.

### 6. Start Automatically with Windows
To launch StreakMate whenever you sign in to Windows:

- Double-click `Install-Autostart.bat` once.
- The widget will launch automatically at your next Windows sign-in.

### 🔒 Privacy
StreakMate is designed to work locally on your computer. The desktop companion and extension communicate through a local connection, and streak data is stored locally. No cloud backend or account is required.

### ⚠️ Notes
- Windows 10/11 and Python 3 are required.
- Keep the extracted project folder in place after installation; the startup shortcut depends on its location.
- The Chrome extension's Accepted-submission detection is experimental and may not detect every submission.
- The widget must be running for desktop updates to appear.
- If the widget does not start, verify that Python is installed and available through `py` or `python`.
