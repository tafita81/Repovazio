export const metadata = {
  title: "psicologia.doc — Cérebro Autônomo",
  description: "@psicologiadoc · Sistema autônomo 24/7 (Next.js / Netlify)",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
