# Theme Switcher Feature

## Overview
Added a light/dark mode toggle button to the Affinity Linux Installer GUI.

## Changes Made

### 1. Added Theme State Variable
- `self.dark_mode = True` - Tracks current theme mode (defaults to dark)

### 2. Theme Toggle Button
- Located in the top bar (next to system status indicator)
- Shows ☀ (sun) icon in dark mode → "Switch to Light Mode"
- Shows 🌙 (moon) icon in light mode → "Switch to Dark Mode"
- Clicking toggles between themes instantly

### 3. Theme Methods

#### `toggle_theme()`
- Switches between dark and light modes
- Updates button icon and tooltip
- Refreshes UI elements

#### `apply_theme()`
- Applies the current theme
- Dispatches to `_apply_dark_theme()` or `_apply_light_theme()`

#### `_apply_dark_theme()`
- Original dark theme styles
- Dark backgrounds (#1c1c1c, #252526)
- Light text (#dcdcdc, #f0f0f0)

#### `_apply_light_theme()`
- New light theme styles
- Light backgrounds (#f5f5f5, #ffffff)
- Dark text (#2d2d2d)
- Material Design inspired colors

### 4. Dynamic UI Element Updates

#### `_update_top_bar_style()`
- Updates top bar background
- Dark: #2d2d2d
- Light: #e8e8e8
- Updates title text color

#### `_update_right_scroll_style()`
- Updates scroll area styling
- Adjusts scrollbar colors for visibility

#### `_update_progress_label_style()`
- Updates progress label styling
- Adjusts text and background colors

## Usage
Simply click the sun/moon button in the top-right of the window to switch themes.

## Color Schemes

### Dark Theme
- Background: #1c1c1c
- Panel: #252526
- Text: #dcdcdc
- Primary: #8ff361 (lime green)
- Accent: #007acc (blue)

### Light Theme
- Background: #f5f5f5
- Panel: #ffffff
- Text: #2d2d2d
- Primary: #4caf50 (green)
- Accent: #4caf50 (green)

## Technical Details
- Themes are applied via QSS (Qt Style Sheets)
- All widget types have theme-specific styling
- Smooth transitions when switching themes
- No restart required
