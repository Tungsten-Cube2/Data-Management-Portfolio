from pathlib import Path
import shutil
import hashlib

specific_organizing = True
source = Path("messy files")
destination = Path("clean files")

for file in source.iterdir():
    if file.is_file():
        extension = file.suffix.lower()

        if extension in [".pdf", ".txt", ".md", ".docx"]:
            folder = destination / "Documents & Text Files"
            if specific_organizing == True:
                if extension == ".pdf":
                    folder = folder / "PDFs"
                elif extension == ".txt":
                    folder = folder / "Text Files"
                elif extension == ".md":
                    folder = folder / "Markdown Files"
                elif extension == ".docx":
                    folder = folder / "DOCX Files"
        elif extension in [".csv", ".xlsx"]:
            folder = destination / "Data"
            if specific_organizing == True:
                if extension == ".csv":
                    folder = folder / "CSV Files"
                elif extension == ".xlsx":
                    folder = folder / "Excel Files"
        elif extension in [".jpg", ".png"]:
            folder = destination / "Images"
            if specific_organizing == True:
                if extension == ".png":
                    folder = folder / "PNGs"
                elif extension == ".jpg":
                    folder = folder / "JPGs"
        elif extension == ".py":
            folder = destination / "Python Scripts"
        else:
            folder = destination / "Other"

        folder.mkdir(parents=True, exist_ok=True)

        shutil.move(str(file), str(folder / file.name))