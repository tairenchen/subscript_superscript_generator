import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
import numpy as np
from PIL import Image
import PIL
import os
from io import BytesIO
from generated_color_by_contrast import ensure_readable_colors, contrast_ratio

# super_sub_size_map = {1:"tiny", 2:"scriptsize", 3:"footnotesize", 4:"small", 5:"normalsize", 6:"large", 7:"Large"}

def crop_extra_boundary(image:PIL.Image) -> PIL.Image:
    img_array = np.array(image)
    
    # For transparent PNG, find the alpha channel (if it exists)
    if img_array.shape[2] == 4:  # RGBA
        # Find non-transparent pixels
        non_empty_columns = np.where(img_array[:, :, 3].max(axis=0) > 0)[0]
        non_empty_rows = np.where(img_array[:, :, 3].max(axis=1) > 0)[0]
    else:  # RGB
        # Use inverted approach - find non-white pixels (assuming white background)
        is_not_white = (img_array[:, :, 0] < 255) | (img_array[:, :, 1] < 255) | (img_array[:, :, 2] < 255)
        non_empty_columns = np.where(is_not_white.any(axis=0))[0]
        non_empty_rows = np.where(is_not_white.any(axis=1))[0]
    
    # Crop the image to content only if there are non-empty pixels
    if len(non_empty_rows) > 0 and len(non_empty_columns) > 0:
        cropped_img = img_array[
            min(non_empty_rows):max(non_empty_rows) + 1,
            min(non_empty_columns):max(non_empty_columns) + 1
        ]
        # Convert back to PIL
        final_img = Image.fromarray(cropped_img)
    else:
        final_img = image
    
    return final_img


