export type Category = {
  id: number;
  name: string;
  parent: number;
  category_image: string;
  category_href: string;
}

export type CategoryResponseDTO = {
  count: number;
  next: string;
  previous: string;
  results: Category[];
}

export type CategoryRequestDTO = {
  name: string;
  parent: number;
  category_image: string;
  category_href: string;
}