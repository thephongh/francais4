from PIL import Image, ImageDraw, ImageFont
import os

def create_clothing_image(text, color, size=(300, 300), bg_color='white'):
    # Create a new image with white background
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Get text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculate text position for center alignment
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=color, font=font)
    
    return img

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Create images for each clothing item
clothing_items = {
    'chemise_blanche.jpg': ('👔\nChemise', 'black'),
    'pantalon_noir.jpg': ('👖\nPantalon', 'black'),
    'sac_rouge.jpg': ('🎒\nSac', 'red'),
    'veste_grise.jpg': ('🧥\nVeste', 'gray'),
    'tshirt_rouge.jpg': ('👕\nT-shirt', 'red'),
    'chapeau_jaune.jpg': ('🎩\nChapeau', 'goldenrod'),
    'robe_violette.jpg': ('👗\nRobe', 'purple'),
    'lunettes.jpg': ('👓\nLunettes', 'black')
}

# Generate and save all images
for filename, (text, color) in clothing_items.items():
    img = create_clothing_image(text, color)
    img.save(f'images/{filename}') 