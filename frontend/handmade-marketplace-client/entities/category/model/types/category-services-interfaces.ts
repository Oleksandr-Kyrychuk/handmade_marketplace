import { CategoryRequestDTO, CategoryResponseDTO } from "./interfaces";

interface ICategoryService {
  getCategory: () => Promise<CategoryResponseDTO>;
  createCategory: (data: CategoryRequestDTO) => Promise<CategoryResponseDTO>
}

export { type ICategoryService }