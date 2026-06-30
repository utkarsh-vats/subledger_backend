import uuid

from fastapi import status

from app.models.payment_attempt import PaymentAttemptStatus
from tests.test_invoices import _create_customer, _create_plan, _create_subscription, _create_invoice

def _create_payment_record(client, auth_header, **overrides):
    pass

# test_record_payment_unauthorized — POST /payments/record without JWT → 401.
# test_record_payment_missing_idempotency_key_returns_422 — POST with valid body but no Idempotency-Key header → 422 (route-level enforcement of mandatory header).
# test_record_successful_payment_full_amount_transitions_invoice_to_paid — issue invoice for 1200, POST success payment for 1200, assert 201, payment_attempt.status=success, payment_attempt.provider_reference starts with "FAKE-", AND fetch the invoice and assert status=paid, amount_paid=1200.00.
# test_record_successful_partial_payment_transitions_invoice_to_partially_paid — invoice for 1200, payment for 500, assert invoice status=partially_paid, amount_paid=500.00.
# test_record_failed_payment_does_not_mutate_invoice — invoice for 1200, POST failed payment with failure_reason="card_declined", assert payment row created with status=failed, fetch invoice and assert status=issued (unchanged) and amount_paid=0.00.
# test_record_payment_on_missing_invoice_returns_404 — random invoice UUID → 404.
# test_record_payment_on_paid_invoice_returns_400 — fully pay an invoice, attempt second payment, expect 400 ValidationError (status not in {ISSUED, PARTIALLY_PAID, OVERDUE}).
# test_record_payment_with_currency_mismatch_returns_400 — invoice in INR, payment in USD → 400.
# test_record_overpayment_returns_400 — invoice for 1200, payment for 1500 with status=success → 400.
# test_idempotent_replay_returns_same_attempt_no_double_charge — POST success payment with Idempotency-Key X, then POST identical body with same key, assert second response has same id as first, fetch invoice and assert amount_paid=1200.00 (NOT 2400.00 — the load-bearing test).
# test_record_failed_payment_missing_failure_reason_returns_422 — POST status=failed with no failure_reason field → 422 (Pydantic model validator).
# test_record_successful_payment_with_failure_reason_returns_422 — POST status=success with failure_reason="anything" → 422.
# test_idempotent_replay_after_partial_payment_returns_first_attempt — partial payment with key X, second request same key, assert replay returns first attempt unchanged, invoice not double-paid.
# test_two_payments_with_different_idempotency_keys_both_apply — partial payment with key X for 500, partial payment with key Y for 500, assert both rows exist, invoice amount_paid=1000.00.
# test_get_payment_attempt_by_id — happy path GET.
# test_get_unknown_payment_attempt_returns_404 — random UUID GET.
# test_list_payments_filtered_by_invoice_id — create payments across two invoices, GET ?invoice_id=... → only that invoice's.
# test_list_payments_filtered_by_status — mix success + failed, GET ?status=failed → only failed rows.











