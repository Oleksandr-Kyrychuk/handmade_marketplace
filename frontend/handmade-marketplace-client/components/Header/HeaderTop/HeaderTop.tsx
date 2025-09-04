"use client";

import HeaderTopPC from "./HeaderTopPC";
import SocialLinks from "@/layout/SocialLinks/SocialLinks";

function HeaderTop() {
  return (
    <div className='menu-top bg-accent-700'>
			<div className="container px-4 mx-auto">
				<div className="block lg:hidden">
          <SocialLinks />
        </div>

        <div className="hidden lg:block">
          <HeaderTopPC />
        </div>
			</div>
		</div>
  );
}

export default HeaderTop;