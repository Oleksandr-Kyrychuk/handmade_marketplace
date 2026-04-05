

import SiteContainer from "@/entities/siteContainer/SiteContainer";
import { ReactNode } from "react";

interface IAuthLayout {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  classSubtitle?: string;
  classFormBlock?: string
}

function AuthLayout({children, title, subtitle, classSubtitle, classFormBlock}: IAuthLayout) {
  return (
    <SiteContainer>
      <div className={`${classFormBlock} max-w-[685px] mx-auto bg-snow-70 shadow-custom1 lg:p-12 px-6 py-10 rounded-5xl`}>
        <div className="auth__header lg:mb-12 mb-6">
          <h2 className="text-center text-size-h2 mb-2 leading-100 text-accent-800">{title}</h2>
          <div className={`text-size-body-1 leading-130 text-center ${classSubtitle}`}>
            {subtitle}
          </div>
        </div>

        {children}
      </div>
    </SiteContainer>
  );
}

export default AuthLayout;