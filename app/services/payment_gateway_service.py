"""
===============================================================================
The Uncharted Route
Payment Gateway Service
===============================================================================

Provides a unified interface for processing payments.

The service is intentionally provider-agnostic so The Uncharted Route can
support multiple payment gateways without changing booking or payment logic.

Supported payment concepts include:

• Payment initiation
• Payment confirmation
• Payment verification
• Payment refunds
• Payment status lookup
• Provider selection
• Transaction references
• Payment metadata
• Gateway error handling

Potential providers:

• M-Pesa
• Paystack
• Flutterwave
• Stripe
• Bank Transfer
• Manual / Offline Payments

The service does not contain booking-specific business logic.
It provides the payment layer that other services can use.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

# =============================================================================
# Payment Result
# =============================================================================

@dataclass
class PaymentResult:
    """
    Standardized result returned by payment gateway operations.

    This prevents the rest of the application from depending directly on
    the response format of a particular payment provider.
    """

    success: bool

    status: str = "pending"

    transaction_id: Optional[str] = None

    reference: Optional[str] = None

    amount: Optional[float] = None

    currency: str = "KES"

    provider: Optional[str] = None

    message: Optional[str] = None

    checkout_url: Optional[str] = None

    provider_response: Optional[Dict[str, Any]] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


# =============================================================================
# Payment Gateway Error
# =============================================================================

class PaymentGatewayError(Exception):
    """
    Raised when a payment gateway operation fails.
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)

        self.message = message
        self.provider = provider
        self.response = response or {}

    def __str__(self):
        if self.provider:
            return (
                f"{self.provider} payment gateway error: "
                f"{self.message}"
            )

        return f"Payment gateway error: {self.message}"


# =============================================================================
# Payment Gateway Service
# =============================================================================

