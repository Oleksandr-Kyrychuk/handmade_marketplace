import { getFooterBottomLinks } from "@/shared/data/LayoutData";
import { Link } from "@/shared/i18n/config/navigation";
import { useTranslations } from "next-intl";

function FooterBottom() {
  const t = useTranslations();

  const footerBottomLinks = getFooterBottomLinks();
  return (
    <div className="md:mt-6 md:py-6 pt-1 pb-6 m-0">
			<div className="flex items-center lg:justify-between justify-center lg:flex-nowrap flex-wrap lg:flex-row flex-col">
				<div className="flex items-center lg:mb-0 mb-6 md:flex-row flex-col md:divide-x divide-white lg:gap-0 gap-y-3">
					{footerBottomLinks.map(item => (
						<Link href={item.path} key={item.labelKey} className="link-title-2 block py-1 px-2 hover:underline duration-500">
              {t(`footer.footerBottomLink.${item.labelKey}`)}
            </Link>
					))}
				</div>

				<div className="flex items-center divide-x divide-white">
					<div className="link-title-2 px-2">
						&copy; 2025 - Artlance 
					</div>
					<div className="px-2">{t('footer.allRightsReserved')}</div>
				</div>
			</div>
		</div>
  );
}

export default FooterBottom;