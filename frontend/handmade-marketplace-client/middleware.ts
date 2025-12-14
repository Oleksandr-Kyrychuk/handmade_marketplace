import { NextRequest, NextResponse } from "next/server";
import { routing } from "./shared/i18n";
import createMiddleware from 'next-intl/middleware';

const intlMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {

  const response = intlMiddleware(request);
  if (response) return response;

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
  //  matcher: ['/', '/(en|uk)/:path*'],
}