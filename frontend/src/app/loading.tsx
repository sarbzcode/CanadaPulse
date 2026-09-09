export default function Loading() {
  return (
    <div role="status" aria-live="polite">
      <p className="loading-text">Loading CanadaPulse…</p>
      <div className="skeleton" />
      <div className="skeleton" />
    </div>
  );
}
