"""Forms for The Uncharted Route safari catalogue."""

from app.forms.safari.admin_forms import (
    SafariDestinationForm,
    SafariPropertyForm,
    SafariPropertyMediaForm,
    SafariPackageOptionForm,
    SafariItineraryDayForm,
    SafariPackageRateForm,
)

from app.forms.safari.public_forms import SafariInquiryForm

__all__ = [
    "SafariDestinationForm",
    "SafariPropertyForm",
    "SafariPropertyMediaForm",
    "SafariPackageOptionForm",
    "SafariItineraryDayForm",
    "SafariPackageRateForm",
    "SafariInquiryForm",
]