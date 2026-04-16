export const metadata = {
  title: "Next Netlify App",
  description: "Next.js app deployed on Netlify",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
