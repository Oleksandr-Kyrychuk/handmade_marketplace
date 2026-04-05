import { NextRequest, NextResponse } from "next/server";
import { routing } from "./shared/i18n";
import createMiddleware from 'next-intl/middleware';
import { Path } from "./shared/enums/Path";

const intlMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  const hasConfirmSession = !!request.cookies.get('email_confirm_session');
  const url = request.nextUrl.pathname; 
  const locale = url.split('/')[1];

  if (!hasConfirmSession) {
    const confirmUrl = `/${locale}${Path.Send_confirm_email}`;
    if (url.startsWith(confirmUrl)) {
      return NextResponse.redirect(new URL(Path.Home, request.url));
    }
  }

  const response = intlMiddleware(request);
  if (response) return response;

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
  //  matcher: ['/', '/(en|uk)/:path*'],
}