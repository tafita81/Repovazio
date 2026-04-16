/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingIncludes: {
    "/api/agent": [
      "./app/**/*.{js,jsx,ts,tsx,mjs,cjs,json}",
      "./lib/**/*.{js,jsx,ts,tsx,mjs,cjs,json}",
      "./netlify/**/*.{js,jsx,ts,tsx,mjs,cjs,json,toml}",
      "./public/**/*",
      "./package.json",
      "./netlify.toml",
      "./next.config.js",
      "./jsconfig.json",
      "./README.md"
    ],
    "/api/agent/context": [
      "./app/**/*.{js,jsx,ts,tsx,mjs,cjs,json}",
      "./lib/**/*.{js,jsx,ts,tsx,mjs,cjs,json}",
      "./netlify/**/*.{js,jsx,ts,tsx,mjs,cjs,json,toml}",
      "./public/**/*",
      "./package.json",
      "./netlify.toml",
      "./next.config.js"
    ]
  }
};
module.exports = nextConfig;
