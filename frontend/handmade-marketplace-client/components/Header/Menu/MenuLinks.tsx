"use client"

import { getMenuLinks } from "@/data/LayoutData";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";


function MenuLinks() {
  const t = useTranslations('header');

  const menuLinks = getMenuLinks();
  return (
    <ul className="flex-1 flex lg:flex-row flex-col xl:gap-x-9 lg:gap-x-7 gap-2.5 lg:p-0 p-3.5">
      {menuLinks?.map(({labelKey, path}) => (
        <li key={labelKey} className="menu__item">
          <Link href={path} className="text-size-link-1 py-1.5 duration-500 font-secondary">{t(`navigation.${labelKey}`)}</Link>
        </li>
      ))}
    </ul> 
  );
}

export default MenuLinks;