import { Path } from "@/shared/enums/Path";
import { IButtonVariant } from "@/shared/UI/Button/types/interfaces";

export interface PromoSliderButton {
  labelKey: string;
  href: Path;
  variant: IButtonVariant
}

export interface PromoStats {
  value: string;
  labelKey: string;
  style: string;
}

export interface IPromoSliderData  {
  titleKey: string;
  descriptionKeys: string[];
  buttons?: PromoSliderButton[];
  stats?: PromoStats[]
}