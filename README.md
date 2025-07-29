WebDAV File Watcher

/filewatch/hash_watcher.py  
/var/www/webdav/hash/ file 업로드 되면 inotifywait로 감지하여  
해당 위치에 file.sha256 생성  
/opt/filewatch/filewatch.db  
인덱스, 파일이름, 파일경로, sha256해시값, 타임스탬프 등록  
/system/hash_watcher.service  
systemd 설정 파일  
