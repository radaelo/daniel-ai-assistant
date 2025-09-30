import json
import os
from pathlib import Path

def prepare_training_data():
    """Prepara datos para fine-tuning a partir de textos"""
    try:
        text_dir = Path("./text_data")
        training_data = []
        
        for txt_file in text_dir.glob("*.txt"):
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Crear ejemplos de entrenamiento
            example = {
                "text": content[:1000],  # Limitar tamaño
                "metadata": {
                    "source": txt_file.name,
                    "type": "technical_document"
                }
            }
            training_data.append(example)
        
        # Guardar en formato JSON
        with open("training_data.json", "w", encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Preparados {len(training_data)} ejemplos de entrenamiento")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    prepare_training_data()
