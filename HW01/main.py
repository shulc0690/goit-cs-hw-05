import asyncio
import aiofiles
import os
import logging
from pathlib import Path
from argparse import ArgumentParser

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def copy_file(file_path, destination_dir):
    try:
        dest_file = destination_dir / file_path.name
        async with aiofiles.open(file_path, "rb") as f_source:
            content = await f_source.read()

        async with aiofiles.open(dest_file, "wb") as f_dest:
            await f_dest.write(content)

        logging.info(f"Copied {file_path} to {dest_file}")
    except Exception as e:
        logging.error(f"Error copying {file_path}: {e}")


async def read_folder(folder_path, output_dir):
    tasks = []
    for item in os.scandir(folder_path):
        if item.is_file():
            ext = item.name.split(".")[-1]
            dest_folder = output_dir / ext
            dest_folder.mkdir(parents=True, exist_ok=True)
            tasks.append(asyncio.create_task(copy_file(Path(item.path), dest_folder)))
        elif item.is_dir():
            tasks.append(asyncio.create_task(read_folder(Path(item.path), output_dir)))
    await asyncio.gather(*tasks)


async def main(source_dir, output_dir):
    await read_folder(source_dir, output_dir)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Asynchronous file sorter based on file extensions."
    )
    parser.add_argument("source", type=str, help="Source directory")
    parser.add_argument("output", type=str, help="Output directory")
    args = parser.parse_args()
    source_dir = Path(args.source)
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"Source directory '{source_dir}' does not exist.")
        logging.error(f"Source directory '{source_dir}' does not exist.")
        exit(1)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    asyncio.run(main(source_dir, output_dir))
