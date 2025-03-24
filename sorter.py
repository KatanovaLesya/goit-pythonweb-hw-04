import asyncio
import aiofiles
import aiofiles.os
from pathlib import Path
import argparse
import shutil
import os
import logging

parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням")

parser.add_argument("source", type=str, help="Шлях до вихідної папки (source folder)")
parser.add_argument("output", type=str, help="Шлях до папки призначення (output folder)")

args = parser.parse_args()

source_path = Path(args.source)
output_path = Path(args.output)

async def read_folder(source_path: Path, output_path: Path):
    tasks = []

    for file_path in source_path.rglob('*'):
        if file_path.is_file():
            task = asyncio.create_task(copy_file(file_path, output_path))
            tasks.append(task)

    await asyncio.gather(*tasks)

    
async def copy_file(file_path: Path, output_path: Path):
    try:
        # Отримуємо розширення файлу, без крапки
        extension = file_path.suffix[1:] if file_path.suffix else "no_extension"

        # Шлях до папки за розширенням
        ext_folder = output_path / extension
        ext_folder.mkdir(parents=True, exist_ok=True)

        # Кінцева ціль для копіювання
        dest_file = ext_folder / file_path.name

        # Копіюємо файл (використовуємо синхронну функцію, але в окремому потоці)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy2, file_path, dest_file)

    except Exception as e:
        logging.error(f"Помилка копіювання {file_path} → {dest_file}: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("file_sorter.log"), logging.StreamHandler()]
    )

    if not source_path.exists():
        logging.error(f"Вихідна папка не існує: {source_path}")
        exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    asyncio.run(read_folder(source_path, output_path))
    logging.info("✅ Сортування завершено!")

