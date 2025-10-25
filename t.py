from PIL import Image
import sys

# --- Configuration ---
IMAGE_PATH = '1.png'
OUTPUT_WIDTH = 120  # Terminal width in characters
V_SCALE_FACTOR = 0.55  # Vertical scaling (0.4-0.7 recommended)
ENABLE_COLOR = True  # Set to False for grayscale ASCII
INVERT_BRIGHTNESS = False  # Invert dark/light mapping

# Enhanced character sets (sorted from darkest to lightest)
CHAR_SETS = {
    'standard': " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    'blocks': " ░▒▓█",
    'detailed': " .:-=+*#%@",
    'extended': " .'`^\",:;Il!i~+_-?][}{)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
}

CHAR_SET = CHAR_SETS['detailed']  # Change to 'blocks' or 'detailed' for different styles
# ---------------------

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"

def get_ansi_256_color(r, g, b):
    """
    Convert RGB (0-255) to closest ANSI 256-color code.
    Uses improved color cube mapping for better accuracy.
    """
    # Grayscale check with tighter threshold
    if abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10:
        gray_avg = (r + g + b) // 3
        if gray_avg < 8:
            return 16  # Black
        if gray_avg > 248:
            return 231  # White
        # 24 grayscale shades (232-255)
        return 232 + int((gray_avg - 8) / 247 * 23)
    
    # 6x6x6 color cube (216 colors, codes 16-231)
    def rgb_to_cube(val):
        """Map 0-255 RGB value to 0-5 cube index"""
        return int(val / 255 * 5 + 0.5)  # Rounding for better accuracy
    
    r_idx = rgb_to_cube(r)
    g_idx = rgb_to_cube(g)
    b_idx = rgb_to_cube(b)
    
    return 16 + (36 * r_idx) + (6 * g_idx) + b_idx

def get_ansi_true_color(r, g, b):
    """Generate 24-bit true color ANSI code (better quality if terminal supports it)"""
    return f"\033[38;2;{r};{g};{b}m"

def calculate_luminance(r, g, b):
    """
    Calculate perceptual luminance using ITU-R BT.709 standard.
    More accurate than simple averaging.
    """
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def generate_ascii_art(image_path, width=OUTPUT_WIDTH, v_scale=V_SCALE_FACTOR, 
                       colored=ENABLE_COLOR, invert=INVERT_BRIGHTNESS,
                       true_color=False):
    """
    Generate ASCII art from an image.
    
    Args:
        image_path: Path to input image
        width: Output width in characters
        v_scale: Vertical scale factor (adjust for aspect ratio)
        colored: Enable ANSI color output
        invert: Invert brightness mapping
        true_color: Use 24-bit color (if terminal supports it)
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate dimensions maintaining aspect ratio
            aspect_ratio = img.height / img.width
            new_height = int(width * aspect_ratio * v_scale)
            
            # Resize with high-quality resampling
            img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            
            # Extract pixel data
            pixels = list(img.getdata())
            img_width, img_height = img.size
        
        # Character mapping setup
        chars = CHAR_SET
        if invert:
            chars = chars[::-1]  # Reverse for inverted mapping
        
        char_count = len(chars)
        
        # Generate ASCII art
        output_lines = []
        for y in range(img_height):
            line = []
            for x in range(img_width):
                idx = y * img_width + x
                r, g, b = pixels[idx]
                
                # Calculate luminance for character selection
                luminance = calculate_luminance(r, g, b)
                
                # Map luminance (0-255) to character index
                char_idx = int(luminance / 255 * (char_count - 1))
                char_idx = max(0, min(char_idx, char_count - 1))  # Clamp
                char = chars[char_idx]
                
                # Add color if enabled
                if colored:
                    if true_color:
                        color_code = get_ansi_true_color(r, g, b)
                        line.append(f"{color_code}{char}")
                    else:
                        color_code = get_ansi_256_color(r, g, b)
                        line.append(f"\033[38;5;{color_code}m{char}")
                else:
                    line.append(char)
            
            output_lines.append(''.join(line) + RESET)
        
        return '\n'.join(output_lines)
    
    except FileNotFoundError:
        return f"Error: Image file '{image_path}' not found."
    except Exception as e:
        return f"Error: {e}"

def save_to_file(content, filename='ascii_art.txt'):
    """Save ASCII art to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nASCII art saved to '{filename}'")

# Main execution
if __name__ == "__main__":
    print("Generating ASCII art...\n")
    
    # Generate the art
    ascii_art = generate_ascii_art(
        IMAGE_PATH,
        width=OUTPUT_WIDTH,
        v_scale=V_SCALE_FACTOR,
        colored=ENABLE_COLOR,
        invert=INVERT_BRIGHTNESS,
        true_color=True  # Set to True if your terminal supports 24-bit color
    )
    
    # Display
    print(ascii_art)
    
    # Optional: Save to file
    # save_to_file(ascii_art, 'output.txt')
    
    print("\n" + "="*50)
    print(f"Width: {OUTPUT_WIDTH} chars | V-Scale: {V_SCALE_FACTOR}")
    print(f"Character Set: {len(CHAR_SET)} chars | Color: {ENABLE_COLOR}")
    print("="*50)
    print("\n" + '='*50)
    print(f"size =  ")