'use client';

import { getSocialLinks } from "@/shared/data/LayoutData";
import { Link } from "@/shared/i18n/config/navigation";
import { ISocialLinksProps } from "./types/interface";
import { iconMap } from "@/shared/maps/SocialIcons";

function SocialLinks({className = '', colorIcon="text-snow"}: ISocialLinksProps) {
  const socialLinks = getSocialLinks();
  return (
    <ul className={`${className} flex justify-center gap-6 py-1.5`}>
      {socialLinks.map(({path, icon}) => {
        const Icon = iconMap[icon];

        return (
          <li key={icon}>
            <Link href={path} className={colorIcon}>
              <Icon width={24} height={24} />
            </Link>
          </li>
        )
      })}
    </ul>
  );
}

export default SocialLinks;