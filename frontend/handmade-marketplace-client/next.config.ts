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

  turbopack: {
    rules: {
      '*.svg': {
        loaders: [
          {
            loader: '@svgr/webpack',
            options: {
              replaceAttrValues: {
                '^#([0-9a-fA-F]{3,6})$': 'currentColor',
                '#000': 'currentColor',
                '#000000': 'currentColor',
                '#A0864D': 'currentColor',
                '#fff': 'currentColor',
                '#ffffff': 'currentColor',
                '#FCFCFC': 'currentColor',
                '#1D2026': 'currentColor',
                '#282828': 'currentColor'
              },
              svgoConfig: {
                plugins: [
                  {
                    name: 'preset-default',
                    params: {
                      overrides: {
                        removeViewBox: false,
                      },
                    },
                  },
                  'removeDimensions',
                ],
              },
            },
          },
        ],
        as: '*.js',
      },
    },
  },
};

const withNextIntl = createNextIntlPlugin();

export default withNextIntl(nextConfig);