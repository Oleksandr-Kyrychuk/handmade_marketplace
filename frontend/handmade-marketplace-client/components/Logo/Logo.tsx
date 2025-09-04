import { Link } from "@/i18n/navigation";

import { LogoIcon, LogoText } from '@/assets/Logo';

function Logo() {
	return (
		<Link href="/"
			className="max-w-[276px] flex items-center"
		>
			<div className="logo-img max-w-[40px] flex-[40px] me-2">
				<LogoIcon color="#A0864D" width={40} height={56} />
			</div>
			<span className="logo-text">
				<LogoText color="#FCFCFC" width={226} height={38} />
			</span>
		</Link>
	);
}

export default Logo;