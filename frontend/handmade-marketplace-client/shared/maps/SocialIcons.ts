import FacebookIcon from "@/assets/SocialIcons/FacebookIcon.svg";
import InstagramIcon from "@/assets/SocialIcons/InstaIcon.svg";
import PinterestIcon from "@/assets/SocialIcons/PinterestIcon.svg";

import FavoriteIcon from "@/assets/HeaderActions/FavoriteIcon.svg"
import NotificationIcon from "@/assets/HeaderActions/NotificationIcon.svg"
import BasketIcon from "@/assets/HeaderActions/BasketIcon.svg"

export const iconMap = {
  facebook: FacebookIcon,
  instagram: InstagramIcon,
  pinterest: PinterestIcon,
} as const;

export type IconName = keyof typeof iconMap;

export const iconActive = {
  favorite: FavoriteIcon,
  notification: NotificationIcon,
  basket: BasketIcon
}

export type IconActive = keyof typeof iconActive;