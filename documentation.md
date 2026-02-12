# Dark Mode Implementation Guide & Development Notes

## Overview
This document outlines the architectural decisions and implementation details for adding a robust, persistent dark mode to the NiceGUI-based blog application.

## Key Features Implemented
1.  **Persistent State**: Dark mode preference is saved across sessions and page reloads.
2.  **Flash Prevention (Anti-FOUC)**: Eliminates the "white flash" when loading the page in dark mode.
3.  **Seamless Toggling**: Smooth transitions between modes without "stuck" states during navigation.

## Technical Challenges & Solutions

### 1. Persistence
**Problem**: By default, `ui.dark_mode()` is session-based and resets on reload.
**Solution**:
-   Used `app.storage.user` (requires `storage_secret` in `ui.run`) to store the boolean `dark_mode` preference in an encrypted cookie.
-   Bound the UI toggle to this storage value: `dark.bind_value(app.storage.user, 'dark_mode')`.

### 2. Preventing Flash of Unstyled Content (FOUC)
**Problem**: When refreshing a page in dark mode, the browser renders the default white background for a split second before the JavaScript loads and applies the dark theme.
**Solution**:
-   **Critical CSS Injection**: We check the user's storage *on the server side* before serving the page.
-   If dark mode is active, we inject a `<style>` block directly into the `<head>`:
    ```html
    <style>html.dark body { background-color: #121212 !important; color: white !important; }</style>
    <script>document.documentElement.classList.add("dark");</script>
    ```
-   This ensures the browser knows the background should be black *before* it paints the first pixel.

### 3. The "Stuck Background" Bug
**Problem**: We initially injected unconditional CSS (`body { background-color: #121212 }`). When a user navigated pages and then toggled dark mode *off*, the unconditional CSS remained active, keeping the background black while text turned dark (becoming invisible).
**Solution**:
-   Scoped the injected CSS to `html.dark body`.
-   When `toggle()` removes the `dark` class from the HTML element, the CSS rule automatically stops applying, reverting the background to white.

## Future Development & Prompting Guide

When requesting similar features for future applications, use the following prompts to ensure high-quality implementation from the start:

### For Persistent Dark Mode:
> "Implement a dark mode toggle that persists across reloads using `app.storage.user`. Ensure `storage_secret` is configured."

### For Flash-Free Loading (Critical):
> "To prevent FOUC (Flash of Unstyled Content), please conditionally inject critical CSS into the `<head>` based on the stored user preference. The background color should be set before the body is rendered."

### For Robust Styling:
> "Ensure the dark mode implementation handles both Tailwind classes (`dark:`) and Quasar/Material styles. Sync the `dark` class to `document.documentElement` to support standard CSS selectors like `html.dark`."

## Code Reference (`home.py`)

-   **`common_style()`**: Handles the storage check, script injection, and Tailwind class syncing.
-   **`ui.run()`**: Must include `storage_secret='...'` for persistence to work.
-   **Toggle Buttons**: Should directly modify `app.storage.user['dark_mode']` to trigger the binding updates.
