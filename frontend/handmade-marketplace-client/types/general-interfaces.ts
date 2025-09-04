import { IconActive, IconName } from "@/maps/SocialIcons";
import { IconUserMenu } from "@/maps/UserMenuIcons";
import React from "react";

export interface IChildren {
  children: React.ReactNode
}

export interface INavigationLinks {
  path: string;
  labelKey: string;
}

export interface ISocialLinks {
  path: string;
  icon: IconName;
}

export interface IRootLayoutProps extends IChildren {
  params: Promise<{local: string}>
}

export interface IGetHeaderActionLinks {
  path: string;
  labelKey: string;
  icon: IconActive;
  count: boolean 
}

export interface IUserMenuLinks {
  path: string;
  labelKey: string;
  icon: IconUserMenu;
}