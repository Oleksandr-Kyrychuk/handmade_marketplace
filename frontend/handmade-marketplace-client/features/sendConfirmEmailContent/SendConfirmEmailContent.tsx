import SiteContainer from "@/entities/siteContainer/SiteContainer";
import { useTranslations } from "next-intl";

function SendConfirmEmailContent() {
  const t = useTranslations();
  return (
    <SiteContainer>
      <div>
        <h1 className="text-center">{t('send_confirm_email.send_confirm_email_title')}</h1>
        <div className="text-center">{t('send_confirm_email.send_confirm_email_description')}</div>
      </div>
    </SiteContainer>
  );
}

export default SendConfirmEmailContent;