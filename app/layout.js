export const metadata = {
  metadataBase: new URL("https://psicologia.doc"),
  title: {
    default: "psicologia.doc — Cérebro Autônomo 24/7",
    template: "%s | psicologia.doc",
  },
  description:
    "Sistema autônomo de psicologia que funciona 24/7. Insights, ferramentas e conteúdo para transformar sua mente. Seguido por +50k pessoas no Instagram e TikTok.",
  keywords: ["psicologia", "saúde mental", "autoconhecimento", "cérebro", "mente"],
  authors: [{ name: "psicologia.doc", url: "https://psicologia.doc" }],
  creator: "psicologia.doc",
  publisher: "psicologia.doc",

  // Open Graph — otimizado para compartilhamento viral
  openGraph: {
    type: "website",
    locale: "pt_BR",
    url: "https://psicologia.doc",
    siteName: "psicologia.doc",
    title: "psicologia.doc — Cérebro Autônomo 24/7",
    description:
      "Sistema autônomo de psicologia que funciona 24/7. Transforme sua mente com ciência.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "psicologia.doc — Cérebro Autônomo",
      },
    ],
  },

  // Twitter/X Card
  twitter: {
    card: "summary_large_image",
    title: "psicologia.doc — Cérebro Autônomo 24/7",
    description: "Sistema autônomo de psicologia 24/7.",
    images: ["/og-image.png"],
    creator: "@psicologiadoc",
  },

  // Robots
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },

  // Verificação das plataformas
  verification: {
    // google: "seu-codigo-aqui",
    // yandex: "seu-codigo-aqui",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <head>
        {/* Pinterest Rich Pins */}
        <meta name="pinterest-rich-pin" content="true" />
        {/* WhatsApp Preview */}
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        {/* Preconnect para performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://supabase.co" />
      </head>
      <body>{children}</body>
    </html>
  );
}
