import { CategoryRequestDTO, CategoryResponseDTO } from "./interfaces"

interface ICategoryApi {
  getCategory: () => Promise<CategoryResponseDTO>;
  createCategory: (data: CategoryRequestDTO) => Promise<CategoryResponseDTO>
}

export { type ICategoryApi }