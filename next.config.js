/** @type {import('next').NextConfig} */
const nextConfig = {
  // Security: Disable powered-by header
  poweredByHeader: false,
  // Performance: Enable compression
  compress: true,
};
module.exports = nextConfig;
