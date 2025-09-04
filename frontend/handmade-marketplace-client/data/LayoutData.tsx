import { Path } from "@/enums/Path"
import { IGetHeaderActionLinks, INavigationLinks, ISocialLinks, IUserMenuLinks } from "@/types/general-interfaces"

export const getMenuLinks = ():INavigationLinks[] => {
  return [
    {
      path: Path.Home,
      labelKey: 'home'
    },
    {
      path: Path.Masters,
      labelKey: 'masters'
    },
    {
      path: Path.LiveAuction,
      labelKey: 'liveAuction'
    },
    {
      path: Path.SaleHits,
      labelKey: 'salehits'
    },
    {
      path: Path.SpecialPropositions,
      labelKey: 'specialPropositions'
    },
    {
      path: Path.MasterClass,
      labelKey: 'masterClass'
    },
    {
      path: Path.Blog,
      labelKey: 'blog'
    },
  ]
}

export const getHeaderTopLinks = () => {
  return [
    {
      path: Path.About,
      labelKey: 'about'
    },
    {
      path: Path.Contacts,
      labelKey: 'contacts'
    },
    {
      path: Path.Help,
      labelKey: 'help'
    },
    {
      path: Path.Registration,
      labelKey: 'registration'
    },
  ]
}

export const getSocialLinks = ():ISocialLinks[] => {
  return [
    {
      path: "/",
      icon: "facebook"
    },
    {
      path: "/",
      icon: "instagram"
    },
    {
      path: "/",
      icon: "pinterest",
    },
  ];
};

export const getHeaderActionLinks = ():IGetHeaderActionLinks[] => {
  return [
    {
      path: Path.Favorite,
      labelKey: 'favorite',
      icon: "favorite",
      count: true
    },
    {
      path: Path.Notification,
      labelKey: 'notification',
      icon: "notification",
      count: true
    },
    {
      path: Path.Basket,
      labelKey: 'basket',
      icon: "basket",
      count: true
    }
  ]
}

export const getUserMenuLinks = ():IUserMenuLinks[] => {
  return [
    {
      path: Path.GetMeaster,
      labelKey: 'getMaster',
      icon: 'getMaster'
    },
    {
      path: Path.Orders,
      labelKey: 'orders',
      icon: 'order'
    },
    {
      path: Path.Goods,
      labelKey: 'goods',
      icon: 'goods'
    },
    {
      path: Path.Favorite,
      labelKey: 'favorite',
      icon: 'favorite'
    },
    {
      path: Path.Notification,
      labelKey: 'notification',
      icon: 'notification'
    },
    {
      path: Path.Reviews,
      labelKey: 'reviews',
      icon: 'reviews'
    },
    {
      path: Path.Settings,
      labelKey: 'settings',
      icon: 'settings'
    },
    {
      path: Path.Help,
      labelKey: 'help',
      icon: 'help'
    },
    {
      path: '#',
      labelKey: 'logout',
      icon: 'logout'
    },
  ]
}