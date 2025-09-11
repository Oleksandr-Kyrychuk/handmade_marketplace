import '@/shared/styles/globals.css'

import { hasLocale } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { Comfortaa, Nunito } from "next/font/google";
import { notFound } from "next/navigation";

import { IRootLayoutProps } from '@/shared/types/general-interfaces';
import { routing } from '@/shared/i18n';
import Provider from '@/widgets/Provider/Provider';
import Header from '@/widgets/Header/Header';
import Footer from '@/widgets/Footer/Footer';

const comfortaa = Comfortaa({
  variable: "--font-comfortaa",
  subsets: ["latin"],
  display: 'swap',
  weight: 'variable',
  style: 'normal'
});

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin"],
  display: 'swap',
  weight: 'variable',
  style: 'normal'
});


async function RootLayout({children, params}: IRootLayoutProps) {
  const locale = (await params).local;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  const messages = await getMessages();

  setRequestLocale(locale);

  return (
    <html lang={locale} className={`${comfortaa.variable} ${nunito.variable}`}>
      <body>
        <Provider   
          messages={messages}
          locale={locale}>
            <div className="flex flex-col min-h-screen">
              <Header />
              <main className="main flex-1">
                {children}
              </main>
              <Footer />
            </div>
        </Provider>
      </body>
    </html>
  );
}

export default RootLayout;