"""
File system watcher for configuration files.

This module provides functionality for monitoring configuration files for changes
and triggering automatic reloads.
"""

from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Callable, Dict, Optional, Set

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class ConfigFileEventHandler(FileSystemEventHandler):
    """
    Event handler for configuration file changes.

    Attributes:
        callback: Function to call when a file changes
        watched_files: Set of files being watched
    """

    def __init__(
        self, callback: Callable[[str], None], watched_files: Set[str]
    ) -> None:
        """
        Initialize the event handler.

        Args:
            callback: Function to call when a file changes
            watched_files: Set of files to watch
        """
        self.callback = callback
        self.watched_files = watched_files
        self._last_events: Dict[str, datetime] = {}

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Handle file modification events.

        Args:
            event: File system event
        """
        if not event.is_directory:
            file_path = str(Path(event.src_path).resolve())
            if file_path in self.watched_files:
                # Check if we've already handled this event recently
                now = datetime.now()
                if file_path in self._last_events:
                    # Skip if less than 1 second since last event
                    if (now - self._last_events[file_path]).total_seconds() < 1:
                        return

                self._last_events[file_path] = now
                self.callback(file_path)


class FileSystemWatcher:
    """
    Watches configuration files for changes and triggers reloads.

    Attributes:
        watched_files: Set of files being watched
        observer: File system observer
        event_handler: Configuration file event handler
        stop_event: Event to signal the watcher to stop
    """

    def __init__(self) -> None:
        """Initialize the file system watcher."""
        self.watched_files: Set[str] = set()
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[ConfigFileEventHandler] = None
        self.stop_event = Event()

    def start(self, callback: Callable[[str], None]) -> None:
        """
        Start watching for file changes.

        Args:
            callback: Function to call when a file changes
        """
        if self.observer:
            return

        self.event_handler = ConfigFileEventHandler(callback, self.watched_files)
        self.observer = Observer()

        # Start watching each unique directory
        watched_dirs = {str(Path(f).parent) for f in self.watched_files}
        for directory in watched_dirs:
            self.observer.schedule(self.event_handler, directory, recursive=False)

        self.observer.start()

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self.observer:
            self.stop_event.set()
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.event_handler = None
            self.stop_event.clear()

    def watch_file(self, file_path: str) -> None:
        """
        Add a file to watch.

        Args:
            file_path: Path to the file to watch
        """
        resolved_path = str(Path(file_path).resolve())
        self.watched_files.add(resolved_path)

        # If observer is running, update it
        if self.observer and self.event_handler:
            directory = str(Path(resolved_path).parent)
            self.observer.schedule(self.event_handler, directory, recursive=False)

    def unwatch_file(self, file_path: str) -> None:
        """
        Remove a file from watching.

        Args:
            file_path: Path to the file to stop watching
        """
        resolved_path = str(Path(file_path).resolve())
        self.watched_files.discard(resolved_path)

        # If no more files in a directory, unschedule it
        if self.observer and self.event_handler:
            directory = str(Path(resolved_path).parent)
            if not any(str(Path(f).parent) == directory for f in self.watched_files):
                for watch in self.observer.watches.copy():
                    if watch.path == directory:
                        self.observer.unschedule(watch)
