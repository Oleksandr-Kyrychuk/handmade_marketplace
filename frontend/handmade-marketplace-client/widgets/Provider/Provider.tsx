'use client';

import { useState } from "react";
import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { IProviderProps } from "./types/interfaces";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

function Provider({messages, locale, children}: IProviderProps) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <NextIntlClientProvider 
        locale={locale}
        messages={messages}
        timeZone='Ukraine/Kyiv'
      >
        <QueryClientProvider client={queryClient}>
          <ReactQueryDevtools initialIsOpen={false} />
          {children}
        </QueryClientProvider>
    </NextIntlClientProvider>
  )
}

export default Provider;