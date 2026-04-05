"use client";

import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { Path } from "@/shared/enums/Path";
import { useRouter } from "@/shared/i18n";
import { Button } from "@/shared/UI";
import { useTranslations } from "next-intl";

function VerifyEmailContent() {
  const t = useTranslations();
  const router = useRouter();

  function handleButton() {
    router.replace(`${Path.Home}`)
  }

  return (

    <AuthLayout title={t('varify_email.varify_email_title_succese')} subtitle={t('varify_email.varify_email_subtitle_succese')}>
      <div className="text-center">
        <Button variant="secondary" size="lg" onClick={handleButton}>{t('buttons.back_to_home')}</Button>
      </div>
    </AuthLayout>

  );
}

export default VerifyEmailContent;