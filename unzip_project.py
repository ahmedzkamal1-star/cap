import zipfile
import os

def unzip_file():
    zip_file = 'update_v29.zip'
    target_dir = '/home/Mr7Riko/mysite'
    
    if not os.path.exists(zip_file):
        print(f"❌ Error: {zip_file} not found in this folder. Make sure you uploaded it here.")
        return

    print(f"📦 Unzipping {zip_file}...")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    
    print(f"✅ Extracted all files to {target_dir}")
    print("Next: visit the Web tab and Reload your site.")

if __name__ == "__main__":
    unzip_file()
