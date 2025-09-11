"use client";

import Logo from "@/widgets/Logo/Logo";
import RegionalSettings from "@/widgets/RegionalSettings/RegionalSettings";
import SearchBlock from "@/widgets/SearchBlock/SearchBlock";
import HeaderActions from "../HeaderActions/HeaderActions";
import { IHeaderBottomProps } from "./types/interfaces";

function HeaderBottom({setActiveHamburger, handleOpenUserMenu}: IHeaderBottomProps) {
  function handleActiveHamburger() {
    setActiveHamburger(prev => !prev);
  }

  return (
    <div className='menu-bottom bg-primary-900 md:py-6 py-3'>
      <div className='container mx-auto px-4'>
        <div className="menu-bottom__inner flex items-center justify-between xl:gap-6 lg:gap-4">
          <Logo />

          <div className="lg:flex xl:gap-6 lg:gap-4 items-center hidden flex-1">
            <div className="flex-1">
              <SearchBlock />
            </div>
            <RegionalSettings />
            <HeaderActions handleOpenUserMenu={handleOpenUserMenu} />
          </div>

          <div className="lg:hidden block">
            <button className="hamburger hamburger--collapse" type="button" onClick={handleActiveHamburger}>
              <span className="hamburger-box">
                <span className="hamburger-inner"></span>
              </span>
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default HeaderBottom;