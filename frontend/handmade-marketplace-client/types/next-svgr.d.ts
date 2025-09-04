declare module 'next-svgr' {
  import type { NextConfig } from 'next';
  const withSvgr: (nextConfig: NextConfig) => NextConfig;
  export default withSvgr;
}