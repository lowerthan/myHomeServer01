#!/usr/bin/env python3
import subprocess
import hashlib
import sqlite3
import os
import time

WATCH_DIR = "/var/www/webdav/hash"
DB_PATH = "/opt/filewatch/filewatch.db"

def sha256_file(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def write_sha256_file(file_path, hash_value):
    sha_file_path = file_path + ".sha256"
    filename = os.path.basename(file_path)
    content = f"{hash_value}  {filename}\n"
    with open(sha_file_path, "w") as f:
        f.write(content)
    print(f"[+] SHA256 file created: {sha_file_path}")

def insert_hash(filename, full_path, hash_value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO file_hash_log (filename, full_path, sha256, created_at) VALUES (?, ?, ?, ?)", (
        filename, full_path, hash_value, time.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def already_in_db(filename):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM file_hash_log WHERE filename = ?", (filename,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def main():
    print(f"Watching {WATCH_DIR} ...")
    proc = subprocess.Popen(
        ["inotifywait", "-m", "-e", "close_write,move", "--format", "%f", WATCH_DIR],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    for line in proc.stdout:
        filename = line.strip()
	
        if (
            filename.startswith(".davfs.") or 
            filename.startswith("._") or
            filename.endswith(".sha256") or
            filename in [".DS_Store", "Thumbs.db"]
        ):
            continue
        if already_in_db(filename):
            continue

        full_path = os.path.join(WATCH_DIR, filename)

        if os.path.exists(full_path + ".sha256"):
            continue

        if os.path.isfile(full_path):
            try:
                hash_value = sha256_file(full_path)
                insert_hash(filename, full_path, hash_value)
                write_sha256_file(full_path, hash_value)
                print(f"[+] {filename} → SHA256: {hash_value}")
            except Exception as e:
                print(f"[!] Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
