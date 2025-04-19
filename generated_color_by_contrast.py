# using The Web Content Accessibility Guidelines (WCAG) define specific contrast requirements:
#
#
#

import random
import numpy as np

def get_luminance(color):
    """Calculate relative luminance of an RGB color"""
    if len(color) > 3:
        color = color[:3]
    r, g, b = [c/255 for c in color]
    
    # Convert to sRGB
    r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
    g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
    b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors"""
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    
    # Ensure lighter color is first
    if lum1 < lum2:
        lum1, lum2 = lum2, lum1
        
    return (lum1 + 0.05) / (lum2 + 0.05)


def generate_contrasting_colors(fixed_color, min_contrast=4.5):
    """Generate text and background colors with minimum contrast ratio"""
    while True:
        # Generate random background color
        gen_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
        # Check if contrast is sufficient
        new_ctr = contrast_ratio(fixed_color, gen_color)
        if new_ctr >= min_contrast:
            return fixed_color, gen_color, new_ctr


def ensure_readable_colors(text_color_in, bg_color_in, min_contrast=4.5, fix_color=1):
    """
    fix_color: whether to fix color or not
             1: fix the text color 
             2: fix the background color
    Check if text and background colors have enough contrast.
    If not, adjust the text color for better readability.
    """
    if len(text_color_in) > 3:
        text_color = text_color_in[:3]
    else:
        text_color = text_color_in
    
    if len(bg_color_in) > 3:
        bg_color = bg_color_in[:3]
    else:
        bg_color = bg_color_in
    
    cr = contrast_ratio(text_color, bg_color)
    
    if cr >= min_contrast:
        return text_color, bg_color, cr
    
    if fix_color == 1:
        text_color, bg_color, new_ctr = generate_contrasting_colors(text_color)
    else:
        text_color, bg_color, new_ctr = generate_contrasting_colors(bg_color)
        
    if len(text_color) == 3 and len(text_color_in) == 4:
        text_color_list = list(text_color)
        text_color_list.append(text_color_in[-1])
        text_color = tuple(text_color_list)
        
    if len(bg_color) == 3 and len(bg_color_in) == 4:
        bg_color_list = list(bg_color)
        bg_color_list.append(bg_color_in[-1])
        bg_color = tuple(bg_color_list)

    return text_color, bg_color, new_ctr



if __name__ == "__main__":
    
    # Original colors
    text_color = (200, 50, 50)  # Reddish
    bg_color = (180, 70, 80)    # Similar reddish (low contrast)

    # Check and adjust if needed
    text_color, bg_color, cr = ensure_readable_colors(text_color, bg_color)
    print(f"Contrast ratio: {cr:.2f}")

    # Now use these colors in your text rendering