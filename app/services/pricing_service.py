"""
===============================================================================
The Uncharted Route
Pricing Service
===============================================================================

Centralized pricing logic for experiences, booking, and optional add-ons.

The pricing service is responsible for:

• Calculating experiences prices
• Applying pricing tiers
• Calculating guest totals
• Calculating add-on costs
• Applying discounts
• Applying percentage-based adjustments
• Calculating taxes
• Calculating booking totals
• Formatting prices
• Providing pricing breakdowns

The service intentionally keeps pricing calculations separate from models
and routes so pricing rules can be changed without rewriting the booking
system.

Expected pricing levels:

• Explorer
• Signature
• Luxury
• Expedition
• Bespoke
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


# =============================================================================
# Pricing Error
# =============================================================================

class PricingError(Exception):
    """
    Raised when a pricing operation cannot be completed.
    """

    pass


# =============================================================================
# Pricing Line
# =============================================================================

@dataclass
class PricingLine:
    """
    Represents one item in a pricing breakdown.
    """

    name: str

    quantity: float

    unit_price: float

    total: float

    currency: str = "KES"

    pricing_type: str = "Per Person"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =============================================================================
# Pricing Result
# =============================================================================

@dataclass
class PricingResult:
    """
    Standardized pricing calculation result.
    """

    subtotal: float = 0.0

    discount: float = 0.0

    tax: float = 0.0

    fees: float = 0.0

    total: float = 0.0

    currency: str = "KES"

    lines: List[PricingLine] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def grand_total(self) -> float:
        """
        Return the final payable amount.
        """

        return round(
            self.total,
            2
        )


# =============================================================================
# Pricing Service
# =============================================================================

class PricingService:
    """
    Centralized pricing service for The Uncharted Route.
    """

    # =========================================================================
    # Supported Experience Levels
    # =========================================================================

    EXPERIENCE_LEVELS = {
        "explorer",
        "signature",
        "luxury",
        "expedition",
        "bespoke",
    }

    # =========================================================================
    # Default Currency
    # =========================================================================

    DEFAULT_CURRENCY = "KES"

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        default_currency: str = DEFAULT_CURRENCY,
    ):
        self.default_currency = (
            default_currency.upper()
            if default_currency
            else self.DEFAULT_CURRENCY
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def validate_amount(
        amount: float,
        allow_zero: bool = True,
    ) -> float:
        """
        Validate and normalize a monetary amount.
        """

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise PricingError(
                "Amount must be a valid number."
            )

        if not allow_zero and amount <= 0:
            raise PricingError(
                "Amount must be greater than zero."
            )

        if allow_zero and amount < 0:
            raise PricingError(
                "Amount cannot be negative."
            )

        return round(
            amount,
            2
        )

    @staticmethod
    def validate_quantity(
        quantity: float,
    ) -> float:
        """
        Validate a quantity.
        """

        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            raise PricingError(
                "Quantity must be a valid number."
            )

        if quantity <= 0:
            raise PricingError(
                "Quantity must be greater than zero."
            )

        return quantity

    @staticmethod
    def normalize_currency(
        currency: Optional[str],
        default: str = "KES",
    ) -> str:
        """
        Normalize a currency code.
        """

        if not currency:
            return default.upper()

        return currency.strip().upper()

    # =========================================================================
    # Experience Level
    # =========================================================================

    def normalize_experience_level(
        self,
        level: Optional[str],
    ) -> str:
        """
        Normalize an experiences pricing level.
        """

        if not level:
            return "explorer"

        normalized = level.strip().lower()

        if normalized not in self.EXPERIENCE_LEVELS:
            raise PricingError(
                f"Unsupported experiences level: {level}"
            )

        return normalized

    # =========================================================================
    # Experience Price
    # =========================================================================

    def get_experience_price(
        self,
        experience,
        guests: int = 1,
        level: Optional[str] = None,
    ) -> float:
        """
        Calculate the base experiences price.

        The method supports several common pricing structures used by
        experiences models.

        It first attempts to use a pricing tier when available, then falls
        back to the experiences's base price.
        """

        if not experience:
            raise PricingError(
                "Experience is required."
            )

        guests = int(
            self.validate_quantity(
                guests
            )
        )

        selected_level = (
            level
            or getattr(
                experience,
                "experience_level",
                None
            )
            or getattr(
                experience,
                "level",
                None
            )
        )

        if selected_level:
            selected_level = (
                self.normalize_experience_level(
                    selected_level
                )
            )

        # ---------------------------------------------------------------------
        # Try pricing tiers
        # ---------------------------------------------------------------------

        pricing_tiers = getattr(
            experience,
            "pricing_tiers",
            None
        )

        if pricing_tiers:

            if hasattr(
                pricing_tiers,
                "all"
            ):
                pricing_tiers = pricing_tiers.all()

            for tier in pricing_tiers:

                tier_level = (
                    getattr(
                        tier,
                        "level",
                        None
                    )
                    or getattr(
                        tier,
                        "pricing_level",
                        None
                    )
                )

                if (
                    selected_level
                    and tier_level
                    and tier_level.strip().lower()
                    != selected_level
                ):
                    continue

                price = (
                    getattr(
                        tier,
                        "price",
                        None
                    )
                )

                if price is not None:
                    pricing_type = (
                        getattr(
                            tier,
                            "pricing_type",
                            "Per Person"
                        )
                    )

                    return self.calculate_pricing_type(
                        price=price,
                        quantity=guests,
                        pricing_type=pricing_type,
                    )

        # ---------------------------------------------------------------------
        # Fall back to base experiences price
        # ---------------------------------------------------------------------

        price = getattr(
            experience,
            "price",
            None
        )

        if price is None:
            price = getattr(
                experience,
                "base_price",
                None
            )

        if price is None:
            raise PricingError(
                "Experience does not contain a usable price."
            )

        pricing_type = (
            getattr(
                experience,
                "pricing_type",
                "Per Person"
            )
        )

        return self.calculate_pricing_type(
            price=price,
            quantity=guests,
            pricing_type=pricing_type,
        )

    # =========================================================================
    # Pricing Type Calculation
    # =========================================================================

    def calculate_pricing_type(
        self,
        price: float,
        quantity: float = 1,
        pricing_type: str = "Per Person",
    ) -> float:
        """
        Calculate a price according to its pricing type.

        Supported types:

        • Per Person
        • Per Booking
        • Per Vehicle
        • Per Group
        """

        price = self.validate_amount(
            price
        )

        quantity = self.validate_quantity(
            quantity
        )

        normalized_type = (
            pricing_type.strip().lower()
            if pricing_type
            else "per person"
        )

        if normalized_type in {
            "per booking",
            "per group",
        }:
            return price

        if normalized_type in {
            "per person",
            "per guest",
            "per traveler",
            "per traveller",
            "per vehicle",
            "per unit",
        }:
            return round(
                price * quantity,
                2
            )

        raise PricingError(
            f"Unsupported pricing type: {pricing_type}"
        )

    # =========================================================================
    # Add-on Pricing
    # =========================================================================

    def calculate_addon_price(
        self,
        addon,
        quantity: float = 1,
        guests: Optional[int] = None,
    ) -> float:
        """
        Calculate the total cost of an experiences add-on.
        """

        if not addon:
            raise PricingError(
                "Add-on is required."
            )

        price = getattr(
            addon,
            "price",
            None
        )

        if price is None:
            raise PricingError(
                "Add-on does not contain a price."
            )

        pricing_type = getattr(
            addon,
            "pricing_type",
            "Per Person"
        )

        if pricing_type.lower() in {
            "per person",
            "per guest",
        } and guests is not None:
            quantity = guests

        return self.calculate_pricing_type(
            price=price,
            quantity=quantity,
            pricing_type=pricing_type,
        )

    # =========================================================================
    # Multiple Add-ons
    # =========================================================================

    def calculate_addons(
        self,
        addons: Iterable,
        guests: int = 1,
    ) -> List[PricingLine]:
        """
        Calculate pricing lines for multiple add-ons.
        """

        lines = []

        for addon in addons:

            if not getattr(
                addon,
                "active",
                True
            ):
                continue

            if not getattr(
                addon,
                "available_online",
                True
            ):
                continue

            total = self.calculate_addon_price(
                addon=addon,
                guests=guests,
            )

            price = self.validate_amount(
                getattr(
                    addon,
                    "price",
                    0
                )
            )

            pricing_type = getattr(
                addon,
                "pricing_type",
                "Per Person"
            )

            quantity = (
                guests
                if pricing_type.lower()
                in {
                    "per person",
                    "per guest",
                }
                else 1
            )

            lines.append(
                PricingLine(
                    name=getattr(
                        addon,
                        "name",
                        "Add-on"
                    ),
                    quantity=quantity,
                    unit_price=price,
                    total=total,
                    currency=self.normalize_currency(
                        getattr(
                            addon,
                            "currency",
                            self.default_currency
                        ),
                        self.default_currency,
                    ),
                    pricing_type=pricing_type,
                    metadata={
                        "addon_id": getattr(
                            addon,
                            "id",
                            None
                        )
                    },
                )
            )

        return lines

    # =========================================================================
    # Percentage Calculations
    # =========================================================================

    @staticmethod
    def calculate_percentage(
        amount: float,
        percentage: float,
    ) -> float:
        """
        Calculate a percentage of an amount.
        """

        amount = PricingService.validate_amount(
            amount
        )

        try:
            percentage = float(
                percentage
            )
        except (TypeError, ValueError):
            raise PricingError(
                "Percentage must be a valid number."
            )

        if percentage < 0:
            raise PricingError(
                "Percentage cannot be negative."
            )

        return round(
            amount * (
                percentage / 100
            ),
            2
        )

    # =========================================================================
    # Discount
    # =========================================================================

    def calculate_discount(
        self,
        amount: float,
        percentage: Optional[float] = None,
        fixed_amount: Optional[float] = None,
    ) -> float:
        """
        Calculate a discount.

        Either percentage or fixed_amount may be supplied.
        """

        amount = self.validate_amount(
            amount
        )

        if (
            percentage is not None
            and fixed_amount is not None
        ):
            raise PricingError(
                "Use either percentage or fixed amount, not both."
            )

        if percentage is not None:

            discount = self.calculate_percentage(
                amount,
                percentage,
            )

        elif fixed_amount is not None:

            discount = self.validate_amount(
                fixed_amount
            )

        else:
            return 0.0

        return min(
            discount,
            amount
        )

    # =========================================================================
    # Tax
    # =========================================================================

    def calculate_tax(
        self,
        amount: float,
        tax_percentage: float = 0,
    ) -> float:
        """
        Calculate tax on an amount.
        """

        return self.calculate_percentage(
            amount,
            tax_percentage,
        )

    # =========================================================================
    # Fees
    # =========================================================================

    def calculate_fee(
        self,
        amount: float,
        fee_percentage: Optional[float] = None,
        fixed_fee: Optional[float] = None,
    ) -> float:
        """
        Calculate a booking or payment fee.
        """

        amount = self.validate_amount(
            amount
        )

        if (
            fee_percentage is not None
            and fixed_fee is not None
        ):
            raise PricingError(
                "Use either fee percentage or fixed fee, not both."
            )

        if fee_percentage is not None:
            return self.calculate_percentage(
                amount,
                fee_percentage,
            )

        if fixed_fee is not None:
            return self.validate_amount(
                fixed_fee
            )

        return 0.0

    # =========================================================================
    # Booking Pricing
    # =========================================================================

    def calculate_booking_total(
        self,
        experience,
        guests: int = 1,
        addons: Optional[Iterable] = None,
        discount_percentage: Optional[float] = None,
        discount_amount: Optional[float] = None,
        tax_percentage: float = 0,
        fee_percentage: Optional[float] = None,
        fixed_fee: Optional[float] = None,
        level: Optional[str] = None,
        currency: Optional[str] = None,
    ) -> PricingResult:
        """
        Calculate the complete price for an experiences booking.
        """

        guests = int(
            self.validate_quantity(
                guests
            )
        )

        currency = self.normalize_currency(
            currency,
            self.default_currency,
        )

        # ---------------------------------------------------------------------
        # Experience
        # ---------------------------------------------------------------------

        experience_total = self.get_experience_price(
            experience=experience,
            guests=guests,
            level=level,
        )

        experience_price = (
            experience_total / guests
        )

        lines = [
            PricingLine(
                name=getattr(
                    experience,
                    "title",
                    "Experience"
                ),
                quantity=guests,
                unit_price=round(
                    experience_price,
                    2
                ),
                total=experience_total,
                currency=currency,
                pricing_type="Per Person",
                metadata={
                    "experience_id": getattr(
                        experience,
                        "id",
                        None
                    )
                },
            )
        ]

        # ---------------------------------------------------------------------
        # Add-ons
        # ---------------------------------------------------------------------

        if addons:

            addon_lines = self.calculate_addons(
                addons=addons,
                guests=guests,
            )

            lines.extend(
                addon_lines
            )

        subtotal = round(
            sum(
                line.total
                for line in lines
            ),
            2
        )

        # ---------------------------------------------------------------------
        # Discount
        # ---------------------------------------------------------------------

        discount = self.calculate_discount(
            amount=subtotal,
            percentage=discount_percentage,
            fixed_amount=discount_amount,
        )

        taxable_amount = round(
            subtotal - discount,
            2
        )

        # ---------------------------------------------------------------------
        # Tax
        # ---------------------------------------------------------------------

        tax = self.calculate_tax(
            amount=taxable_amount,
            tax_percentage=tax_percentage,
        )

        # ---------------------------------------------------------------------
        # Fees
        # ---------------------------------------------------------------------

        fees = self.calculate_fee(
            amount=taxable_amount,
            fee_percentage=fee_percentage,
            fixed_fee=fixed_fee,
        )

        # ---------------------------------------------------------------------
        # Final Total
        # ---------------------------------------------------------------------

        total = round(
            taxable_amount
            + tax
            + fees,
            2
        )

        return PricingResult(
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            fees=fees,
            total=total,
            currency=currency,
            lines=lines,
            metadata={
                "guest_count": guests,
                "experience_id": getattr(
                    experience,
                    "id",
                    None
                ),
                "experience_level": level,
            },
        )

    # =========================================================================
    # Price Formatting
    # =========================================================================

    def format_price(
        self,
        amount: float,
        currency: Optional[str] = None,
        decimals: int = 0,
    ) -> str:
        """
        Format a monetary amount for display.
        """

        amount = self.validate_amount(
            amount
        )

        currency = self.normalize_currency(
            currency,
            self.default_currency,
        )

        if decimals < 0:
            decimals = 0

        return (
            f"{currency} "
            f"{amount:,.{decimals}f}"
        )

    # =========================================================================
    # Price Per Person
    # =========================================================================

    @staticmethod
    def price_per_person(
        total: float,
        guests: int,
    ) -> float:
        """
        Calculate the average price per guest.
        """

        total = PricingService.validate_amount(
            total
        )

        guests = int(
            PricingService.validate_quantity(
                guests
            )
        )

        return round(
            total / guests,
            2
        )

    # =========================================================================
    # Deposit
    # =========================================================================

    def calculate_deposit(
        self,
        total: float,
        percentage: float,
    ) -> float:
        """
        Calculate a required booking deposit.
        """

        total = self.validate_amount(
            total
        )

        deposit = self.calculate_percentage(
            total,
            percentage,
        )

        return min(
            deposit,
            total
        )

    # =========================================================================
    # Balance
    # =========================================================================

    def calculate_balance(
        self,
        total: float,
        amount_paid: float,
    ) -> float:
        """
        Calculate the remaining booking balance.
        """

        total = self.validate_amount(
            total
        )

        amount_paid = self.validate_amount(
            amount_paid
        )

        return max(
            round(
                total - amount_paid,
                2
            ),
            0.0
        )


# =============================================================================
# Service Instance
# =============================================================================

pricing_service = PricingService()


# =============================================================================
# Convenience Functions
# =============================================================================

def calculate_booking_total(
    experience,
    guests: int = 1,
    addons: Optional[Iterable] = None,
    discount_percentage: Optional[float] = None,
    discount_amount: Optional[float] = None,
    tax_percentage: float = 0,
    fee_percentage: Optional[float] = None,
    fixed_fee: Optional[float] = None,
    level: Optional[str] = None,
    currency: Optional[str] = None,
) -> PricingResult:
    """
    Convenience wrapper for booking pricing.
    """

    return pricing_service.calculate_booking_total(
        experience=experience,
        guests=guests,
        addons=addons,
        discount_percentage=discount_percentage,
        discount_amount=discount_amount,
        tax_percentage=tax_percentage,
        fee_percentage=fee_percentage,
        fixed_fee=fixed_fee,
        level=level,
        currency=currency,
    )


def calculate_discount(
    amount: float,
    percentage: Optional[float] = None,
    fixed_amount: Optional[float] = None,
) -> float:
    """
    Convenience wrapper for discount calculations.
    """

    return pricing_service.calculate_discount(
        amount=amount,
        percentage=percentage,
        fixed_amount=fixed_amount,
    )


def calculate_tax(
    amount: float,
    tax_percentage: float = 0,
) -> float:
    """
    Convenience wrapper for tax calculations.
    """

    return pricing_service.calculate_tax(
        amount=amount,
        tax_percentage=tax_percentage,
    )


def format_price(
    amount: float,
    currency: Optional[str] = None,
    decimals: int = 0,
) -> str:
    """
    Convenience wrapper for price formatting.
    """

    return pricing_service.format_price(
        amount=amount,
        currency=currency,
        decimals=decimals,
    )