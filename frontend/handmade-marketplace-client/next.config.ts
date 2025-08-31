import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const nextConfig: NextConfig = {
   // compress: false, //!FIXME: should probably turn on when we'll use nginx
  devIndicators: {
    buildActivityPosition: 'top-right',
  },
  experimental: {
    // cssChunking: 'loose', //!FIXME: should probably turn on
    optimizePackageImports: ['package-name'],
    typedRoutes: true,
    scrollRestoration: true,
  },
  poweredByHeader: false, //!turned off x-powered-by header
  output: 'standalone',
};

const withNextIntl = createNextIntlPlugin();

export default withNextIntl(nextConfig);
