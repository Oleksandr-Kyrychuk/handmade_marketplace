"use client";

import { getHeaderTopLinks } from "@/shared/data/LayoutData";
import { LocalKeys } from "@/shared/enums/LocalKey";
import { Link } from "@/shared/i18n/config/navigation";
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