#!/usr/bin/env python3
"""
Script para generar iconos de la PWA DivisaAPI
Genera iconos en diferentes tamaños para el manifest.json
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Crear un icono del tamaño especificado"""
    # Crear imagen con fondo transparente
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calcular dimensiones
    padding = size // 8
    inner_size = size - (padding * 2)
    
    # Crear fondo circular con gradiente
    # Fondo exterior
    draw.ellipse([0, 0, size-1, size-1], fill=(99, 102, 241, 255))
    
    # Fondo interior más claro
    inner_padding = padding // 2
    draw.ellipse([inner_padding, inner_padding, size-1-inner_padding, size-1-inner_padding], 
                 fill=(139, 92, 246, 255))
    
    # Símbolo de moneda (VES)
    symbol_size = inner_size // 3
    symbol_x = size // 2 - symbol_size // 2
    symbol_y = size // 2 - symbol_size // 2
    
    # Dibujar símbolo de moneda
    draw.ellipse([symbol_x, symbol_y, symbol_x + symbol_size, symbol_y + symbol_size], 
                 fill=(255, 255, 255, 255))
    
    # Texto "VES" en el centro
    try:
        # Intentar usar una fuente del sistema
        font_size = max(8, size // 8)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback a fuente por defecto
        font = ImageFont.load_default()
    
    text = "VES"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = size // 2 - text_width // 2
    text_y = size // 2 - text_height // 2
    
    draw.text((text_x, text_y), text, fill=(99, 102, 241, 255), font=font)
    
    # Guardar icono
    icons_dir = "static/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    icon_path = os.path.join(icons_dir, filename)
    img.save(icon_path, "PNG")
    print(f"✅ Icono creado: {icon_path} ({size}x{size})")
    
    return icon_path

def main():
    """Función principal para generar todos los iconos"""
    print("🎨 Generando iconos para DivisaAPI PWA...")
    
    # Tamaños de iconos requeridos por el manifest
    icon_sizes = [
        (72, "icon-72x72.png"),
        (96, "icon-96x96.png"),
        (128, "icon-128x128.png"),
        (144, "icon-144x144.png"),
        (152, "icon-152x152.png"),
        (192, "icon-192x192.png"),
        (384, "icon-384x384.png"),
        (512, "icon-512x512.png")
    ]
    
    created_icons = []
    
    for size, filename in icon_sizes:
        try:
            icon_path = create_icon(size, filename)
            created_icons.append(icon_path)
        except Exception as e:
            print(f"❌ Error creando icono {filename}: {e}")
    
    print(f"\n🎯 Iconos generados: {len(created_icons)}/{len(icon_sizes)}")
    
    if created_icons:
        print("\n📁 Iconos creados en: static/icons/")
        print("🔗 Asegúrate de que el manifest.json apunte a estos archivos")
        
        # Verificar que el manifest.json existe
        manifest_path = "static/manifest.json"
        if os.path.exists(manifest_path):
            print(f"✅ Manifest encontrado: {manifest_path}")
        else:
            print(f"⚠️  Manifest no encontrado: {manifest_path}")
    else:
        print("❌ No se pudieron generar iconos")

if __name__ == "__main__":
    main() 