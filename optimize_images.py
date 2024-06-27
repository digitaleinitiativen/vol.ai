import os
import argparse
from PIL import Image

def process_images(overwrite=False):
    # Pfade zu den Ordnern festlegen
    source_folder = "generated_images"
    destination_folder = "generated_images_small"

    # Maximale Größe festlegen
    max_size = (1024, 1024)

    # Überprüfen, ob der Zielordner existiert, und ggf. erstellen
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Alle Dateien im Ursprungsordner durchlaufen
    for filename in os.listdir(source_folder):
        if filename.endswith(".png"):
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, os.path.splitext(filename)[0] + ".jpg")
            
            # Überprüfen, ob die Datei bereits im Zielordner existiert
            if not os.path.exists(destination_path) or overwrite:
                # Bild öffnen
                with Image.open(source_path) as img:
                    # Bildgröße anpassen
                    img.thumbnail(max_size, Image.LANCZOS)
                    # Bild im Zielordner speichern
                    img = img.convert("RGB")
                    img.save(destination_path, "JPEG", optimize=True, quality=70)

    print("Bilder wurden erfolgreich konvertiert und kopiert.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bilder komprimieren und konvertieren.")
    parser.add_argument("--overwrite", action="store_true", help="Vorhandene Bilder überschreiben.")
    args = parser.parse_args()

    process_images(args.overwrite)