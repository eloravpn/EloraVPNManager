import importlib.util
from pathlib import Path


class VersionManager:
    """Manages application version information."""

    def __init__(self):
        self._version = "Unknown"
        self._build_date = "Unknown"
        self._load_version()

    def _load_version(self):
        """Load version information from version.py file."""
        try:
            # Get the absolute path to version.py
            base_dir = Path(__file__).parent.parent.parent
            version_file = base_dir / "version.py"

            if version_file.exists():
                # Load the version.py module
                spec = importlib.util.spec_from_file_location("version", version_file)
                version_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(version_module)

                # Get version information
                self._version = getattr(version_module, "__version__", "Unknown")
                self._build_date = getattr(version_module, "__build_date__", "Unknown")
        except Exception as e:
            print(f"Warning: Could not load version information: {e}")

    @property
    def version(self):
        """Get the application version."""
        return self._version

    @property
    def build_date(self):
        """Get the build date."""
        return self._build_date

    def get_version_info(self):
        """Get complete version information."""
        return {"version": self._version, "build_date": self._build_date}


# Create a singleton instance
version_manager = VersionManager()
