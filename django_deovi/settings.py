"""
Default application settings
----------------------------

These are the default settings you can override in your own project settings
right after the line which load the default app settings.

"""
DEVICE_PAGINATION = 15
"""
Device entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

DIRECTORY_PAGINATION = 48
"""
Directory entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

MEDIAFILE_PAGINATION = 60
"""
MediaFile entry per page limit for pagination, set it to ``None`` to disable
pagination.
"""

DEVICE_OCCUPANCY_SVG = "django_deovi/device/_occupancy.svg"
"""
Path to Occupancy SVG template used by tag ``show_occupancy_svg``
"""
