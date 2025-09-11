import React from "react";

export interface IHeaderBottomProps {
  setActiveHamburger: React.Dispatch<React.SetStateAction<boolean>>;
  handleOpenUserMenu: () => void;
}