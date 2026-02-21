import React, { ReactNode } from 'react';

function SiteContainer({children}: {children: ReactNode}) {
  return (
    <div className="pattern-bg lg:py-[80px] py-[40px]">
      <div className="container mx-auto px-4">
        {children}
      </div>
    </div>
  );
}

export default SiteContainer;