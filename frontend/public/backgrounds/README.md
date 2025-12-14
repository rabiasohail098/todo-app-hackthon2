# Background Images

This directory contains background images for the todo app's theme system.

## Current Files

- `light-theme-bg.svg` - Desktop background for light theme (1920x1080)
- `dark-theme-bg.svg` - Desktop background for dark theme (1920x1080)
- `light-theme-bg-sm.svg` - Mobile background for light theme (1280x720)
- `dark-theme-bg-sm.svg` - Mobile background for dark theme (1280x720)

## Replacing Placeholders

The current SVG files are placeholders with gradient patterns. To use custom images:

1. Replace these SVG files with JPG or WebP images
2. Keep the same filenames
3. Recommended specifications:
   - Desktop: 1920x1080px, optimized to ~150-200KB
   - Mobile: 1280x720px, optimized to ~80-100KB
   - Format: JPG (70-80% quality) or WebP for better compression
   - Use tools like TinyPNG, ImageOptim, or Squoosh for optimization

## Image Recommendations

### Light Theme
- Soft, bright colors
- Minimal patterns (clouds, subtle gradients, paper textures)
- High-key aesthetic

### Dark Theme
- Deep blues, purples, or grays
- Starry sky, subtle geometric patterns
- Low-key aesthetic

## CSS Usage

These images are referenced in `app/globals.css`:

```css
body.with-background-image::before {
  background-image: url('/backgrounds/light-theme-bg.svg');
}

.dark body.with-background-image::before {
  background-image: url('/backgrounds/dark-theme-bg.svg');
}
```
