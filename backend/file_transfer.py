
import base64
import re
from urllib.parse import urlparse


MAX_FILE_BYTES = 5 * 1024 * 1024

ALLOWED_DOWNLOAD_HOSTS = {
    "www.w3.org",
    "raw.githubusercontent.com",
}


def build_transfer_source(task):

    operation = getattr(task, "operation", "")

    task_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(task.task_id)
    )

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    if operation == "File Upload":

        filename = getattr(
            task,
            "uploaded_filename",
            ""
        )

        file_bytes = getattr(
            task,
            "uploaded_bytes",
            None
        )

        upload_location = getattr(
            task,
            "upload_location",
            "~/sysnexa_transfers/uploads/"
        ).strip()

        if file_bytes is None:
            raise ValueError("No uploaded file found.")

        if len(file_bytes) > MAX_FILE_BYTES:
            raise ValueError("Maximum file size is 5 MB.")

        if not upload_location:
            raise ValueError("Upload destination is required.")

        filename = filename.replace("\\", "/").split("/")[-1]

        if filename in ("", ".", ".."):
            raise ValueError("Invalid filename.")

        encoded_data = base64.b64encode(
            file_bytes
        ).decode("ascii")

        return f'''
import base64
import json
import time
from pathlib import Path


# Resolve the selected Ubuntu destination

home = Path.home().resolve()

directory = Path(
    {upload_location!r}
).expanduser().resolve()


# Validate destination

if not directory.is_relative_to(home):

    raise ValueError(
        "Destination must be inside the Ubuntu home directory."
    )


# Automatically create the selected directory

directory.mkdir(
    parents=True,
    exist_ok=True
)


# Final file destination

destination = directory / {filename!r}


# Prevent overwriting an existing file

if destination.exists() or destination.is_symlink():

    raise FileExistsError(
        "A file with this name already exists."
    )


# Start actual file transfer

start_time = time.perf_counter()

data = base64.b64decode({encoded_data!r})

with destination.open("xb") as file:

    file.write(data)


# Calculate actual runtime measurements

duration = time.perf_counter() - start_time

size = destination.stat().st_size

speed = size / duration if duration > 0 else None


# Return transfer results

print(json.dumps({{

    "operation": "File Upload",

    "filename": destination.name,

    "destination": str(destination),

    "transferred_bytes": size,

    "transfer_time_seconds": duration,

    "transfer_speed_bytes_per_second": speed

}}))
'''

    # =====================================================
    # FILE DOWNLOAD
    # =====================================================

    elif operation == "File Download":

        url = getattr(
            task,
            "download_url",
            ""
        ).strip()

        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or parsed.hostname not in ALLOWED_DOWNLOAD_HOSTS
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port not in (None, 443)
        ):

            raise ValueError(
                "Use an HTTPS URL from an approved download host."
            )

        filename = parsed.path.split("/")[-1]

        filename = re.sub(
            r"[^a-zA-Z0-9._-]",
            "_",
            filename
        )

        if filename in ("", ".", ".."):

            filename = "downloaded_file"

        return f'''
import json
import time
import urllib.request
from pathlib import Path


class NoRedirect(urllib.request.HTTPRedirectHandler):

    def redirect_request(
        self, req, fp, code, msg, headers, newurl
    ):

        return None


directory = (
    Path.home()
    / "sysnexa_transfers"
    / "downloads"
    / {task_id!r}
)

directory.mkdir(
    parents=True,
    exist_ok=True
)

destination = directory / {filename!r}

temporary = directory / ({filename!r} + ".part")

maximum_bytes = {MAX_FILE_BYTES}

start_time = time.perf_counter()

size = 0

opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({{}}),
    NoRedirect()
)

try:

    with opener.open({url!r}, timeout=15) as response:

        with temporary.open("wb") as file:

            while True:

                chunk = response.read(65536)

                if not chunk:

                    break

                size += len(chunk)

                if size > maximum_bytes:

                    raise ValueError(
                        "Download exceeds the 5 MB limit."
                    )

                file.write(chunk)

    temporary.replace(destination)

except Exception:

    temporary.unlink(missing_ok=True)

    raise


duration = time.perf_counter() - start_time

speed = size / duration if duration > 0 else None


print(json.dumps({{

    "operation": "File Download",

    "filename": destination.name,

    "destination": str(destination),

    "transferred_bytes": size,

    "transfer_time_seconds": duration,

    "transfer_speed_bytes_per_second": speed

}}))
'''

    else:

        raise ValueError(
            "Unsupported file transfer operation."
        )
