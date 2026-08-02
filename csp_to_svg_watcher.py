
import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image  # NEW: For WebP conversion

# Try to import available SVG conversion libraries
converter = None
converter_type = None

try:
    from img2svg import api
    converter = 'img2svg'
    print("Using img2svg for conversion")
except ImportError:
    pass

if not converter:
    try:
        import vtracer
        converter = 'vtracer'
        print("Using vtracer for conversion")
    except ImportError:
        pass

if not converter:
    try:
        import cairosvg
        converter = 'cairosvg'
        print("Using cairosvg for conversion")
    except ImportError:
        pass

if not converter:
    print("ERROR: No SVG conversion library found!")
    print("Please install one of the following:")
    print("  pip install vtracer")
    print("  pip install img2svg")
    print("  pip install cairosvg")
    sys.exit(1)

# Define your project folders
WATCH_FOLDER = os.path.expanduser("~/Desktop/csp_exports")  # FIXED: Expand ~ path
OUTPUT_FOLDER = os.path.expanduser("~/Desktop/vector_assets")  # FIXED: Expand ~ path
WEBP_FOLDER = os.path.expanduser("~/Desktop/webp_assets")  # NEW: WebP output folder

# ===== NEW: WebP Conversion Settings =====
CREATE_WEBP = True           # Set to False to disable WebP conversion
WEBP_LOSSLESS = True         # True = lossless (larger, perfect quality), False = lossy
WEBP_QUALITY = 90            # Quality for lossy mode only (1-100)

# Create folders if they don't exist
try:
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(WEBP_FOLDER, exist_ok=True)  # NEW: Create WebP folder
    print(f"Watch folder: {os.path.abspath(WATCH_FOLDER)}")
    print(f"SVG output folder: {os.path.abspath(OUTPUT_FOLDER)}")
    print(f"WebP output folder: {os.path.abspath(WEBP_FOLDER)}")  # NEW
except Exception as e:
    print(f"Error creating folders: {e}")
    sys.exit(1)

# ===== NEW: WebP Conversion Function =====
def convert_to_webp(input_path, output_path, lossless=True, quality=90):
    """
    Convert image to WebP format.
    
    Parameters:
    - input_path: Source image path
    - output_path: WebP output path
    - lossless: True for lossless (perfect quality, ~50-70% of PNG size)
                False for lossy (adjustable quality, ~10-30% of PNG size)
    - quality: Quality setting for lossy mode (1-100, higher = better)
    """
    try:
        with Image.open(input_path) as img:
            # Handle transparency for lossy mode
            if not lossless and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            
            # Save as WebP
            if lossless:
                img.save(output_path, "WEBP", lossless=True)
            else:
                img.save(output_path, "WEBP", lossless=False, quality=quality)
            return True
    except Exception as e:
        print(f"  WebP conversion error: {e}")
        return False

def is_file_ready(filepath, timeout=10):
    """
    Check if file is fully written and accessible.
    Returns True if file is stable and ready for processing.
    """
    if not os.path.exists(filepath):
        return False
    
    start_time = time.time()
    previous_size = -1
    stable_count = 0
    
    while time.time() - start_time < timeout:
        try:
            if not os.path.exists(filepath):
                return False
            
            current_size = os.path.getsize(filepath)
            
            if current_size == 0:
                time.sleep(0.3)
                continue
            
            if current_size == previous_size:
                stable_count += 1
                if stable_count >= 3:
                    try:
                        with open(filepath, 'rb') as f:
                            f.read(1)
                        return True
                    except (IOError, PermissionError):
                        time.sleep(0.3)
                        continue
            else:
                stable_count = 0
                previous_size = current_size
                
            time.sleep(0.3)
            
        except (OSError, FileNotFoundError):
            return False
    
    return False

