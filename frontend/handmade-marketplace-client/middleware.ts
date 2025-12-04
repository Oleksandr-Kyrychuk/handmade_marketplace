import { NextRequest, NextResponse } from "next/server";
import { Path } from "./shared/enums/Path";
import createMiddleware from 'next-intl/middleware';
import { routing } from "./shared/i18n";

const intlMiddleware = createMiddleware(routing);

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const locale = pathname.split("/")[1]

  if(pathname.includes(Path.Home)) {
    const token = request.nextUrl.searchParams.get('token');

    if(!token) {
      return NextResponse.redirect(new URL(`/${locale}`, request.url))
    }
  }

  const response = intlMiddleware(request);
  if (response) return response;

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
}