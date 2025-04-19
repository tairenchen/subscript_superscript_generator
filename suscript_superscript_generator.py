import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
import os
from generated_color_by_contrast import ensure_readable_colors, contrast_ratio

def generate_text_image(
    output_path,
    main_text="Text",
    super_text=None,
    sub_text=None,
    text_color=(0.0, 0.0, 0.0, 1.0),
    font_size=22,
    left_adjustment=0.02,
    dpi=300,
    font_type = 'serif',
    transparent=True
):
    """
    Generate an image with just text (superscript/subscript)
    """
    # Create combined text
    combined_text = main_text
    if super_text:
        combined_text = f"{main_text}$^{{{super_text}}}$"
    elif sub_text:
        combined_text = f"{main_text}$_{{{sub_text}}}$"

    # Set font
    font_prop = None
    if font_type.lower() in ['serif', 'sans-serif', 'monospace']:
        rcParams['mathtext.fontset'] = 'custom'
        rcParams['mathtext.rm'] = font_type.lower()
    elif os.path.isfile(font_type):
        # Load TTF font
        font_prop = FontProperties(fname=font_type)
    else:
        raise ValueError("font_type must be 'serif', 'sans-serif', 'monospace', or a valid .ttf path")


    # Create figure
    fig_width = len(combined_text) * font_size / 50
    fig_height = font_size / 50 * 1.5
    
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
        
    # Add text with slight position adjustment
    text = ax.text(
        0.5 - left_adjustment, 0.5, combined_text,
        ha='center', va='center',
        fontsize=font_size,
        color=text_color,
        fontproperties=font_prop,
        transform=ax.transAxes
    )
    
    # First draw to get the bbox
    fig.canvas.draw()
    bbox = text.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        
    # Update figure size
    fig.set_size_inches(bbox.width, bbox.height)
    
    # Create a tight layout, which is sensitive to padding
    plt.tight_layout(pad=0)
    
    # Save the image
    plt.savefig(
        output_path,
        bbox_inches='tight',
        pad_inches=0,
        transparent=transparent,
        dpi=dpi
    )
    
    plt.close()
    print(f"Text image saved to {output_path}")
    
    # Return the dimensions of the generated image
    img = Image.open(output_path)
    return img.size


def gen_image_random_sample_(wdith_range_bd, height_range_bd, text_size, background_img, pad_all):
    pad_left, pad_top, pad_right, pad_bottom = pad_all
    text_w, text_h = text_size
    sample_width_left = np.random.randint(pad_left, wdith_range_bd + 1)
    sample_height_top = np.random.randint(pad_top, height_range_bd + 1)
    sample_width_right = sample_width_left + text_w
    sample_height_bottom = sample_height_top + text_h
    
    cropped_image = background_img.crop((sample_width_left, sample_height_top, sample_width_right, sample_height_bottom))
    cropped_img_rgb = np.array(cropped_image).mean(axis=(0,1))   
    return cropped_img_rgb, cropped_image, [sample_width_left, sample_height_top, sample_width_right, sample_height_bottom]


def sample_from_bgImage(background_img:Image, text_img_size:list, pad_all:list, generated_text_color:tuple, min_contrast:float =4.5):
    img_w, img_h = background_img.size
    text_w, text_h = text_img_size
    pad_left, pad_top, pad_right, pad_bottom = pad_all
    
    if img_w > text_w and img_h > text_h:
        
        wdith_range_bd = img_w - text_w - pad_left - pad_right
        height_range_bd = img_h - text_h - pad_top - pad_bottom
        
        cropped_img_rgb, cropped_image, sample_indices = gen_image_random_sample_(wdith_range_bd, height_range_bd, [text_w, text_h], background_img, pad_all)
        
        count_contrast = 0
        use_bg = True
        
        while contrast_ratio(generated_text_color, cropped_img_rgb) < min_contrast:
            cropped_img_rgb, cropped_image, sample_indices = gen_image_random_sample_(wdith_range_bd, height_range_bd, [text_w, text_h], background_img, pad_all)
            if count_contrast > 20:
                print("background does not have enough contrast with text")
                print("Generate the background instead")
                use_bg = False
                break
            count_contrast += 1
        
        [sample_width_left, sample_height_top, sample_width_right, sample_height_bottom] = sample_indices
        extend_left = sample_width_left - pad_left
        extend_right = sample_width_right + pad_right
        extend_top = sample_height_top - pad_top
        extend_bottom = sample_height_bottom + pad_bottom
        
        if not use_bg:
            text_width = sample_width_right - sample_width_left
            text_height = sample_height_bottom - sample_height_top
            upd_text_width = text_width + pad_left + pad_right
            upd_text_height = text_height + pad_top + pad_bottom
            generated_text_color, generated_bkground_color, new_ctr = ensure_readable_colors(generated_text_color, cropped_img_rgb, fix_color=1)
            cropped_image = Image.new('RGBA', (text_width, text_height), generated_bkground_color)
            background_img_ext = Image.new('RGBA', (upd_text_width, upd_text_height), generated_bkground_color)
            
        else:    
            background_img_ext = background_img.crop((extend_left, extend_top, extend_right, extend_bottom))
            
        return cropped_image, background_img_ext
                
    else:
        return None, None


