import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def on_created(event):
    print(event.src_path, "has been created") 

def main () :
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created

    path = "."
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
