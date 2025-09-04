"use client";

import { getHeaderTopLinks } from "@/data/LayoutData";
import { LocalKeys } from "@/enums/LocalKey";
import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";

function HeaderTopPC() {
  const topLinks = getHeaderTopLinks();
  const t = useTranslations(LocalKeys.HeaderTop);

  return (
    <ul className='flex lg:flex-row flex-col lg:items-center justify-center lg:gap-x-14 gap-y-3'>
      {topLinks.map(({path, labelKey}) => (
        <li key={labelKey}>
          <Link aria-current='page' href={path} className='text-size-link-1 lg:text-white leading-100 text-primary-900 py-1 px-2 font-secondary block'>
            {t(`${labelKey}`)}
          </Link>
        </li>
      ))}
    </ul>
  )
}

export default HeaderTopPC;