from PIL import Image, ImageDraw
import os

def create_app_icon():
    """Crée une icône d'application simple"""
    # Créer une image 256x256
    img = Image.new('RGBA', (256, 256), (70, 130, 180, 255))  # Bleu acier
    draw = ImageDraw.Draw(img)
    
    # Dessiner un train/camion simple
    # Corps du véhicule
    draw.rectangle([50, 100, 200, 150], fill=(255, 215, 0, 255))  # Or
    
    # Roues
    draw.ellipse([70, 140, 90, 160], fill=(50, 50, 50, 255))
    draw.ellipse([160, 140, 180, 160], fill=(50, 50, 50, 255))
    
    # Texte TS
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((100, 50), "TS", fill=(255, 255, 255, 255), font=font)
    
    # Sauvegarder en différentes tailles pour .ico
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Sauvegarder en .ico
    icons[0].save("resources/icons/app_icon.ico", format='ICO', sizes=sizes)
    print("Icône créée: resources/icons/app_icon.ico")
    
    # Sauvegarder aussi en PNG pour l'application
    img.resize((64, 64), Image.Resampling.LANCZOS).save("resources/icons/app_icon.png")
    print("Icône PNG créée")

if __name__ == "__main__":
    # Créer le dossier icons s'il n'existe pas
    os.makedirs("resources/icons", exist_ok=True)
    create_app_icon()
