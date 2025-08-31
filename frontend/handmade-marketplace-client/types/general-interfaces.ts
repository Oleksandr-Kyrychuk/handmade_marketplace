import React from "react";

export interface IChildren {
  children: React.ReactNode
}

export interface IRootLayoutProps extends IChildren {
  params: Promise<{local: string}>
}