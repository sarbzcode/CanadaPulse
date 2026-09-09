import type { Metadata } from "next";
import { Navigation } from "@/components/navigation";
import "./globals.css";
export const metadata: Metadata = {
  title: {
    default: "CanadaPulse | Canadian Economic Intelligence",
    template: "%s | CanadaPulse",
  },
  description:
    "Explore Canadian labour-market trends, provincial comparisons, and policy interest rates from official public data.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a href="#content" className="skip">
          Skip to content
        </a>
        <Navigation />
        <main className="main" id="content">
          <div className="topline">
            <span>Canada / Economic & labour market intelligence</span>
            <span className="badge">Official public data</span>
          </div>
          {children}
          <footer>
            Sources:{" "}
            <a href="https://www.statcan.gc.ca/en/developers/wds">
              Statistics Canada
            </a>{" "}
            ·{" "}
            <a href="https://www.bankofcanada.ca/valet/docs">Bank of Canada</a>.
            <br />
            CanadaPulse is an independent portfolio project and is not
            affiliated with Statistics Canada, the Bank of Canada, or the
            Government of Canada.
            <br />A scheduled batch platform ·{" "}
            <a href="https://github.com/sarbzcode/CanadaPulse">
              Source code & architecture
            </a>{" "}
            · Figures retain their stated reference periods and units.
          </footer>
        </main>
      </body>
    </html>
  );
}
