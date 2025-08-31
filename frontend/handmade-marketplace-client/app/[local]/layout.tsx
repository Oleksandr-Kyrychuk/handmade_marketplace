import { routing } from "@/i18n/routing";
import Provider from "@/components/Provider/Provider";
import { IRootLayoutProps } from "@/types/general-interfaces";
import { hasLocale } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { Comfortaa, Nunito } from "next/font/google";
import { notFound } from "next/navigation";

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
  style: 'italic'
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
            {children}
        </Provider>
      </body>
    </html>
  );
}

export default RootLayout;