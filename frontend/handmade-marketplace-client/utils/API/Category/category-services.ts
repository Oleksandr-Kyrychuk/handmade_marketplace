import { CategoryApi } from "./category-api";
import { ICategoryService } from "./types";
import { CategoryRequestDTO, CategoryResponseDTO } from "./types/interfaces";


class CategoryService implements ICategoryService {
  private categoryApi: CategoryApi
  
  constructor(categoryApi: CategoryApi) {
    this.categoryApi = categoryApi;
  }

  async getCategory(): Promise<CategoryResponseDTO> {
    return this.categoryApi.getCategory();
  }

  async createCategory(data: CategoryRequestDTO): Promise<CategoryResponseDTO> {
    return this.categoryApi.createCategory(data);
  }
}

export {CategoryService}