import SocialLinks from "@/layout/SocialLinks/SocialLinks";
import Logo from "../Logo/Logo";
import { Email, Phone } from "@/assets/Icons";
import SearchBlock from "../SearchBlock/SearchBlock";
import { useTranslations } from "next-intl";
import PayMethods from "./PayMethods/PayMethods";
import RegionalSettings from "../RegionalSettings/RegionalSettings";
import Button from "@/UI/Button/Button";
import { Link } from "@/i18n/navigation";
import { Path } from "@/enums/Path";
import { getFooterLinksAbout, getFooterLinksInfo, getMenuLinks } from "@/data/LayoutData";

function FooterTop() {
  const t = useTranslations();

  const colLeft = getMenuLinks();
  const colMiddle = getFooterLinksAbout();
  const colRight = getFooterLinksInfo();

  return (
		<div className="w-full flex lg:flex-nowrap flex-wrap justify-between xl:gap-[67px] lg:gap-5">

			<div className="footer__left md:max-w-[276px] max-w-none md:mb-0 mb-9">
				<div className="md:mb-8 mb-4">
					<Logo />
					<div className="md:text-size-body-3 text-size-body-4  mt-4 leading-130">
						{t('footer.textUnderLogo')}
					</div>
				</div>

				<div className="md:mb-8 mb-4">
					<div className="text-h-7 mb-4">{t('footer.socialTitle')}</div>
					<SocialLinks className="justify-start" />
				</div>

				<div className="md:mb-8">
					<div className="text-h-7 md:mb-4 mb-3">{t('footer.contactTitle')}</div>
					<div className="flex items-center mb-2">
						<span className="mr-2 block">
							<Email className="text-snow" />
						</span>
						<a href="mailto:support@artlance.com" className="text-size-link-1 underline">support@artlance.com</a>
					</div>
					<div className="flex items-center mb-2">
						<span className="mr-2 block">
							<Phone className="text-snow" />
						</span>
						<a href="tel:+38 000 000 00 00" className="text-size-link-1">+38 000 000 00 00</a>
					</div>
				</div>
			</div>

			<div className="footer__middle lg:w-auto md:w-1/2 w-full md:mb-0 mb-6">
				<div className="footer__middle-block 2xl:columns-3 columns-2 xl:gap-[65px] lg:gap-5">
					{colLeft.map(item => (
						<Link href={item.path} key={item.labelKey} className="text-size-link-1 text-snow block md:mb-6 mb-3 w-fit  md:whitespace-nowrap">
              {t(`navigation.${item.labelKey}`)}
            </Link>
					))}
					{colMiddle.map(item => (
						<Link href={item.path} key={item.labelKey} className="text-size-link-1 text-snow block md:mb-6 mb-3 w-fit md:whitespace-nowrap">
              {t(`footer.footerAboutLinks.${item.labelKey}`)}
            </Link>
					))}
					{colRight.map(item => (
						<Link href={item.path} key={item.labelKey} className="text-size-link-1 text-snow block md:mb-6 mb-3 w-fit md:whitespace-nowrap">
              {t(`footer.footerInfoLinks.${item.labelKey}`)}
            </Link>
					))}
				</div>
			</div>

			<div className="footer__right md:w-[375px] w-full">
				<div className="flex items-center md:gap-6 gap-3 mb-8">
					<RegionalSettings />
					<Button variant="secondary" className="text-size-body-2 font-bold h-[56px] flex-1" size="lg">
						{/* {isAssesToken
							? (
								<Link to={AppRoute.PROFILE}>Профіль</Link>
							) : (
								<Link to={AppRoute.LOGIN}>Вхід</Link>
							)
						} */}
						<Link href={Path.LogIn}>{t('authorization.LogIn')}</Link>
					</Button>
				</div>
				<div className="mb-8 flex-1">
					<SearchBlock />
				</div>
				<div className="mb-8">
					<div className="text-h-7 font-bold mb-4">{t('footer.payMethodsTitle')}</div>
					<PayMethods />
				</div>
			</div>
		</div>
	)
}

export default FooterTop;