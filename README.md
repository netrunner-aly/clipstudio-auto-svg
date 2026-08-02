# clipstudio-auto-svg
Automatically Convert Clip Studio Exports to SVG and WebP using Python

# Clip Studio Paint to SVG & WebP
An offline, privacy-first automation pipeline that automatically converts Clip Studio Paint (`.png`, `.jpg`,`.jpeg`) exports into clean `.svg` vectors and optimized `.webp` web images in real-time.

---

## About the Project

I am currently developing a personal website concept designed as a **game menu UI interface**. It’s a creative approach to displaying my work, housing my project documentation blogs, and dev logs. 

Creating a game UI requires several individual graphic assets. To avoid manually redrawing and tracing every single piece of linework in Inkscape, I collaborated with Gemini and DeepSeek to develop a local Python automation script that exports `.png` files from a Desktop csp_exports folder to a `.svg` and `.webp` assets folder. Whenever an artwork layer is exported as a `.png` from Clip Studio Paint, the script intercepts it and instantly generates clean `.svg` paths and compressed `.webp` web assets into designated output directories.

### Privacy & Integrity First
I prefer to keep my creative work from cloud AI training or online vector converters. This workflow runs **locally and offline on your own machine**. It relies on open-source tracing engines and local computer vision tools, meaning your artwork doesn't interact with an external server or training dataset.

---

## Features

* **Instant Folder Watching:** Detects new `.png` exports from Clip Studio Paint the moment you export them.
* **Auto-Vectorization:** Converts raster line art and colored shapes into editable `.svg` files using local engines (`vtracer` / `img2svg`).
* **Web Optimization:** Automatically generates `.webp` files alongside your vectors to keep web page loading times fast.
* **Offline & Private:** Zero cloud dependencies, zero data collection, zero AI model training on your work.

---

## Installation & Setup

### 1. Prerequisites
Make sure you have **Python 3.8+** and **Clip Studio Paint** installed on your system.

### 2. Install Required Packages
Open your terminal or command prompt and run:

```bash
pip install img2svg watchdog pillow vtracer
```
---

## Repository Structure

Keep your project directory organized like this:

    csp_exports/        # (Created automatically) Drop your CSP PNGs here
    vector_assets/      # (Created automatically) Converted .svg files land here
    webp_assets/        # (Created automatically) Converted.webp files land here
    watch_csp.py        # Main Python script
    README.md           # Project documentation
    LICENSE             # MIT License
    
---

## How to Use

### 1. Start the Watcher:
Open your terminal (or VS Code terminal) and execute the watcher script:

```bash
python csp_to_svg_watcher.py
```

### 2. Draw in Clip Studio Paint:
Hide your background paper layer in CSP so your line art or graphic sits on a transparent background.

### 3. Quick Export:
Export your single-layer artwork as a `.png` directly into the csp_exports folder.

### 4. Done:
The script automatically picks up the image and drops the freshly generated `.svg` and `.webp` files into your vector_assets folder.

---

## Acknowledgements & AI Transparency

I am still relatively new to writing Python code, so I constructed this solution in collaboration with Gemini and cross-referenced/refined the logic using DeepSeek.

I believe in developing efficient, smart workflows with integrity. Utilizing AI as a collaborative pair to build local, ethical, and privacy-respecting tools. I believe in full transparency - I am here to document my development journey.

---

## Feedback & Contributions

Since I am actively learning and refining this pipeline, feedback and suggestions are very welcome! If you spot any flaws, potential code optimizations, or have ideas to improve performance:

    Open an Issue to discuss proposed changes.

    Submit a Pull Request (PR) if you’d like to contribute directly.

---

## License

This project is licensed under the MIT License - feel free to use and adapt freely!