def convert_to_svg(input_path, output_path):
    """
    Convert image to SVG using available library.
    Handles different library APIs.
    """
    if converter == 'img2svg':
        try:
            api.convert(
                input_path=input_path,
                output_path=output_path,
                mode="trace"
            )
            return True
        except Exception as e:
            try:
                api.convert(
                    input_path=input_path,
                    output_path=output_path,
                    mode="color"
                )
                return True
            except:
                raise e
    
    elif converter == 'vtracer':
        try:
            vtracer.convert_image_to_svg_py(
                input_path,
                output_path,
                colormode='color',
                hierarchical='stacked',
                mode='spline',
                filter_speckle=8,
                color_precision=6,
                layer_difference=16,
                corner_threshold=80,
                length_threshold=4.0,
                max_iterations=10,
                splice_threshold=45,
                path_precision=3
            )
            return True
        except Exception as e:
            try:
                vtracer.convert_image_to_svg_py(
                    input_path,
                    output_path
                )
                return True
            except:
                raise e
    
    elif converter == 'cairosvg':
        import subprocess
        import tempfile
        
        bmp_path = tempfile.mktemp(suffix='.bmp')
        try:
            from PIL import Image
            img = Image.open(input_path)
            img.save(bmp_path, 'BMP')
            
            result = subprocess.run(
                ['potrace', '-s', '-o', output_path, bmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"potrace failed: {result.stderr}")
            
            return True
        finally:
            if os.path.exists(bmp_path):
                os.remove(bmp_path)
    
    return False

class CSPExportHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processing_files = set()
        self.max_retries = 3

    def on_created(self, event):
        self._process(event.src_path)

    def on_moved(self, event):
        self._process(event.dest_path)

    def _process(self, filepath):
        # Skip directories, duplicates, temp files, and non‑image types
        if os.path.isdir(filepath):
            return
        if filepath in self.processing_files:
            return

        filename = os.path.basename(filepath)
        if filename.startswith('.') or filename.startswith('~'):
            return

        valid_extensions = ('.png', '.jpg', '.jpeg',)
        if not filepath.lower().endswith(valid_extensions):
            return

        print(f"\n[{time.strftime('%H:%M:%S')}] New file detected: {filename}")
        self.processing_files.add(filepath)

        try:
            print(f"  Waiting for file to be fully written...")
            if not is_file_ready(filepath, timeout=30):
                print(f"  ERROR: File not ready after timeout: {filename}")
                return

            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)
            print(f"  File size: {file_size_mb:.2f} MB")

            # --- SVG conversion ---
            svg_filename = os.path.splitext(filename)[0] + ".svg"
            svg_output_path = os.path.join(OUTPUT_FOLDER, svg_filename)
            if os.path.exists(svg_output_path):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                svg_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.svg"
                svg_output_path = os.path.join(OUTPUT_FOLDER, svg_filename)

            svg_success = False
            for attempt in range(self.max_retries):
                try:
                    print(f"  Converting to SVG (attempt {attempt + 1}/{self.max_retries})...")
                    convert_to_svg(filepath, svg_output_path)
                    if os.path.exists(svg_output_path) and os.path.getsize(svg_output_path) > 0:
                        svg_size_kb = os.path.getsize(svg_output_path) / 1024
                        print(f"  ✓ SVG SUCCESS ({svg_size_kb:.1f} KB)")
                        svg_success = True
                        break
                except Exception as e:
                    print(f"  SVG Attempt {attempt + 1} failed: {str(e)[:100]}")
                    time.sleep(1)

            # --- WebP conversion ---
            webp_success = False
            if CREATE_WEBP:
                webp_filename = os.path.splitext(filename)[0] + ".webp"
                webp_output_path = os.path.join(WEBP_FOLDER, webp_filename)
                if os.path.exists(webp_output_path):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    webp_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.webp"
                    webp_output_path = os.path.join(WEBP_FOLDER, webp_filename)

                print(f"  Converting to WebP...")
                webp_success = convert_to_webp(filepath, webp_output_path,
                                               lossless=WEBP_LOSSLESS,
                                               quality=WEBP_QUALITY)
                if webp_success and os.path.exists(webp_output_path):
                    webp_size_kb = os.path.getsize(webp_output_path) / 1024
                    reduction = (1 - os.path.getsize(webp_output_path) / file_size) * 100
                    print(f"  ✓ WebP SUCCESS ({webp_size_kb:.1f} KB, {reduction:.1f}% smaller)")
                else:
                    print(f"  ✗ WebP FAILED")

            print(f"  --- Summary ---")
            print(f"    SVG:  {'✓' if svg_success else '✗'}")
            if CREATE_WEBP:
                print(f"    WebP: {'✓' if webp_success else '✗'}")

        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
        finally:
            self.processing_files.discard(filepath)

def main():
    """Main function to run the file watcher"""
    print("=" * 60)
    print("CSP Export to SVG + WebP Converter")
    print("=" * 60)
    print(f"SVG Converter: {converter}")
    print(f"Watching folder: {os.path.abspath(WATCH_FOLDER)}")
    print(f"SVG output folder: {os.path.abspath(OUTPUT_FOLDER)}")
    print(f"WebP output folder: {os.path.abspath(WEBP_FOLDER)}")
    print(f"WebP mode: {'Lossless' if WEBP_LOSSLESS else f'Lossy (Quality: {WEBP_QUALITY})'}")
    print("-" * 60)
    print("Instructions:")
    print("1. Export artwork from Clip Studio Paint to the watch folder")
    print("2. Both SVG and WebP files will be automatically generated")
    print("3. Press Ctrl+C to stop the watcher")
    print("=" * 60)
    
    event_handler = CSPExportHandler()
    observer = Observer()
    
    try:
        observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
        observer.start()
        print("\n✓ Watcher started successfully!\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down watcher...")
        observer.stop()
        print("Watcher stopped.")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        observer.stop()
        sys.exit(1)
        
    finally:
        observer.join()
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()
