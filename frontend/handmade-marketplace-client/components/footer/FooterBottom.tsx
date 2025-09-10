import { getFooterBottomLinks } from "@/shared/data/LayoutData";
import { Link } from "@/shared/i18n/config/navigation";
import { useTranslations } from "next-intl";

function FooterBottom() {
  const t = useTranslations();

  const footerBottomLinks = getFooterBottomLinks();
  return (
    <div className="md:mt-6 md:py-6 pt-1 pb-6 m-0">
			<div className="flex items-center lg:justify-between justify-center lg:flex-nowrap flex-wrap lg:flex-row flex-col">
				<div className="flex items-center lg:mb-0 mb-6 md:flex-row flex-col md:gap-0 gap-3">
					{footerBottomLinks.map(item => (
						<Link href={item.path} key={item.labelKey} className="text-size-link-1">
              {t(`footer.footerBottomLink.${item.labelKey}`)}
            </Link>
					))}
				</div>

				<div className="flex items-center">
					<div className="text-size-link-1">
						&copy; 2025 - Artlance 
					</div>
					<div>{t('footer.allRightsReserved')}</div>
				</div>
			</div>
		</div>
  );
}

export default FooterBottom;