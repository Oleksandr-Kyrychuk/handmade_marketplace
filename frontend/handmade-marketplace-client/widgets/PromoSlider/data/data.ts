import { Path } from "@/shared/enums/Path";
import { IPromoSliderData } from "../type/interface";

export const promoSliderData: IPromoSliderData[] = [
  {
    titleKey: 'promo-slider.block1.title',
    descriptionKeys: [
      'promo-slider.block1.description.p1',
      'promo-slider.block1.description.p2'
    ],
    buttons: [
      {
        labelKey: 'buttons.registration',
        href: Path.Registration,
        variant: 'default'
      },
      {
        labelKey: 'buttons.auction',
        href: Path.LiveAuction,
        variant: 'secondary'
      },
    ],
    stats: [
      { value: "5k+", labelKey: "promo-slider.block1.stats.products", style: "one" },
      { value: "500", labelKey: "promo-slider.block1.stats.auctions", style: "two" },
      { value: "5k+", labelKey: "promo-slider.block1.stats.craftsmen", style: "three" },
    ]
  },
  {
    titleKey: 'promo-slider.block2.title',
    descriptionKeys: [
      'promo-slider.block2.description.p1',
      'promo-slider.block2.description.p2'
    ],
    buttons: [
      {
        labelKey: 'buttons.about',
        href: Path.About,
        variant: 'default'
      },
      {
        labelKey: 'buttons.help',
        href: Path.Help,
        variant: 'secondary'
      },
    ],
  }
]