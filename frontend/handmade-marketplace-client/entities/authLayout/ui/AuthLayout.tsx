import { useTranslations } from "next-intl";
import { ReactNode } from "react";

interface IAuthLayout {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  classSubtitle?: string;
  classFormBlock?: string
}

function AuthLayout({children, title, subtitle, classSubtitle, classFormBlock}: IAuthLayout) {
  const t = useTranslations()
  return (
    <div className="pattern-bg lg:py-[80px] py-[40px]">
      <div className="container mx-auto px-4">
        <div className={`${classFormBlock} max-w-[685px] mx-auto bg-snow-70 shadow-custom1 lg:p-12 px-6 py-10 rounded-5xl`}>
          <div className="auth__header lg:mb-12 mb-6">
            <h2 className="text-center text-size-h2 mb-2 leading-100 text-accent-800">{title}</h2>
            <div className={`text-size-body-1 leading-130 ${classSubtitle}`}>
              {subtitle}
            </div>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
}

export default AuthLayout;