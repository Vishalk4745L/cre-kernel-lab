import { useCallback, useEffect, useState } from 'react';
import { PageHeader } from '../components/PageHeader';
import { getErrorReviews, getTrustEvents } from '../api/kernelApi';
import type { ErrorReview, TrustEvent } from '../types/api';
import { formatTimestamp } from '../utils/format';

const PAGE_SIZE = 15;

export function AuditPage() {
  const [offset, setOffset] = useState(0);

  const [trustEvents, setTrustEvents] = useState<TrustEvent[]>([]);
  const [trustTotal, setTrustTotal] = useState(0);

  const [errorReviews, setErrorReviews] = useState<ErrorReview[]>([]);
  const [errorTotal, setErrorTotal] = useState(0);

  const load = useCallback(async () => {
    try {
      const [trustRes, errorRes] = await Promise.all([
        getTrustEvents(PAGE_SIZE, offset),
        getErrorReviews(PAGE_SIZE, offset),
      ]);

      // ✅ v1.0 SAFE unwrap
      const trustData = trustRes?.data ?? {};
      const errorData = errorRes?.data ?? {};

      setTrustEvents(trustData.items ?? []);
      setTrustTotal(trustData.total ?? 0);

      setErrorReviews(errorData.items ?? []);
      setErrorTotal(errorData.total ?? 0);

    } catch (err) {
      console.error("Audit load failed:", err);
      setTrustEvents([]);
      setErrorReviews([]);
    }
  }, [offset]);

  useEffect(() => {
    void load();
  }, [load]);

  const maxTotal = Math.max(trustTotal, errorTotal);

  return (
    <section>
      <PageHeader
        title="Audit Viewer"
        description="Paginated trust events and error-review trails for explainability and governance operations."
      />

      <div className="panel">
        <div className="inline-form">
          <button
            onClick={() => setOffset((prev) => Math.max(prev - PAGE_SIZE, 0))}
            disabled={offset === 0}
          >
            Previous
          </button>

          <button
            onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
            disabled={offset + PAGE_SIZE >= maxTotal}
          >
            Next
          </button>

          <button onClick={() => void load()}>
            Refresh
          </button>
        </div>

        <p>
          Showing offset {offset}, page size {PAGE_SIZE}
        </p>
      </div>

      {/* ================= TRUST EVENTS ================= */}

      <div className="panel">
        <h3>trust_events</h3>

        {trustEvents.length === 0 ? (
          <p>No trust events found.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Agent</th>
                <th>Change</th>
                <th>Reason</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {trustEvents.map((event, idx) => (
                <tr key={`${event.agent}-${event.timestamp}-${idx}`}>
                  <td>{event.agent}</td>
                  <td>{Number(event.change).toFixed(3)}</td>
                  <td>{event.reason}</td>
                  <td>{formatTimestamp(event.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ================= ERROR REVIEWS ================= */}

      <div className="panel">
        <h3>error_reviews</h3>

        {errorReviews.length === 0 ? (
          <p>No error reviews found.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Reviewer</th>
                <th>Target</th>
                <th>Entity</th>
                <th>Type</th>
                <th>Confidence</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {errorReviews.map((review) => (
                <tr key={review.id}>
                  <td>{review.reviewer_agent}</td>
                  <td>{review.target_agent}</td>
                  <td>{review.entity}</td>
                  <td>{review.error_type}</td>
                  <td>{Number(review.confidence).toFixed(3)}</td>
                  <td>{formatTimestamp(review.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}