import {GetMaster, Profile, Order, Box, Favorite, Notification, Reviews, Settings, Help, LogOut} from '@/assets/UserMenu'

export const userMenuIcons = {
  getMaster: GetMaster,
  profile: Profile,
  order: Order, 
  goods: Box,
  favorite: Favorite,
  notification: Notification,
  reviews: Reviews,
  settings: Settings,
  help: Help,
  logout: LogOut
}

export type IconUserMenu = keyof typeof userMenuIcons;