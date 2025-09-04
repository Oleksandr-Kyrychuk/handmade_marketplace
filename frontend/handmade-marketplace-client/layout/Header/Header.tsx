"use client";

import { useState } from "react";

import HeaderBottom from "@/components/Header/HeaderBottom/HeaderBottom";
import HeaderTop from "@/components/Header/HeaderTop/HeaderTop";
import Menu from "@/components/Header/Menu/Menu";

function Header() {
  const [activeHamburger, setActiveHamburger] = useState(false);
  const [openMenuCatalog, setOpenMenuCatalog] = useState(false);
	const [userMenu, setUserMenu] = useState(false);

  function handleCloseMobileMenu() {
    setActiveHamburger(false)
		setOpenMenuCatalog(false)
		setUserMenu(false)
  }

  function handleOpenUserMenu() {
		setUserMenu(prev => !prev)
	}

  function handleOpenMenuCatalog() {
    setOpenMenuCatalog(prev => !prev)
  }

  return (
    <header className="header relative z-10">
      <HeaderTop />
      <HeaderBottom setActiveHamburger={setActiveHamburger} handleOpenUserMenu={handleOpenUserMenu} />

      <div className="lg:block hidden">
        <Menu openMenuCatalog={openMenuCatalog} handleOpenMenuCatalog={handleOpenMenuCatalog} />
      </div>
    </header>
  );
}

export default Header;