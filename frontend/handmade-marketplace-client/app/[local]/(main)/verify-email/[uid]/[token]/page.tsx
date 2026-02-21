import VerifyEmailContent from "@/features/verifyEmail/ui/VerifyEmailContent";
import { Path } from "@/shared/enums/Path";
import { redirect } from "@/shared/i18n";


interface PageProps {
  params: Promise<{ uid: string; token: string, locale: string }>;
}

async function VerifyEmail({params}: PageProps) {
  const {uid, token, locale} = await params;

  if(!uid || !token) {
    redirect({
      href: Path.Home,
      locale: locale
    })
  }


  return (
    <VerifyEmailContent />
  );
}

export default VerifyEmail;