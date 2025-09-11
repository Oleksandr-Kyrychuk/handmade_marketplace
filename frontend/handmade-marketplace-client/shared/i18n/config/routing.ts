import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ['ua', 'en'] as const,
  defaultLocale: 'ua',
  localePrefix: 'always'
})

export type Local = (typeof routing)['locales'][number]