"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className="notice error" role="alert">
      <h1>We could not load this view.</h1>
      <p>Please try again. Your data has not been changed.</p>
      <button className="button" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