def generate_text_image(
    main_text="Text",
    super_text=None,
    sub_text=None,
    text_color=(0.0, 0.0, 0.0, 1.0),
    font_size=22,
    left_adjustment=0.02,
    super_sub_position=0.5, # For the superscript, it moves higher; for subscript, it moves lower
    super_sub_size=5, # define the superscript or subscript font size
    dpi=300,
    font_type = 'serif',
    transparent=True
):
    """
    Generate an image with just text (superscript/subscript)
    """
    # Create combined text
    combined_text = main_text
    
    super_sub_position = str(super_sub_position) + "ex"
    # super_sub_size = super_sub_size_map[super_sub_size]
    
    buf = BytesIO()

    # if "$" in main_text or "%" in main_text or "#" in main_text or "&" in main_text or "\\" in main_text:
    #     main_text = main_text.replace("\\", "").replace("$", "\$").replace("%", "\%").replace("#", "\#").replace("&", "\&")

    if "$" in main_text or "%" in main_text or "#" in main_text or "&" in main_text:
        main_text = main_text.replace("$", "\$").replace("%", "\%").replace("#", "\#").replace("&", "\&")
    
    if super_text and not sub_text:
        super_or_sub = 0
        combined_text = f"{main_text}$^{{\\raisebox{{{super_sub_position}}}{{\\fontsize{{{super_sub_size}}}{{0}}\\selectfont {super_text}}}}}$"
        
        # Add space between the main text and superscript
        # combined_text = f"{main_text}\\hspace{{0.2em}}$^{{\\raisebox{{{super_sub_position}}}{{\\fontsize{{{super_sub_size}}}{{0}}\\selectfont {super_text}}}}}$"
    
    elif sub_text and not super_text:
        super_or_sub = 1
        super_sub_position = "-" + super_sub_position        
        combined_text = f"{main_text}$_{{\\raisebox{{{super_sub_position}}}{{\\fontsize{{{super_sub_size}}}{{0}}\\selectfont  {sub_text}}}}}$"
    
    elif super_text and sub_text:
        super_or_sub = 2
        adjusted_sub_position = "-" + super_sub_position  # for subscript (negative lift)
        combined_text = (
            f"{main_text}"
            f"$^{{\\raisebox{{{super_sub_position}}}{{\\fontsize{{{super_sub_size}}}{{0}}\\selectfont {super_text}}}}}"
            f"_{{\\raisebox{{{adjusted_sub_position}}}{{\\fontsize{{{super_sub_size}}}{{0}}\\selectfont {sub_text}}}}}$"
        )

    else:
        # If neither super_text nor sub_text
        super_or_sub = -1
        combined_text = main_text
        
    
    # Set font
    font_prop = None
    rcParams['text.usetex'] = True
    rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
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
    # to avoid cutting the top of superscirpt, increase the bbox.height by 50%
    # then crop it late
    fig.set_size_inches(bbox.width, bbox.height * 1.5 )
    
    # Create a tight layout, which is sensitive to padding
    plt.tight_layout(pad=0)
    
    # Save the image
    plt.savefig(
        buf,
        bbox_inches='tight',
        pad_inches=0,
        transparent=transparent,
        dpi=dpi
    )
    
    # save it for testing
    plt.savefig(
        "./current_test.png",
        bbox_inches='tight',
        pad_inches=0,
        transparent=transparent,
        dpi=dpi
    )
    buf.seek(0)
    gen_image = Image.open(buf)
    
    # crop the white space previously added by increasing the bbox.height
    gen_image = crop_extra_boundary(gen_image)
    
    plt.close()
    
    # Return the dimensions of the generated image
    # img = Image.open(output_path)
    return gen_image.size, gen_image, super_or_sub


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

    wdith_range_bd = img_w - text_w - pad_left - pad_right
    height_range_bd = img_h - text_h - pad_top - pad_bottom

    if wdith_range_bd > 0 and height_range_bd > 0:
                
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
    gen_text_image,
    output_path,
    generated_text_color,
    background_image_path=None,
    gen_bg_color='white',
    pad_all = [0, 0, 0, 0],
):
    """
    Overlays a generated text image onto a background image (or a plain color background),
    applying optional padding around the text.

    Parameters:
        gen_text_image (PIL.Image.Image): 
            The generated text image to overlay (already opened as a PIL Image object).
        
        output_path (str): 
            The file path where the final combined image will be saved (e.g., "output.png").
        
        generated_text_color (tuple or str): 
            The text color used when sampling or blending with a background image.
        
        background_image_path (str, optional): 
            Path to a background image file. If None, a solid color background will be created.
        
        gen_bg_color (str or tuple, optional): 
            The background color to use if no background image is provided. 
            Defaults to 'white'. Accepts color names or RGB(A) tuples.
        
        pad_all (list of int, optional): 
            Padding to apply around the text image [left, top, right, bottom]. 
            Defaults to [0, 0, 0, 0].
    """
    try:
        # Open the images
        text_img = gen_text_image #Image.open(text_image_path)        
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
        background_img_ext.save(output_path)
    
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
    gen_font_size = 10
    super_sub_position = 0
    super_sub_size_ratio = 0.5
    gen_font_type = "/media/Tairen_Chen/Data/all_font_ttfs/georgia/georgia.ttf"
    main_text = "accuracy"
    super_text = '9'
    sub_text = ""
    
    # Add step 2 parameters
    # Either use an existing background image or generate an background
    background_img = "/media/Tairen_Chen/Data/background_images/light_background.jp"
    pad_all = [0,0,0,0] # can generate random pixel values for the padding
    
    text_size, gen_image, super_or_sub = generate_text_image(
        main_text=main_text,
        super_text=super_text,
        sub_text=sub_text,
        text_color=generated_text_color,
        super_sub_position=super_sub_position,
        super_sub_size=gen_font_size * super_sub_size_ratio,
        font_size=gen_font_size,
        font_type=gen_font_type,
    )
    
    # Step 2: Overlay the text on a background
    generated_text_color_denorm = denormalize_rgba(generated_text_color)

    if super_or_sub == 1:
        super_sub_chk = "subscript"
    elif super_or_sub == 0:
        super_sub_chk = "superscript"
    elif super_or_sub == 2:
        super_sub_chk = "bothSuperSub"
    
    gen_font = gen_font_type.split(os.sep)[-1]
        
    save_image_name = super_sub_chk + "_e" + str(super_sub_position) + "_ratio" + str(super_sub_size_ratio) + "_GenFontSize_" + str(gen_font_size) + \
                      "_GenFontColor_" + str(list(generated_text_color)) \
                          + "_" + gen_font + "_" + main_text + "_" + super_text + "_" + sub_text +  ".png"

    if os.path.exists(background_img):
        ## with background image
        overlay_on_background(
            gen_image,
            save_image_name,
            generated_text_color_denorm,
            background_img,
            pad_all=pad_all
        )

    else:
        ## without background iamge, so generated background image
        generated_bkground_color = (255,255,255)
        
        # make sure the generated background has a good contrast with generated_text        
        generated_text_color, generated_bkground_color, new_ctr = ensure_readable_colors(generated_text_color_denorm, generated_bkground_color)
        
        overlay_on_background(
            gen_image,
            save_image_name,
            generated_text_color,
            None,
            generated_bkground_color,
            pad_all
        )