class PaymentGatewayService:
    """
    Unified payment gateway service.

    The service manages payment operations while allowing individual
    providers to be implemented independently.

    Example:

        payment_service = PaymentGatewayService()

        result = payment_service.initiate_payment(
            amount=25000,
            currency="KES",
            customer_email="guest@example.com",
            reference="TUR-BOOKING-001",
        )
    """

    # =========================================================================
    # Supported Providers
    # =========================================================================

    SUPPORTED_PROVIDERS = {
        "mpesa",
        "paystack",
        "flutterwave",
        "stripe",
        "bank_transfer",
        "manual",
    }

    # =========================================================================
    # Payment Statuses
    # =========================================================================

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_REFUNDED = "refunded"
    STATUS_PARTIALLY_REFUNDED = "partially_refunded"

    # =========================================================================
    # Initialization
    # =========================================================================

    def __init__(
        self,
        default_provider: str = "mpesa",
    ):
        """
        Initialize the payment service.

        Args:
            default_provider:
                Default gateway used when a provider is not explicitly
                supplied.
        """

        self.default_provider = self._validate_provider(
            default_provider
        )

    # =========================================================================
    # Provider Management
    # =========================================================================

    def _validate_provider(
        self,
        provider: str,
    ) -> str:
        """
        Validate and normalize a payment provider.
        """

        if not provider:
            raise PaymentGatewayError(
                "Payment provider is required."
            )

        provider = provider.strip().lower()

        if provider not in self.SUPPORTED_PROVIDERS:
            raise PaymentGatewayError(
                f"Unsupported payment provider: {provider}"
            )

        return provider

    def get_provider(
        self,
        provider: Optional[str] = None,
    ) -> str:
        """
        Return the requested provider or the configured default provider.
        """

        if provider:
            return self._validate_provider(provider)

        return self.default_provider

    def get_supported_providers(self):
        """
        Return all supported payment providers.
        """

        return sorted(
            self.SUPPORTED_PROVIDERS
        )

    # =========================================================================
    # Validation
    # =========================================================================

    @staticmethod
    def _validate_amount(
        amount: float,
    ) -> float:
        """
        Validate a payment amount.
        """

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise PaymentGatewayError(
                "Payment amount must be a valid number."
            )

        if amount <= 0:
            raise PaymentGatewayError(
                "Payment amount must be greater than zero."
            )

        return round(
            amount,
            2
        )

    @staticmethod
    def _validate_currency(
        currency: str,
    ) -> str:
        """
        Normalize a payment currency.
        """

        if not currency:
            return "KES"

        return currency.strip().upper()

    # =========================================================================
    # Payment Initiation
    # =========================================================================

    def initiate_payment(
        self,
        amount: float,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        reference: Optional[str] = None,
        currency: str = "KES",
        provider: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        """
        Initiate a payment.

        This method provides a common interface for all payment providers.

        Provider-specific implementations can later be connected without
        changing the booking service.
        """

        amount = self._validate_amount(amount)

        currency = self._validate_currency(
            currency
        )

        provider = self.get_provider(
            provider
        )

        metadata = metadata or {}

        if not reference:
            reference = self.generate_reference()

        # ---------------------------------------------------------------------
        # Provider Dispatch
        # ---------------------------------------------------------------------

        if provider == "mpesa":
            return self._initiate_mpesa_payment(
                amount=amount,
                currency=currency,
                customer_phone=customer_phone,
                reference=reference,
                description=description,
                metadata=metadata,
            )

        if provider == "paystack":
            return self._initiate_paystack_payment(
                amount=amount,
                currency=currency,
                customer_email=customer_email,
                reference=reference,
                callback_url=callback_url,
                metadata=metadata,
            )

        if provider == "flutterwave":
            return self._initiate_flutterwave_payment(
                amount=amount,
                currency=currency,
                customer_email=customer_email,
                customer_name=customer_name,
                reference=reference,
                callback_url=callback_url,
                metadata=metadata,
            )

        if provider == "stripe":
            return self._initiate_stripe_payment(
                amount=amount,
                currency=currency,
                customer_email=customer_email,
                reference=reference,
                callback_url=callback_url,
                metadata=metadata,
            )

        if provider == "bank_transfer":
            return self._initiate_bank_transfer(
                amount=amount,
                currency=currency,
                reference=reference,
                metadata=metadata,
            )

        if provider == "manual":
            return self._initiate_manual_payment(
                amount=amount,
                currency=currency,
                reference=reference,
                metadata=metadata,
            )

        raise PaymentGatewayError(
            f"Payment provider '{provider}' is not implemented."
        )

    # =========================================================================
    # M-Pesa
    # =========================================================================

    def _initiate_mpesa_payment(
        self,
        amount: float,
        currency: str,
        customer_phone: Optional[str],
        reference: str,
        description: Optional[str],
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Initiate an M-Pesa payment.

        The actual Daraja/STK Push implementation should be connected here.
        """

        if not customer_phone:
            raise PaymentGatewayError(
                "Customer phone number is required for M-Pesa.",
                provider="mpesa",
            )

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="mpesa",
            message=(
                "M-Pesa payment gateway implementation "
                "requires provider credentials/configuration."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Paystack
    # =========================================================================

    def _initiate_paystack_payment(
        self,
        amount: float,
        currency: str,
        customer_email: Optional[str],
        reference: str,
        callback_url: Optional[str],
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Initiate a Paystack payment.
        """

        if not customer_email:
            raise PaymentGatewayError(
                "Customer email is required for Paystack.",
                provider="paystack",
            )

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="paystack",
            message=(
                "Paystack payment gateway implementation "
                "requires provider credentials/configuration."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Flutterwave
    # =========================================================================

    def _initiate_flutterwave_payment(
        self,
        amount: float,
        currency: str,
        customer_email: Optional[str],
        customer_name: Optional[str],
        reference: str,
        callback_url: Optional[str],
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Initiate a Flutterwave payment.
        """

        if not customer_email:
            raise PaymentGatewayError(
                "Customer email is required for Flutterwave.",
                provider="flutterwave",
            )

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="flutterwave",
            message=(
                "Flutterwave payment gateway implementation "
                "requires provider credentials/configuration."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Stripe
    # =========================================================================

    def _initiate_stripe_payment(
        self,
        amount: float,
        currency: str,
        customer_email: Optional[str],
        reference: str,
        callback_url: Optional[str],
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Initiate a Stripe payment.
        """

        if not customer_email:
            raise PaymentGatewayError(
                "Customer email is required for Stripe.",
                provider="stripe",
            )

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="stripe",
            message=(
                "Stripe payment gateway implementation "
                "requires provider credentials/configuration."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Bank Transfer
    # =========================================================================

    def _initiate_bank_transfer(
        self,
        amount: float,
        currency: str,
        reference: str,
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Create a bank-transfer payment instruction.
        """

        return PaymentResult(
            success=True,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="bank_transfer",
            message=(
                "Bank transfer payment created. "
                "Awaiting payment confirmation."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Manual Payment
    # =========================================================================

    def _initiate_manual_payment(
        self,
        amount: float,
        currency: str,
        reference: str,
        metadata: Dict[str, Any],
    ) -> PaymentResult:
        """
        Create a manually verified payment.
        """

        return PaymentResult(
            success=True,
            status=self.STATUS_PENDING,
            reference=reference,
            amount=amount,
            currency=currency,
            provider="manual",
            message=(
                "Manual payment created. "
                "Awaiting administrator confirmation."
            ),
            metadata=metadata,
        )

    # =========================================================================
    # Payment Verification
    # =========================================================================

    def verify_payment(
        self,
        reference: str,
        provider: Optional[str] = None,
    ) -> PaymentResult:
        """
        Verify a payment with the selected gateway.
        """

        if not reference:
            raise PaymentGatewayError(
                "Payment reference is required."
            )

        provider = self.get_provider(
            provider
        )

        if provider == "mpesa":
            return self._verify_mpesa_payment(
                reference
            )

        if provider == "paystack":
            return self._verify_paystack_payment(
                reference
            )

        if provider == "flutterwave":
            return self._verify_flutterwave_payment(
                reference
            )

        if provider == "stripe":
            return self._verify_stripe_payment(
                reference
            )

        if provider in {
            "bank_transfer",
            "manual",
        }:
            return PaymentResult(
                success=False,
                status=self.STATUS_PENDING,
                reference=reference,
                provider=provider,
                message=(
                    "Payment requires manual confirmation."
                ),
            )

        raise PaymentGatewayError(
            f"Verification is not implemented for {provider}."
        )

    # =========================================================================
    # Provider Verification Stubs
    # =========================================================================

    def _verify_mpesa_payment(
        self,
        reference: str,
    ) -> PaymentResult:
        """
        Verify an M-Pesa transaction.
        """

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            provider="mpesa",
            message="M-Pesa verification requires gateway integration.",
        )

    def _verify_paystack_payment(
        self,
        reference: str,
    ) -> PaymentResult:
        """
        Verify a Paystack transaction.
        """

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            provider="paystack",
            message="Paystack verification requires gateway integration.",
        )

    def _verify_flutterwave_payment(
        self,
        reference: str,
    ) -> PaymentResult:
        """
        Verify a Flutterwave transaction.
        """

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            provider="flutterwave",
            message=(
                "Flutterwave verification requires "
                "gateway integration."
            ),
        )

    def _verify_stripe_payment(
        self,
        reference: str,
    ) -> PaymentResult:
        """
        Verify a Stripe transaction.
        """

        return PaymentResult(
            success=False,
            status=self.STATUS_PENDING,
            reference=reference,
            provider="stripe",
            message="Stripe verification requires gateway integration.",
        )

    # =========================================================================
    # Refunds
    # =========================================================================

    def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> PaymentResult:
        """
        Request a full or partial payment refund.
        """

        if not transaction_id:
            raise PaymentGatewayError(
                "Transaction ID is required for refunds."
            )

        if amount is not None:
            amount = self._validate_amount(
                amount
            )

        provider = self.get_provider(
            provider
        )

        if provider == "manual":
            return PaymentResult(
                success=True,
                status=self.STATUS_PENDING,
                transaction_id=transaction_id,
                amount=amount,
                provider=provider,
                message=(
                    "Refund request created and requires "
                    "manual processing."
                ),
                metadata={
                    "reason": reason
                },
            )

        raise PaymentGatewayError(
            f"Refund integration is not yet configured for {provider}.",
            provider=provider,
        )

    # =========================================================================
    # Payment Status
    # =========================================================================

    def get_payment_status(
        self,
        reference: str,
        provider: Optional[str] = None,
    ) -> PaymentResult:
        """
        Retrieve the current payment status.
        """

        return self.verify_payment(
            reference=reference,
            provider=provider,
        )

    # =========================================================================
    # Reference Generation
    # =========================================================================

    @staticmethod
    def generate_reference(
        prefix: str = "TUR",
    ) -> str:
        """
        Generate a unique payment reference.

        Example:

            TUR-20260807-142530
        """

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d-%H%M%S-%f"
        )

        return (
            f"{prefix.upper()}-{timestamp}"
        )

    # =========================================================================
    # Payment Metadata
    # =========================================================================

    @staticmethod
    def build_metadata(
        booking_id: Optional[int] = None,
        user_id: Optional[int] = None,
        experience_id: Optional[int] = None,
        **extra,
    ) -> Dict[str, Any]:
        """
        Build standardized payment metadata.
        """

        metadata = {}

        if booking_id is not None:
            metadata["booking_id"] = booking_id

        if user_id is not None:
            metadata["user_id"] = user_id

        if experience_id is not None:
            metadata["experience_id"] = experience_id

        metadata.update(
            extra
        )

        return metadata


# =============================================================================
# Service Instance
# =============================================================================
payment_gateway_service = PaymentGatewayService()

# =============================================================================
# Convenience Functions
# =============================================================================

def initiate_payment(
    amount: float,
    customer_email: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    reference: Optional[str] = None,
    currency: str = "KES",
    provider: Optional[str] = None,
    description: Optional[str] = None,
    callback_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> PaymentResult:
    """
    Convenience wrapper around PaymentGatewayService.
    """

    return payment_gateway_service.initiate_payment(
        amount=amount,
        customer_email=customer_email,
        customer_name=customer_name,
        customer_phone=customer_phone,
        reference=reference,
        currency=currency,
        provider=provider,
        description=description,
        callback_url=callback_url,
        metadata=metadata,
    )


def verify_payment(
    reference: str,
    provider: Optional[str] = None,
) -> PaymentResult:
    """
    Convenience wrapper for payment verification.
    """

    return payment_gateway_service.verify_payment(
        reference=reference,
        provider=provider,
    )


def refund_payment(
    transaction_id: str,
    amount: Optional[float] = None,
    reason: Optional[str] = None,
    provider: Optional[str] = None,
) -> PaymentResult:
    """
    Convenience wrapper for refunds.
    """

    return payment_gateway_service.refund_payment(
        transaction_id=transaction_id,
        amount=amount,
        reason=reason,
        provider=provider,
    )


def get_payment_status(
    reference: str,
    provider: Optional[str] = None,
) -> PaymentResult:
    """
    Convenience wrapper for payment status.
    """

    return payment_gateway_service.get_payment_status(
        reference=reference,
        provider=provider,
    )