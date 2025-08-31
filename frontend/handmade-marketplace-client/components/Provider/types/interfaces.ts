import { IChildren } from "@/types/general-interfaces";
import { AbstractIntlMessages } from "next-intl";

export interface IProviderProps extends IChildren {
  locale: string;
  messages: AbstractIntlMessages;
}