def overlay_on_background(
    text_image_path,
    output_path,
    generated_text_color,
    background_image_path=None,
    gen_bg_color='white',
    pad_all = [0, 0, 0, 0],
):
    """
    Overlay the text image on a background image
    
    Parameters:
    -----------
    text_image_path : str
        Path to the text image
    background_image_path : str
        Path to the background image
    output_path : str
        Path to save the combined image
    position : str or tuple
        'center' or (x, y) coordinates for positioning
    scale_background : bool
        If True, scales the background to match text size
        If False, crops the background to match text size
    """
    try:
        # Open the images
        text_img = Image.open(text_image_path)        
        # Get dimensions
        text_width, text_height = text_img.size
        
        # Crop background to match text dimensions
        # If background is smaller than text, it will be centered
        pad_left, pad_top, pad_right, pad_bottom = pad_all
        if background_image_path is None:
            # Create a new blank image with text dimensions
            upd_text_width = text_width + pad_left + pad_right
            upd_text_height = text_height + pad_top + pad_bottom
            
            background_img = Image.new('RGBA', (text_width, text_height), gen_bg_color)
            background_img_ext = Image.new('RGBA', (upd_text_width, upd_text_height), gen_bg_color)
            
        else:
            background_img = Image.open(background_image_path)
            background_img, background_img_ext = sample_from_bgImage(background_img, [text_width, text_height], pad_all, generated_text_color)
        
        # Create a new image with RGBA mode to handle transparency
        combined_img = Image.new('RGBA', text_img.size, (0, 0, 0, 0))
        
        # Paste the background first
        combined_img.paste(background_img, (0, 0))
    
        # Overlay the text (with transparency)
        if text_img.mode == 'RGBA':
            combined_img = Image.alpha_composite(combined_img, text_img)
        else:
            # Convert to RGBA if needed
            text_img_rgba = text_img.convert('RGBA')
            combined_img = Image.alpha_composite(combined_img, text_img_rgba)
    
        # Save the combined image
        # combined_img.save(output_path)
        print(f"Combined image saved to {output_path}")
        background_img_ext.paste(combined_img, (pad_left, pad_top))
        background_img_ext.save("gen_extend_img.png")
    
    
    except Exception as e:
        print(f"Error overlaying images: {e}")


def normalize_rgba(rgba):
    return tuple(c / 255 for c in rgba)

def denormalize_rgba(rgba):
    return tuple(255 * c for c in rgba)

# Example usage
if __name__ == "__main__":
    
    # Step 1: Generate the text image  
    generated_text_color = (0.0, 0.0, 0.0, 1.0) # Normalized RGBA 1.0 means no transpancy
    
    font_type = "/media/Tairen_Chen/Data/all_font_ttfs/georgia/georgia.ttf"
    
    text_size = generate_text_image(
        "text_with_superscript.png",
        main_text="Example",
        super_text="2",
        text_color=generated_text_color,
        font_size=16,
        font_type=font_type
    )
    
    # Step 2: Overlay the text on a background
    # Either use an existing background image or generate an background
    background_img = "/media/Tairen_Chen/Data/background_images/light_background.jpg"
    
    pad_all = [5,5,10,10] # can generate random pixel values for the padding
    
    generated_text_color_denorm = denormalize_rgba(generated_text_color)
    
    if os.path.exists(background_img):
        ## with background image
        overlay_on_background(
            "text_with_superscript.png",
            "final_image_cropped.png",
            generated_text_color_denorm,
            background_img,
            pad_all=pad_all
        )

    else:
        ## without background iamge, so generated background image
        generated_bkground_color = (0,0,0)
        # make sure the generated background has a good contrast with generated_text        
        generated_text_color, generated_bkground_color, new_ctr = ensure_readable_colors(generated_text_color_denorm, generated_bkground_color)
        
        overlay_on_background(
            "text_with_superscript.png",
            "final_image_cropped.png",
            generated_text_color,
            None,
            generated_bkground_color,
            pad_all
        )
        

