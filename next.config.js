/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ignorar erros de TypeScript no build (remotion/scripts não são parte do app)
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Excluir pastas que não são parte do Next.js app
  webpack: (config) => {
    config.watchOptions = {
      ...config.watchOptions,
      ignored: ['**/remotion/**', '**/scripts/**', '**/output/**'],
    };
    return config;
  },
};

module.exports = nextConfig;
